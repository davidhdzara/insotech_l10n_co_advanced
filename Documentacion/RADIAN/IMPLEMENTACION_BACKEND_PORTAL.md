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

## 4. Firma Criptográfica XAdES-BES
**Problema crítico superado:** Odoo 19 posee un bug nativo en su motor `certificate` donde falla de manera catastrófica (`TypeError: Password was given but private key is not encrypted`) al intentar instanciar llaves `PEM` en texto claro bajo la tubería `cryptography`. Esta fragilidad incluso tumba la creación de contactos al teclear un ID.

**Solución aplicada:**
La clase de `radian_event.py` importa nuestro `xml_signer.py` de `insotech_dian_wizard`, extrayendo en crudo los bytes del `.p12` base64 de InSoTech. Firmamos digitalmente la capa `<ds:Signature>` evadiendo todo el motor defectuoso de llaves de Odoo.

## 5. Transmisión SOAP Síncrona a la DIAN
Las facturas locales utilizan un bus encolado a Odoo IAP. Nuestro RADIAN implementa un socket directo a la capa de validación (WCF de la DIAN):
- **Capa Envelope:** Usamos `_build_soap_envelope` inyectando credenciales WS-Security en el Header.
- **Acción:** Descubrimos que el WSDL oficial de la DIAN consume la directiva `http://wcf.dian.colombia/IWcfDianCustomerServices/SendEventUpdateStatus`.
- **Empaquetado:** El script zipea en memoria base64 el `.xml` (`zipfile.ZIP_DEFLATED`), cumpliendo con la exigencia de tamaño de envío.
- **Trazabilidad:** Al recibir confirmación, los archivos (`XML Enviado` y `ApplicationResponse DIAN`) se adjuntan automáticamente al Chatter del `account.move`.

## 6. Frontend: Parche Web "Blank Error Bug"
Odoo 19 introdujo una disrupción en su clase web `PortalMixin`. Cuando los middlewares validaban negativamente reglas de negocio (e.g. No marcar la casilla legal) usando variables QWeb como `?error=...`, Odoo renderizaba el recuadro `<div class="alert alert-danger">` completamente vacío y con las clases CSS rotas.

**Estrategia "Own Namespace":**
- El controlador HTTP intercepta los retornos usando un url-encoder propio y parámetros blindados: `?radian_success`, `?radian_error` y `?radian_warning`.
- Inyectamos en vivo desde DOM la recepción de estas variables en Native Bootstrap Components dentro de `s_radian_actions.xml`, desactivando cualquier heredabilidad en conflicto del layout base de Odoo.

---
**Resultado:** Cero dependencias IAP, latencias sub-segundo para la validación web, sin bloqueos asíncronos u operaciones CRON retenidas. El usuario pulsa, firma, transmite, y el Título Valor nace en la nube DIAN en un solo evento atómico.

---

## 7. Guía Crítica de Migración a Odoo V18 para Futuros Agentes

Si estás leyendo este documento (`IMPLEMENTACION_BACKEND_PORTAL.md`) porque te asignaron la tarea de portar este desarrollo de la versión `19.0` a la `18.0`, ten en cuenta los siguientes **GAPs técnicos**:

1. **Bug Criptográfico Nativos (PEM):** Odoo 19 introdujo un `TypeError` severo en el modelo `certificate` de su core porque intenta inyectar passwords (`pwd`) a llaves `PEM` en texto plano (unencrypted), tumbando la interfaz (`res.partner.onchange`) y el XML Signer propio de Odoo. **En Odoo 18, es posible que ese bug no exista o se comporte distinto.** Aún así, debes **mantener el "Monkey-Patch"** (`_l10n_co_dian_onchange_identification_type` en `res_partner.py`) y usar el `xml_signer` propio desarrollado aquí para mantener el sistema Aislado y Anti-frágil.
2. **Campos DIAN Volátiles:** Odoo 18 acostumbra usar nombres distintos para los campos de tributación. El dígito de verificación en Odoo 19 se perdió/cambió, obligándonos a programar el algoritmo Módulo-11 manual (`_compute_dv`) en nuestro `radian_xml_builder.py`. **Mantenlo así en V18.** No dependas NUNCA de los campos nativos de Odoo (ej. `l10n_co_edi_dv`, `l10n_co_verification_code`) para formar XMLs ante la DIAN, porque cambian la base de datos de versión a versión.
3. **Plantillas del Portal QWeb (`account.portal_invoice_page`):** La inyección de nuestro panel lateral RADIAN se hizo atacando los XPaths `//div[@id='invoice_communication']` y `//p[@name='payment_communication']`. Revisa en Odoo 18 si el core template cambió los ID's de esos wrappers visuales o no inyectará la barra lateral de botones.
4. **Alerta Vacía (Blank Error Box):** No intentes regresar a usar `error=` en el `get_portal_url()` nativo del controlador. Odoo 18 y Odoo 19 rompen silenciosamente la plantilla mostrando "Cajas Rojas" vacías dependiendo de si pasas strings, listas o diccionarios. Usa **siempre** nuestro workaround seguro con URLEncode en el controlador inyectando variables HTML estáticas `?radian_error=` y renderizándolas con tu propio `<div t-if="radian_error">`.
