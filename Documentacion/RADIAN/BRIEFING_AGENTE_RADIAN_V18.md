# Briefing Técnico para Agente: Implementar RADIAN en Odoo 18

> **Propósito:** Este documento prepara a un agente de IA para implementar el sistema RADIAN (eventos de factura electrónica colombiana) en Odoo 18, basándose en la implementación exitosa en Odoo 19 de InSoTech.
>
> **Instrucción al agente:** Lee este documento COMPLETO antes de escribir una sola línea de código. Luego, PIDE al usuario que ejecute los comandos de inspección en su instancia Odoo 18 para verificar qué modelos y campos existen. NUNCA asumas.

---

## 1. ¿Qué es RADIAN?

RADIAN es el sistema de la DIAN (Colombia) para el registro y circulación de facturas electrónicas como **títulos valor**. Involucra 6 eventos que emisores y receptores intercambian:

| Código | Evento | Quién lo emite | Notas |
|--------|--------|---------------|-------|
| **030** | Acuse de Recibo | Receptor | Confirma que recibió la factura |
| **031** | Rechazo de la FE | Receptor | La factura tiene errores |
| **032** | Recibo del Bien/Servicio | Receptor | **⚠️ INICIA el reloj de 3 días** |
| **033** | Aceptación Expresa | Receptor | Acepta voluntariamente |
| **034** | Reclamo de la FE | Receptor | Con código de reclamo (01-04) |
| **035** | Aceptación Tácita | Automático (CRON) | Se genera si pasan 3 días hábiles sin 033/031/034 |

### ⚠️ Error CRÍTICO Común
- **034 NO es Aceptación Tácita** — es Reclamo
- **035 es Aceptación Tácita** — muchas fuentes omiten este código
- **El reloj empieza en 032, NO en 030** — error sutil pero crítico

### Marco Normativo
- **Resolución 000165/2023** de la DIAN
- **Anexo Técnico 1.9** — Estructura XML ApplicationResponse

---

## 2. Lo que se implementó en V19 (tu referencia)

### Sprint 1: Eventos RADIAN + Irrevocabilidad
| Componente | Archivo | Descripción |
|-----------|---------|-------------|
| Modelo `insotech.radian.event` | `radian_event.py` | Modelo propio (NO herencia de account.move) con One2many implícito |
| Modelo `insotech.custom.holiday` | `custom_holiday.py` | Calendario festivos colombianos algorítmico |
| CRON Aceptación Tácita | `cron_radian_tacit.xml` | Diario: busca facturas con 032 sin 033/031/034 tras 3 días hábiles |
| Bloqueo NC/ND | `account_move.py` | Override de `_post()` — bloquea NC si hay evento 033/034 |
| Grupo override | `security.xml` | `group_radian_override` para permitir NC con alerta |

### Sprint 2: Contingencia Tipo 04
| Componente | Archivo | Descripción |
|-----------|---------|-------------|
| Extensión `l10n_co_dian.document` | `l10n_co_dian_document.py` | 5 campos de contingencia + métodos CRON |
| CRON Retry | `cron_contingency.xml` | Cada 5 min: 3 reintentos con sleep(20s) |
| CRON Recovery | `cron_contingency.xml` | Cada 30 min: retransmisión post-contingencia |
| Extensión operation_type | `account_move.py` | `selection_add` con códigos 03/04 |
| Config multi-tenant | `res_company.py` | 4 campos configurables por empresa |

---

## 3. Diferencias clave V18 vs V19

### 🚨 Antes de codificar, el agente DEBE verificar estos puntos:

| Área | V19 | V18 (probable) | Acción requerida |
|------|-----|-----------------|-----------------|
| **SQL Constraints** | `_nombre = models.Constraint('SQL', 'msg')` | `_sql_constraints = [('nombre', 'SQL', 'msg')]` | Usar patrón V18 |
| **ir.cron** | Sin `numbercall`, sin `state`, sin `priority` | **Tiene** `numbercall`, `state`, `priority` | Incluir estos campos |
| **Grupos seguridad** | `privilege_id` reemplaza `category_id` | **Usa** `category_id` | Usar `category_id` |
| **model_id en CRON XML** | `search="[('model', '=', '...')]"` funciona | Puede funcionar `ref="modulo.model_nombre"` | Verificar con usuario |
| **l10n_co_dian** | Existe como módulo Enterprise | **Verificar si existe** — V18 puede tener otro nombre | ⚠️ PREGUNTAR |
| **mail.thread** | Funciona igual | Funciona igual | Sin cambios |
| **selection_add** | Funciona | Funciona | Sin cambios |

