# insotech_dian_wizard — Documentación Técnica

**Versión:** 19.0.3.0.0
**Última actualización:** 2026-03-22
**Repositorio:** `davidhdzara/insotech` (ramas `dev-fase3.5` / `staging_produccion`)
**Anexo Técnico DIAN:** v1.9 (Resolución 000165/2023, vigente desde mayo 2024)

---

## 1. Propósito

Módulo de habilitación DIAN para facturación electrónica colombiana como **software propio**. Desacopla la habilitación del software de la configuración de Odoo, permitiendo habilitar ante la DIAN con datos emulados sin requerir configuración previa.

### El Problema (flujo nativo Odoo)

El habilitador nativo de Odoo (`l10n_co_dian → action_l10n_co_certify_with_dian`) mezcla habilitación y configuración. Exige: categoría de producto, obligaciones fiscales, ID de ciudad DIAN, NIT formateado, productos, diarios con resolución, etc.

### Nuestra Solución (flujo desacoplado)

```
FLUJO NATIVO (acoplado)       →  FLUJO INSOTECH (desacoplado)
─────────────────────────          ─────────────────────────────
1. Configurar empresa completa     1. Pegar 5 credenciales DIAN
2-7. Configurar todo...            2. Clic "Iniciar Habilitación"
8. ❌ Error por dato faltante      3. ✅ Software habilitado
9. Repetir desde paso 1...         4. AHORA SÍ: configurar Odoo
```

---

## 2. Arquitectura del Módulo

```
insotech_dian_wizard/
├── __init__.py
├── __manifest__.py           (deps: base, account, product, l10n_co_dian)
├── hooks.py                  (post_init_hook para product_category_goods)
├── models/
│   ├── res_company.py        (4 campos DIAN + _register_hook)
│   └── res_config_settings.py (Panel en Ajustes)
├── wizard/
│   └── dian_setup_wizard.py  (Orquestador de habilitación)
├── services/
│   ├── test_data.py          (Datos emulados + constantes DIAN)
│   ├── ubl_generator.py      (Generador UBL 2.1: FV/NC/ND)
│   ├── xml_signer.py         (Firma XAdES-EPES con .p12)
│   └── soap_client.py        (Cliente SOAP 1.2 WS-Security)
├── views/
│   ├── dian_setup_wizard_views.xml
│   └── res_config_settings_views.xml
└── security/
    └── ir.model.access.csv
```

---

## 3. Flujo de Habilitación

```
┌──────────────────────────────────────────────┐
│ 1. Usuario ingresa credenciales DIAN:        │
│    Software ID / PIN / Test Set ID           │
│    Clave Técnica / .p12 + Password           │
│    Cantidades: 30 FV + 10 NC + 10 ND        │
└─────────────────┬────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────┐
│ 2. ubl_generator.py                         │
│    - Genera XMLs UBL 2.1 con datos emulados │
│    - Calcula CUFE/CUDE (SHA-384)            │
│    - Incluye QR Code en DianExtensions      │
│    - AuthorizationProvider (NIT DIAN)        │
└─────────────────┬────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────┐
│ 3. xml_signer.py                            │
│    - Lee .p12 del campo l10n_co_dian        │
│    - Firma XAdES-EPES (RSA-SHA256)          │
│    - Incluye SignaturePolicyId v2           │
│    - Digest de doc, KeyInfo, SignedProps     │
└─────────────────┬────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────┐
│ 4. PRE-TEST: SendBillSync (1 factura)       │
│    - Envía UNA factura individual           │
│    - Retorna errores EXACTOS de la DIAN     │
│    - Si falla → PARA y muestra errores      │
│    - Si pasa → procede con batch            │
└─────────────────┬────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────┐
│ 5. BATCH: SendTestSetAsync (50 docs)        │
│    - Empaqueta XMLs en ZIP base64           │
│    - Envía via SendTestSetAsync con TestSetId│
│    - Recibe Track ID (ZipKey)               │
│    - Consulta GetStatusZip                  │
└─────────────────┬────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────┐
│ 6. Si IsValid=true → ✅ Software Habilitado │
│    Marcar estado = 'enabled'                │
└──────────────────────────────────────────────┘
```

---

## 4. Servicios — Detalle Técnico

### 4.1 `test_data.py` — Datos Emulados

