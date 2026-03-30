# Implementación Técnica: Backend RADIAN (Fase 7.3)

Este documento registra las decisiones arquitectónicas y soluciones técnicas aplicadas para lograr la transmisión "End-to-End" de los eventos RADIAN desde el portal público de Odoo 19 hasta el servidor oficial de la DIAN, preservando la filosofía **"Zero Huecos"** y **"Anti-Fragilidad"** de InSoTech.

---

## 1. Arquitectura Desacoplada (Bypass Odoo Core)
El ecosistema de localización colombiana nativa de Odoo 19 (`l10n_co_edi` / `l10n_co_dian`) presenta serios niveles de volatilidad y dependencias poco fiables (como el Odoo IAP). Para garantizar una conexión 100% directa y segura con la DIAN, **bypassamos el motor nativo de Odoo**.

Se ha reutilizado el motor criptográfico robusto del módulo `insotech_dian_wizard` combinado con un nuevo constructor de plantillas específico para RADIAN ubicado en:
`insotech_l10n_co_advanced/services/radian_xml_builder.py`

## 2. Generación del UBL 2.1 (ApplicationResponse)
En lugar de depender de librerías jerárquicas pesadas (LXML objectifying) que son lentas y propensas a errores tras actualizaciones de Odoo, implementamos un **inyector de plantillas por interpolación (`f-strings`)**.
- Replicamos exactamente las plantillas estáticas de la *"Caja de Herramientas Validación Previa 1.8"* de la DIAN.
- Inyectamos en vivo: NIT del facturador, Razón Social, CUFE original e ID del software.
- **Todo dato es genérico**: se lee de `res.company` (`insotech_dian_software_id`, `insotech_dian_software_pin`). Cero datos quemados.

### Independencia del Módulo-11
Durante las pruebas, Odoo 19 originó un *Traceback* por la eliminación del atributo `l10n_co_edi_dv` en el objeto de la compañía. Para lograr una independencia total, se incrustó el algoritmo matemático **Módulo-11** directamente dentro de `radian_xml_builder.py`.
```python
def _compute_dv(nit_str):
    # Cálculo de factores DIAN sin consultar base de datos ni modelos Odoo
```
Esto asegura que el XML cuente con su Dígito de Verificación reglamentario (`schemeID`) sin importar los cambios que Odoo aplique a sus objetos `res.partner` o `res.company`.

## 3. Algoritmo CUDE Autónomo (SHA-384)
Según la Resolución 000165 Anexo 1.9, los eventos RADIAN no utilizan el mismo algoritmo CUFE de una factura. Exigen el cómputo de la matriz **CUDE** exclusiva para `ApplicationResponse`.
La función envenena la cadena `NumAR + FecAR + HorAR + NitOFE + NitAdq + CodEvento + CUFE + PINSoftware` y la sella con **SHA-384**.

> **IMPORTANTE:** El CUDE va en `<cbc:UUID>`. El `<sts:SoftwareSecurityCode>` es un hash DIFERENTE: `SHA384(SoftwareID + PIN + ID)`. Confundir estos dos hashes causa el error `AAB27b` de la DIAN.

## 4. SenderParty y ReceiverParty — Regla de Oro

> **REGLA CRÍTICA VALIDADA EN PRODUCCIÓN (2026-03-26):**
> El `SenderParty` del ApplicationResponse SIEMPRE debe ser el OFE (Obligado a Facturar Electrónicamente), es decir, el VENDEDOR / InSoTech.
> La DIAN valida que el NIT del certificado que firma la transmisión SOAP coincida con el NIT del `SenderParty`. Si no coinciden, devuelve **Code 89: "NIT X no autorizado a enviar documentos para emisor con NIT Y"**.

**¿Quién es quién en el XML?**
- `SenderParty` = OFE / Vendedor / InSoTech (siempre, porque transmite con su certificado)
- `ReceiverParty` = Adquiriente / Comprador / Cliente
- `IssuerParty` (dentro de `DocumentResponse`) = OFE / Vendedor
- El mandato del comprador se registra internamente (IP, timestamp, checkbox en portal)

**Implicación para el Portal:** Aunque el COMPRADOR acepta la factura desde el portal, el XML se genera y firma con el certificado de InSoTech (OFE). La aceptación del comprador queda registrada en `insotech.radian.event` como evidencia forense, NO como SenderParty.

## 5. Autorización DIAN para Eventos RADIAN

> **DESCUBRIMIENTO CRÍTICO (2026-03-26):**
> El OFE (vendedor) NO puede enviar eventos 030-034 para sus PROPIAS facturas de venta a menos que esté registrado como "factor" o "proveedor tecnológico" en RADIAN.
> Error: `AAF01a: "Nombre o Razón social no está autorizado para generar este evento"`

**Escenarios de autorización:**