### 🔴 PASO OBLIGATORIO: Inspeccionar modelos en V18

Antes de implementar NADA, pide al usuario que ejecute en `odoo-bin shell`:

```python
# 1. ¿Existe el modelo DIAN?
try:
    Doc = env['l10n_co_dian.document']
    print("EXISTE:", Doc._name)
    for name, field in sorted(Doc._fields.items()):
        print(name, field.type)
except KeyError:
    print("NO EXISTE l10n_co_dian.document")

# 2. ¿Qué módulos colombianos hay?
import odoo.addons
for mod in sorted(dir(odoo.addons)):
    if 'l10n_co' in mod or 'dian' in mod.lower():
        print(mod)

# 3. ¿Tiene account.move operation_type?
Move = env['account.move']
if 'l10n_co_edi_operation_type' in Move._fields:
    print("operation_type EXISTE")
    print(Move._fields['l10n_co_edi_operation_type'].selection)
else:
    print("operation_type NO EXISTE")

# 4. ¿Cómo se envía a DIAN?
try:
    import inspect
    print(inspect.getsource(Doc._send_to_dian))
except:
    print("No tiene _send_to_dian")
```

**Los resultados de esto determinan TODA la arquitectura.** No procedas sin ellos.

---

## 4. Arquitectura recomendada

### Modelo propio vs herencia
- **Modelo propio `insotech.radian.event`** para eventos ← SIEMPRE
- **Herencia `_inherit`** de `l10n_co_dian.document` para contingencia ← SOLO si el modelo existe
- **Herencia `_inherit`** de `account.move` para bloqueo NC/ND ← SIEMPRE
- **NUNCA agregar 10+ campos a `account.move`** directamente

### Calendario festivos
- Implementar algoritmo puro Python (Ley 51 de 1983)
- No depender de APIs externas
- Los festivos colombianos se calculan con reglas fijas + Semana Santa (algoritmo de Gauss)

### Seguridad
```csv
# ir.model.access.csv — OBLIGATORIO para modelos propios
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_insotech_radian_event_user,insotech.radian.event user,model_insotech_radian_event,account.group_account_invoice,1,1,1,0
access_insotech_radian_event_manager,insotech.radian.event manager,model_insotech_radian_event,account.group_account_manager,1,1,1,1
```

---

## 5. CRON: Formato V18

```xml
<!-- V18: incluir numbercall, state, priority -->
<record id="ir_cron_radian_tacit" model="ir.cron">
    <field name="name">InSoTech: RADIAN Aceptación Tácita</field>
    <field name="model_id" ref="model_insotech_radian_event"/>
    <field name="state">code</field>
    <field name="code">model._cron_tacit_acceptance()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="priority">5</field>
    <field name="active" eval="True"/>
</record>
```

---

## 6. Contingencia Tipo 04 — Protocolo DIAN

### Flujo de detección
```
Intento 1 (síncrono, al confirmar) → falla (state='invoice_sending_failed')
    ↓ CRON (no bloquea UI)
Intento 2 (sleep 20s) → falla
    ↓
Intento 3 (sleep 20s) → falla
    ↓
Intento 4 (sleep 20s) → falla
    ↓
CONTINGENCIA TIPO 04 ACTIVADA
    ↓
operation_type = '04'
CRON recovery cada 30 min
Plazo máximo: 48 horas
```

### Verificaciones de idempotencia
Antes de implementar retry, **verificar con el usuario** que:
1. `_send_to_dian()` o equivalente es stateless (se puede re-invocar)
2. El CUFE se genera ANTES del envío (no dentro de `_send_bill_sync`)
3. Existe detección de "documento ya procesado"

```python
# Pedir al usuario que ejecute:
import inspect
print(inspect.getsource(Doc._send_to_dian))
print(inspect.getsource(Doc._send_bill_sync))
```

---

## 7. Irrevocabilidad — Bloqueo de NC/ND