| Dato | Valor | Nota |
|------|-------|------|
| **Emisor** | INFINITY SOLUTIONS TECHNOLOGY S.A.S | Datos exactos del RUT |
| NIT Emisor | 901797249-5 | DV verificado |
| Ciudad Emisor | Bello (05088), Antioquia (05) | Código DANE exacto |
| Código Postal | 051050 | Del RUT |
| Dirección | DG 54 19 20 | Del RUT |
| **Receptor** | ADQUIRIENTE DE PRUEBAS DIAN | Consumidor final |
| NIT Receptor | 222222222222-2 | Consumidor final DIAN |
| Doc Type Receptor | 13 (Cédula) | Para consumidor final |
| **Producto** | Servicio consultoría | $100.000 + IVA 19% |
| **Resolución** | 18760000001 | Resolución habilitación |
| **Prefijo** | SETP | Prefijo set de pruebas |
| **Rango** | 990000000 – 995000000 | Rango autorizado |

> **CRÍTICO:** Los datos del emisor DEBEN coincidir exactamente con el RUT. Cualquier diferencia (ciudad, dirección, razón social) causa rechazo silencioso.

### 4.2 `ubl_generator.py` — Generador XML UBL 2.1

Genera documentos conformes al Anexo Técnico v1.9:

| Función | Tipo Doc | CustomizationID | ProfileID |
|---------|----------|----------------|-----------|
| `generate_invoice()` | 01 (Factura) | 10 | DIAN 2.1: Factura Electrónica de Venta |
| `generate_credit_note()` | 91 (NC) | 20 | DIAN 2.1: Nota Crédito |
| `generate_debit_note()` | 92 (ND) | 30 | DIAN 2.1: Nota Débito |

**Estructura XML generada:**

```xml
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="..." xmlns:cbc="..." xmlns:ext="..." xmlns:sts="...">
  <ext:UBLExtensions>
    <ext:UBLExtension> <!-- DIAN Extensions -->
      <sts:DianExtensions>
        <sts:InvoiceControl>...</sts:InvoiceControl>    <!-- Resolución -->
        <sts:InvoiceSource>CO</sts:InvoiceSource>
        <sts:SoftwareProvider>...</sts:SoftwareProvider> <!-- NIT + SoftwareID -->
        <sts:SoftwareSecurityCode>SHA384</sts:SoftwareSecurityCode>
        <sts:AuthorizationProvider>                      <!-- NIT DIAN -->
          <sts:AuthorizationProviderID>800197268</sts:AuthorizationProviderID>
        </sts:AuthorizationProvider>
        <sts:QRCode>https://catalogo-vpfe-hab.dian.gov.co/...</sts:QRCode>
      </sts:DianExtensions>
    </ext:UBLExtension>
    <ext:UBLExtension> <!-- Firma Digital XAdES -->
      <ds:Signature>...</ds:Signature>
    </ext:UBLExtension>
  </ext:UBLExtensions>
  <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
  <cbc:CustomizationID>10</cbc:CustomizationID>
  <cbc:ProfileID>DIAN 2.1: Factura Electrónica de Venta</cbc:ProfileID>
  <cbc:ProfileExecutionID>2</cbc:ProfileExecutionID>  <!-- Pruebas -->
  <cbc:ID>SETP99XXXXXXX</cbc:ID>
  <cbc:UUID schemeName="CUFE-SHA384">...</cbc:UUID>
  <!-- ... demás secciones UBL 2.1 ... -->
</Invoice>
```

**Cálculo CUFE (facturas):**
```
SHA384(NumFac + FecFac + HorFac + ValFac +
       CodImp1 + ValImp1 + CodImp2 + ValImp2 +
       CodImp3 + ValImp3 + ValTot +
       NitOFE + NumAdq + ClTec + TipoAmbie)
```

**Cálculo CUDE (NC/ND):** Misma fórmula pero sustituye Clave Técnica por PIN del software.

**Consecutivos dinámicos:** Cada ejecución genera números únicos basados en `time.time()` para evitar Regla 90 (documento duplicado).

### 4.3 `xml_signer.py` — Firma XAdES-EPES