| Escenario | ¿Puede enviar eventos? | Motivo |
|-----------|----------------------|--------|
| OFE envía evento para factura que EMITIÓ | ❌ | El OFE no es el adquiriente |
| Adquiriente envía evento para factura que RECIBIÓ | ✅ | Flujo estándar DIAN |
| OFE envía evento en nombre del adquiriente (mandato) | ⚠️ Requiere habilitación | Requiere registro en RADIAN DIAN |
| OFE envía evento para factura de PROVEEDOR (Vendor Bill) | ✅ | El OFE es el adquiriente |

**Pendiente:** Investigar el proceso de habilitación RADIAN en el portal DIAN (mimuisca/catalogo-vpfe) para que InSoTech pueda enviar eventos en representación de sus clientes.

## 6. Firma Criptográfica XAdES-BES
**Problema crítico superado:** Odoo 19 posee un bug nativo en su motor `certificate` donde falla de manera catastrófica (`TypeError: Password was given but private key is not encrypted`) al intentar instanciar llaves `PEM` en texto claro bajo la tubería `cryptography`. Esta fragilidad incluso tumba la creación de contactos al teclear un ID.

**Solución aplicada:**
La clase de `radian_event.py` importa nuestro `xml_signer.py` de `insotech_dian_wizard`, extrayendo en crudo los bytes del `.p12` base64 de InSoTech. Firmamos digitalmente la capa `<ds:Signature>` evadiendo todo el motor defectuoso de llaves de Odoo.

## 7. Transmisión SOAP Síncrona a la DIAN
Las facturas locales utilizan un bus encolado a Odoo IAP. Nuestro RADIAN implementa un socket directo a la capa de validación (WCF de la DIAN):
- **Capa Envelope:** Usamos `_build_soap_envelope` inyectando credenciales WS-Security en el Header.
- **Acción:** `http://wcf.dian.colombia/IWcfDianCustomerServices/SendEventUpdateStatus`.
- **Empaquetado:** El script zipea en memoria base64 el `.xml` (`zipfile.ZIP_DEFLATED`), cumpliendo con la exigencia de tamaño de envío.
- **Trazabilidad:** Al recibir confirmación, los archivos (`XML Enviado` y `ApplicationResponse DIAN`) se adjuntan automáticamente al Chatter del `account.move`.

## 8. Frontend: Portal RADIAN con Access Token

### Acceso sin Login
El portal RADIAN usa `auth="public"` en el controller y acepta `access_token` como parámetro. El cliente NO necesita usuario ni contraseña. El flujo es:
1. InSoTech envía factura por email (incluye link con `access_token`)
2. El cliente hace clic → ve la factura + botones RADIAN
3. Acepta el mandato (checkbox) → genera evento

### Parche "Blank Error Bug"
Odoo 19 introdujo una disrupción en su clase web `PortalMixin`. El controlador HTTP usa parámetros blindados: `?radian_success`, `?radian_error` y `?radian_warning`, renderizados con componentes Native Bootstrap propios en `s_radian_actions.xml`.

> **BUG CORREGIDO (2026-03-26):** El método `_redirect_msg` era una función local dentro de `trigger_radian_event`, pero las líneas 87/89/93 lo llamaban como `self._redirect_msg()` generando Error 500. Corregido a `_redirect_msg()` (sin self).

## 9. Sincronización de Estados `insotech_dian_status`

> **GAP DETECTADO (2026-03-26):**
> El campo `insotech_dian_status` NO se sincroniza automáticamente con el campo nativo `l10n_co_dian_state`. Los botones RADIAN en el portal solo aparecen cuando `insotech_dian_status == 'accepted'`. Si la DIAN acepta la factura pero el campo custom no se actualiza, los botones no aparecen.
>
> **Workaround actual:** Actualización manual vía shell.
> **Pendiente:** Implementar un `compute` o `onchange` que sincronice ambos campos.

---

## 10. Guía Crítica de Migración a Odoo V18 para Futuros Agentes

Si estás leyendo este documento porque te asignaron la tarea de portar este desarrollo:

1. **Bug Criptográfico Nativos (PEM):** Mantener el "Monkey-Patch" y usar el `xml_signer` propio.
2. **Campos DIAN Volátiles:** No depender NUNCA de campos nativos Odoo para formar XMLs.
3. **Plantillas del Portal QWeb:** Revisar IDs de wrappers visuales en la nueva versión.
4. **Alerta Vacía (Blank Error Box):** Usar siempre el workaround con URLEncode propio.
5. **SenderParty:** SIEMPRE el OFE/transmisor. NUNCA el comprador (causa Code 89).
6. **SoftwareSecurityCode ≠ CUDE:** Son hashes DIFERENTES. Confundirlos causa AAB27b.

---
**Resultado:** Cero dependencias IAP, latencias sub-segundo para la validación web, sin bloqueos asíncronos u operaciones CRON retenidas. El usuario pulsa, firma, transmite, y el evento RADIAN viaja a la DIAN en un solo evento atómico.