### Regla de negocio
Una factura con evento 033 (Aceptación Expresa) o 034 (Reclamo) → **NO se puede revertir** con NC/ND.

### Implementación
```python
def _post(self, soft=True):
    # PRIMERO verificar irrevocabilidad
    self._insotech_check_radian_irrevocability()
    # LUEGO llamar super()
    posted = super()._post(soft=soft)
    return posted
```

**⚠️ Interceptar ANTES de `super()._post()`** — si bloqueas después, el consecutivo DIAN ya se consumió.

### Patrón defensivo para modelos opcionales
```python
RadianEvent = self.env.get('insotech.radian.event')
if RadianEvent is None:
    return  # Módulo no instalado, no bloquear
```

---

## 8. Comunicación SOAP con DIAN — Envío de Eventos RADIAN

Los eventos RADIAN se envían a la DIAN como documentos XML firmados via **SOAP web services**. Esta es la capa que transforma un registro en BD en una comunicación válida con la DIAN.

### Endpoints DIAN

| Ambiente | URL |
|----------|-----|
| Habilitación (pruebas) | `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc` |
| Producción | `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc` |

### Métodos SOAP relevantes

| Método | Uso | Tipo |
|--------|-----|------|
| `SendBillSync` | Enviar 1 factura/evento y obtener respuesta inmediata | Síncrono |
| `SendTestSetAsync` | Enviar batch de hasta 50 documentos (habilitación) | Asíncrono |
| `GetStatusZip` | Consultar estado de un batch asíncrono | Consulta |
| `SendEventUpdateStatus` | **Enviar eventos RADIAN (030-035)** | Síncrono |
| `GetStatus` | Consultar estado de un documento específico | Consulta |

> ⚠️ **IMPORTANTE:** `SendTestSetAsync` **NO reporta errores de validación XML**. Si un documento tiene campos incorrectos, se queda "procesando" indefinidamente. SIEMPRE pre-validar con `SendBillSync` primero.

### Flujo de envío de un evento RADIAN
```
1. Obtener CUFE de la factura original
2. Computar CUDE del evento (SHA-384)
3. Construir XML ApplicationResponse UBL 2.1
4. Firmar con XAdES-EPES (certificado .p12)
5. Comprimir en ZIP
6. Enviar via SendEventUpdateStatus
7. Parsear respuesta SOAP
```

---

## 9. Estructura XML ApplicationResponse (Eventos RADIAN)

Todos los eventos (030-035) comparten la misma estructura base:

```xml
<ApplicationResponse xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2">
  <ext:UBLExtensions>
    <!-- DianExtensions: InvoiceSource, SoftwareProvider, SoftwareSecurityCode, QRCode -->
    <!-- Firma XAdES-EPES (segunda UBLExtension) -->
  </ext:UBLExtensions>
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>         <!-- ⚠️ "UBL 2.1", NO "2.1" -->
  <cbc:CustomizationID>1</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1: ApplicationResponse de la Factura Electrónica de Venta</cbc:ProfileID>
  <cbc:ProfileExecutionID>2</cbc:ProfileExecutionID>     <!-- 1=Producción, 2=Pruebas -->
  <cbc:ID>ACR0021</cbc:ID>                               <!-- Consecutivo del evento -->
  <cbc:UUID schemeID="2" schemeName="CUDE-SHA384">...</cbc:UUID>
  <cbc:IssueDate>2020-12-12</cbc:IssueDate>
  <cbc:IssueTime>18:30:37-05:00</cbc:IssueTime>
  <cbc:Note>...cadena CUDE...</cbc:Note>
  <cac:SenderParty>...</cac:SenderParty>                  <!-- Quien emite el evento -->
  <cac:ReceiverParty>...</cac:ReceiverParty>              <!-- Emisor original de la FE -->
  <cac:DocumentResponse>
    <cac:Response>
      <cbc:ResponseCode>030</cbc:ResponseCode>            <!-- Código del evento -->
      <cbc:Description>Acuse de recibo...</cbc:Description>
    </cac:Response>
    <cac:DocumentReference>
      <cbc:ID>SETG980000358</cbc:ID>                      <!-- Número factura referenciada -->
      <cbc:UUID schemeName="CUFE-SHA384">...</cbc:UUID>   <!-- CUFE de la factura -->
      <cbc:DocumentTypeCode>01</cbc:DocumentTypeCode>     <!-- 01=Factura -->
    </cac:DocumentReference>
    <cac:IssuerParty>  <!-- Solo en evento 030: persona que recibe -->
      <cac:Person>
        <cbc:ID schemeID="4" schemeName="13">2589846132</cbc:ID>
        <cbc:FirstName>...</cbc:FirstName>
        <cbc:FamilyName>...</cbc:FamilyName>
        <cbc:JobTitle>Revisor Fiscal</cbc:JobTitle>
      </cac:Person>
    </cac:IssuerParty>
  </cac:DocumentResponse>
</ApplicationResponse>
```