| Algoritmo | Valor |
|-----------|-------|
| Canonicalización | `http://www.w3.org/TR/2001/REC-xml-c14n-20010315` |
| Firma | RSA-SHA256 (`xmldsig-more#rsa-sha256`) |
| Digest | SHA-256 (`xmlenc#sha256`) |
| Política de firma | `politicadefirmav2.pdf` (DIAN v2) |
| Rol firmante | `supplier` |

**Estructura de firma:**
- `ds:SignedInfo` con 3 references (documento, KeyInfo, SignedProperties)
- `ds:SignatureValue` (RSA-SHA256 sobre SignedInfo c14n)
- `ds:KeyInfo > X509Data > X509Certificate` (certificado DER en base64)
- `xades:QualifyingProperties > SignedProperties`
  - `SigningTime`
  - `SigningCertificate` (digest + issuer + serial)
  - `SignaturePolicyIdentifier > SignaturePolicyId` (política DIAN)
  - `SignerRole > ClaimedRoles > supplier`

### 4.4 `soap_client.py` — Cliente SOAP WS-Security

| Método | SOAP Action | Uso |
|--------|-------------|-----|
| `send_bill_sync()` | `SendBillSync` | Enviar 1 documento → respuesta inmediata con errores |
| `send_test_set_async()` | `SendTestSetAsync` | Enviar batch completo → Track ID |
| `get_status_zip()` | `GetStatusZip` | Consultar estado por Track ID |

**Endpoints:**
- Habilitación: `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc`
- Producción: `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc`

**Parser de respuesta:** Captura `StatusCode`, `IsValid`, `ErrorMessages`, `XmlDocumentComment`, `ApplicationResponse` (base64 decoded), y siempre incluye respuesta SOAP raw para debug.

---

## 5. Wizard — Interfaz de Usuario

### Campos del wizard

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `software_id` | Char | UUID del software registrado en DIAN |
| `software_pin` | Char | PIN del software (5 dígitos) |
| `test_set_id` | Char | UUID del set de pruebas |
| `technical_key` | Char | Clave técnica de habilitación |
| `cert_file` | Binary | Certificado .p12 |
| `cert_password` | Char | Contraseña del .p12 |
| `num_invoices` | Integer | Facturas a generar (default: 30) |
| `num_credit_notes` | Integer | Notas crédito (default: 10) |
| `num_debit_notes` | Integer | Notas débito (default: 10) |
| `config_state` | Selection | not_configured / in_progress / enabled |
| `habilitacion_state` | Selection | idle / sending / waiting / error |
| `track_id` | Char | Track ID del último envío |
| `result_log` | Html | Log de resultados en tiempo real |

### Botones

| Botón | Método | Descripción |
|-------|--------|-------------|
| 💾 Guardar Credenciales | `action_save_config` | Guarda sin enviar |
| 🚀 Iniciar Habilitación | `action_start_habilitacion` | Pre-test + batch |
| 🔍 Probar 1 Factura | `action_test_single` | SendBillSync individual |
| 🔄 Consultar Estado | `action_check_status` | GetStatusZip |
| ✅ Marcar Habilitado | `action_mark_enabled` | Manual override |
| 🔓 Desbloquear | `action_unlock` | Reset a in_progress |

### Flujo de pre-test (SendBillSync)

`action_start_habilitacion` ejecuta este flujo:
1. Genera todos los XMLs (FV + NC + ND)
2. Firma todos con .p12
3. **ANTES de enviar el batch:** envía 1 factura via `SendBillSync`
4. Si `IsValid=true` → procede con batch de 50
5. Si `IsValid=false` → muestra errores exactos y **PARA**
6. Sin respuesta clara → intenta batch de todas formas

---

## 6. Reglas DIAN Validadas

### Errores encontrados y corregidos durante habilitación