### Diferencias entre eventos
| Evento | ResponseCode | IssuerParty (Person) | Atributos extras |
|--------|-------------|---------------------|-----------------|
| 030 Acuse Recibo | `030` | ✅ Sí (receptor) | — |
| 031 Rechazo | `031` | ❌ No | — |
| 032 Recibo B&S | `032` | ❌ No | — |
| 033 Aceptación | `033` | ❌ No | — |
| 034 Reclamo | `034` | ❌ No | `listID="2"` + código reclamo |
| 035 Tácita | `035` | ❌ No | — |

### Códigos de reclamo (evento 034)
- `01`: Documento con inconsistencias
- `02`: Mercancía no entregada totalmente
- `03`: Mercancía no entregada parcialmente
- `04`: Servicio no prestado

### CUDE (Código Único de Documento Electrónico)
Los eventos usan **CUDE** (no CUFE). Se calcula con **SHA-384**:
```
CUDE = SHA384(NumDoc + FechaDoc + HoraDoc + ResponseCode + ... + clave_técnica)
```
- `schemeName="CUDE-SHA384"`, `schemeID="2"`
- La factura original usa `schemeName="CUFE-SHA384"`

### Firma Digital
- **XAdES-EPES** (misma estructura que facturas)
- **SignaturePolicyId** (⚠️ NO `SignaturePolicy` — causa crash XSD)
- Certificado **.p12** del emisor
- URL política de firma: `https://facturaelectronica.dian.gov.co/politicadefirmav2.pdf`

---

## 10. Las 15 Reglas de Oro (aprendidas en producción)

Estas reglas se descubrieron durante la habilitación DIAN. Cada una causó rechazos reales:

| # | Regla | Error si se viola |
|---|-------|-----------------|
| 1 | **`UBLVersionID = 'UBL 2.1'`** (con prefijo) | Regla ZB01: fallo esquema XSD |
| 2 | **CustomizationID varía por tipo:** 10 (FV), 20 (NC ref), 22 (NC sin ref), 30 (ND ref) | Regla CBF03a |
| 3 | **ProfileID incluye tipo de documento** | Regla FAD03 |
| 4 | **AuthorizationProvider con NIT DIAN `800197268`** | Regla FAB31 |
| 5 | **QR Code obligatorio** en DianExtensions | Regla FAB36 |
| 6 | **AllowanceCharge obligatorio** en cada línea (incluso 0) | Regla FBE01 |
| 7 | **Delivery > DeliveryAddress obligatorio** | Regla FAJ28 |
| 8 | **TaxScheme siempre = `01`/IVA** (no-responsable = `TaxLevelCode R-99-PN`) | Regla FAK41 |
| 9 | **Consecutivos irrepetibles** (incluso en pruebas) | Regla 90 |
| 10 | **PaymentMeans > ID es numérico**, incluir PaymentID | Regla FAN02 |
| 11 | **SignaturePolicyId** (no SignaturePolicy) | Crash XSD |
| 12 | **Datos emisor = RUT exacto** (dirección, códigos DANE) | StatusCode 99 |
| 13 | **SendTestSetAsync NO valida XML** — siempre pre-test con SendBillSync | Track ID ≠ éxito |
| 14 | **Fecha generación = fecha firma = fecha transmisión** | Regla FAD09e |
| 15 | **`elem.text` puede ser None** en respuestas SOAP | NoneType crash |

### Dependencia circular CUFE ↔ XML
```
CUFE = SHA384(datos del documento)  ← Solo depende de DATOS, no del XML
QR = URL + CUFE
DianExtensions = { ..., QRCode }
XML = { DianExtensions, datos, CUFE }

Orden correcto:
1. Calcular CUFE con datos puros
2. Crear DianExtensions con QR (que incluye CUFE)
3. Crear el resto del XML
4. Firmar
```

---

## 11. Preguntas que el agente DEBE hacer al usuario

Antes de implementar, obtener respuestas a:

1. **¿Qué módulo maneja la conexión DIAN en V18?** — ¿es `l10n_co_dian`, `l10n_co_edi`, u otro?
2. **¿El modelo `l10n_co_dian.document` existe?** (resultado del script de inspección)
3. **¿Qué campos tiene `account.move` relacionados con DIAN?** (operation_type, etc.)
4. **¿Está el proyecto en Odoo.sh u on-premise?** — afecta los CRONs y deploy
5. **¿Ya tienen certificado .p12 configurado?** — necesario para firmar los ApplicationResponse
6. **¿Qué versión exacta de Odoo 18?** — 18.0 vs 18.x (patches)
7. **¿Hay multi-compañía?** — afecta la configuración de retries/intervalos
8. **¿Qué endpoint DIAN usan?** — habilitación vs producción
9. **¿Tienen software ID y PIN configurados?** — necesarios para DianExtensions
10. **¿Cuál es el prefijo de facturación?** — para generar consecutivos de eventos

---

## 12. Errores comunes a evitar

| Error | Consecuencia | Prevención |
|-------|-------------|------------|
| Usar 034 como Aceptación Tácita | Código incorrecto en XML DIAN | Usar 035 |
| Reloj desde 030 en vez de 032 | Aceptación tácita prematura | Buscar evento 032 |
| Bloquear NC después de `super()._post()` | Consecutivo DIAN consumido | Interceptar ANTES |
| `_sql_constraints` en V19 | Build crash | Usar `models.Constraint` con `_` prefix |
| `numbercall` en CRON V19 | Warning y CRON no funciona | Omitir en V19, incluir en V18 |
| `ref="modulo.model_xxx"` en CRON | XML ID no encontrado | Usar `search="[...]"` si falla |
| No definir `ir.model.access.csv` | Modelo inaccesible | SIEMPRE crear permisos |
| `UBLVersionID = '2.1'` | Rechazo XSD DIAN | Usar `'UBL 2.1'` |
| `SignaturePolicy` en vez de `SignaturePolicyId` | Crash XSD | Verificar contra esquema XAdES |
| Omitir AuthorizationProvider | Regla FAB31 | NIT `800197268` obligatorio |

---

## 13. Archivos de referencia en V19

El agente puede solicitar al usuario que comparta estos archivos como contexto:

| Archivo | Ruta en repo V19 |
|---------|------------------|
| Modelo RADIAN | `insotech_l10n_co_advanced/models/radian_event.py` |
| Festivos | `insotech_l10n_co_advanced/models/custom_holiday.py` |
| Contingencia | `insotech_l10n_co_advanced/models/l10n_co_dian_document.py` |
| CRONs contingencia | `insotech_l10n_co_advanced/data/cron_contingency.xml` |
| CRON tácita | `insotech_l10n_co_advanced/data/cron_radian_tacit.xml` |
| Bloqueo NC/ND | `insotech_l10n_co_advanced/models/account_move.py` |
| Config empresa | `insotech_dian_wizard/models/res_company.py` |
| Generador UBL | `insotech_dian_wizard/services/ubl_generator.py` |
| Firmador XML | `insotech_dian_wizard/services/xml_signer.py` |
| Cliente SOAP | `insotech_dian_wizard/services/soap_client.py` |
| Investigación RADIAN | `Documentacion/RADIAN/INVESTIGACION_RADIAN.md` |
| Investigación Contingencia | `Documentacion/RADIAN/INVESTIGACION_CONTINGENCIA_TIPO4.md` |
| Habilitación DIAN (15 errores) | `.agent/skills/base-de-conocimiento/aprendizajes/dian-habilitacion-facturacion-electronica.md` |

---

> **Nota final:** Este documento es un mapa, no un blueprint. La implementación en V18 puede diferir significativamente dependiendo de los módulos instalados. El paso #3 (inspección) es **OBLIGATORIO** antes de escribir código. La sección de comunicación DIAN (§8-10) contiene lecciones aprendidas en producción real — NO ignorarlas.