| Regla | Error | Causa | Fix |
|-------|-------|-------|-----|
| ZB01 | Fallo esquema XML | `UBLVersionID='2.1'` | → `'UBL 2.1'` |
| ZB01 | `SignaturePolicy` no existe | Nombre de elemento XAdES | → `SignaturePolicyId` |
| FAD03 | ProfileID incompleto | Solo `'DIAN 2.1'` | → `'DIAN 2.1: Factura Electrónica de Venta'` |
| FAB31 | AuthorizationProviderID | Sección faltante | → NIT DIAN `800197268` |
| FAB36 | QR Code faltante | No se incluía | → URL `catalogo-vpfe-hab.dian.gov.co` |
| Regla 90 | Documento duplicado | Mismos consecutivos | → Offset basado en timestamp |
| FAN02 | Método pago inválido | ID texto + falta PaymentID | → ID numérico + PaymentID |
| FAB35 | Tipo doc ≠ 31 | Receptor con NIT incorrecto | → Consumidor final (13) |
| FAK24 | DV incorrecto | DV inventado | → DV calculado correctamente |
| CBF03a | CustomizationID | Mismo valor (10) para todo | → 10/20/30 por tipo doc |
| FBE01 | AllowanceCharge faltante | NC/ND sin descuento | → AllowanceCharge con 0.00 |

### Checklist pre-envío

- ✅ Datos emisor = RUT exacto (carácter por carácter)
- ✅ CustomizationID: 10 (FV), 20 (NC), 30 (ND)
- ✅ ProfileID incluye tipo de documento
- ✅ UBLVersionID = `'UBL 2.1'` (no `'2.1'`)
- ✅ AuthorizationProvider con NIT DIAN
- ✅ QR Code con URL catalogo-vpfe-hab
- ✅ SignaturePolicyId (no SignaturePolicy)
- ✅ AllowanceCharge en todas las líneas
- ✅ Consecutivos únicos por ejecución
- ✅ Fecha = hoy (FAD09e)
- ✅ SendBillSync pre-test antes del batch

---

## 7. Set de Pruebas Requerido

| Documento | Cantidad | Método |
|-----------|----------|--------|
| Factura electrónica (01) | 30 | SendTestSetAsync |
| Nota crédito (91) | 10 | SendTestSetAsync |
| Nota débito (92) | 10 | SendTestSetAsync |
| **Total** | **50** | Batch con TestSetId |

---

## 8. Relación con Otros Módulos

```
PASO 1: Habilitación (desacoplada — este módulo)
┌─────────────────────────┐
│  insotech_dian_wizard   │ ← Solo credenciales + datos emulados
│  deps: l10n_co_dian     │    Resultado: software habilitado ante DIAN
└────────────┬────────────┘
             │
PASO 2: Configuración producción (Odoo nativo)
             ▼
┌─────────────────────────┐
│  l10n_co_dian (nativo)  │ ← Empresa + certificado + resolución real
│  l10n_co_edi            │    + diarios + contactos reales
└────────────┬────────────┘
             │
PASO 3: Protección avanzada
             ▼
┌──────────────────────────────┐
│  insotech_l10n_co_advanced   │ ← PRE-INV, hooks DIAN, banners
│  deps: insotech_dian_wizard  │
└──────────────────────────────┘
```

---

## 9. Historial de Commits

| Hash | Mensaje |
|------|---------|
| `e3c83dc` | `[ADD]` Wizard simplificado para habilitación DIAN |
| `10802b7` | `[ADD]` Habilitación DIAN directa via SOAP |
| `8d3dcd1` | `[ADD]` Probar 1 Factura (SendBillSync) |
| `5b3cb72` | `[FIX]` CustomizationID NC=20, ND=30 |
| `3cdc2f6` | `[FIX]` Mostrar errores exactos de la DIAN |
| `50b717b` | `[FIX]` Crash NoneType en parser XmlBase64Bytes |
| `a59f416` | `[FIX]` UBLVersionID 'UBL 2.1' (ZB01) |
| `a94375f` | `[FIX]` Regla 90 — consecutivos dinámicos |
| `49ce554` | `[FIX]` 10+ errores validación DIAN (mega fix) |

---

## 10. Testing

### Pre-requisitos
- Build exitoso en `staging_produccion`
- Certificado .p12 cargado
- Credenciales DIAN (SoftwareID, PIN, TestSetId, Clave Técnica)

### Flujo de prueba
1. **Contabilidad → Configuración → Habilitación DIAN**
2. Llenar credenciales DIAN
3. Adjuntar .p12 + password
4. Configurar: 1 FV, 1 NC, 1 ND (prueba rápida)
5. Clic **"🚀 Iniciar Habilitación DIAN"**
6. Verificar que SendBillSync retorne `IsValid: true`
7. Si pasa → cambiar a 30/10/10 y enviar set completo
8. Verificar en portal DIAN: `catalogo-vpfe-hab.dian.gov.co`
