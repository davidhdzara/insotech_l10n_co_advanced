# Habilitación DIAN — Facturación Electrónica (Software Propio)

**Fecha de Registro:** 2026-03-22
**Última actualización:** 2026-03-22 (sesión nocturna completa)
**Contexto:** Habilitación de InSoTech como software propio de facturación electrónica ante la DIAN. Módulo `insotech_dian_wizard` en Odoo 19 sobre Odoo.sh. Anexo Técnico v1.9 (Resolución 165/2023, vigente desde mayo 2024).

---

## 🚨 Errores Encontrados (en orden de descubrimiento)

### 1. SendTestSetAsync enmascara errores silenciosamente
**Síntoma:** El batch se queda en "Batch en proceso de validación" PARA SIEMPRE. `GetStatusZip` siempre retorna "en proceso".

**Causa:** `SendTestSetAsync` NO reporta errores de validación XML. Si los documentos tienen campos incorrectos, se quedan "procesando" indefinidamente. No hay timeout ni error explícito.

**Trampa para el desarrollador:** Se asume que recibir un Track ID = envío exitoso. **Falso.** El Track ID solo confirma que el ZIP llegó a la DIAN, no que los documentos sean válidos.

**Fix:** Usar `SendBillSync` ANTES del batch para validar 1 factura individual. Retorna errores exactos de inmediato.

---

### 2. Datos del emisor NO coincidían con el RUT
**Síntoma:** StatusCode 99 — "Documento con errores en campos mandatorios"

**Causa:** Se inventaron datos de prueba (ciudad Bogotá) cuando el RUT dice Bello, Antioquia.

**Trampa para el desarrollador:** Pensar que "para pruebas no importa la dirección". La DIAN valida TODOS los datos contra el RUT en tiempo real, incluso en ambiente de habilitación.

**Datos corregidos:**
```python
EMITTER = {
    'company_name': 'INFINITY SOLUTIONS TECHNOLOGY S.A.S',  # SIN punto final
    'address_line': 'DG 54 19 20',       # Exacto del RUT
    'city_name': 'Bello',                # No Bogotá
    'city_code': '05088',                # Depto(05) + Ciudad(088) DANE
    'department': 'Antioquia',
    'department_code': '05',
    'postal_zone': '051050',
    'nit': '901797249',
    'dv': '5',
}
```

---

### 3. CustomizationID incorrecto para NC/ND (Regla CBF03a)
**Síntoma:** Rechazo silencioso de notas crédito y débito.

**Causa:** Se usaba `CustomizationID = '10'` para todos los tipos de documento.

**Trampa para el desarrollador:** Asumir que CustomizationID es fijo. Cada tipo de documento electrónico tiene su propio valor.

**Valores correctos:**
| Tipo | CustomizationID | Descripción |
|------|----------------|-------------|
| Factura | 10 | Factura electrónica de venta |
| Nota Crédito con referencia | 20 | NC que anula FV específica |
| Nota Crédito sin referencia | 22 | NC independiente |
| Nota Débito con referencia | 30 | ND que corrige FV específica |
| Nota Débito sin referencia | 32 | ND independiente |

---

### 4. UBLVersionID = '2.1' en vez de 'UBL 2.1' (Regla ZB01)
**Síntoma:** "Fallo en el esquema XML del archivo — MessagesType not found"

**Causa:** El XSD de la DIAN valida el valor exacto del string `UBLVersionID`. El estándar UBL especifica `'UBL 2.1'` como string completo, no solo `'2.1'`.

**Trampa para el desarrollador:** Parece lógico poner solo la versión numérica. Pero la DIAN valida contra XSD y el tipo `UBLVersionIDType` exige el prefijo `UBL `.

```python
# ❌ INCORRECTO — Regla ZB01
UBL_VERSION = '2.1'

# ✅ CORRECTO
UBL_VERSION = 'UBL 2.1'
```

---

### 5. SignaturePolicy en vez de SignaturePolicyId (Regla ZB01)
**Síntoma:** "Fallo en el Schema XML — Invalid content was found starting with element 'SignaturePolicy'. One of 'SignaturePolicyId, SignaturePolicyImplied' is expected."

**Causa:** El estándar XAdES v1.3.2 define `SignaturePolicyId` como el elemento hijo de `SignaturePolicyIdentifier`. `SignaturePolicy` no existe en el schema.

**Trampa para el desarrollador:** El nombre `SignaturePolicy` parece correcto intuitivamente. Pero XAdES es muy estricto con los nombres de elementos.

```python
# ❌ INCORRECTO — elemento no existe en XAdES v1.3.2
spi, '{%s}SignaturePolicy' % ns_xades

# ✅ CORRECTO
spi, '{%s}SignaturePolicyId' % ns_xades
```

---

### 6. ProfileID sin tipo de documento (Regla FAD03)
**Síntoma:** "ProfileID no contiene el literal 'DIAN 2.1: Factura Electrónica de Venta'"

**Causa:** Se usaba solo `'DIAN 2.1'` sin especificar el tipo de documento.

**Trampa para el desarrollador:** La documentación general dice "ProfileID = DIAN 2.1" pero la DIAN exige el tipo de documento como sufijo.

**Valores correctos:**
```python
# Factura
'DIAN 2.1: Factura Electrónica de Venta'
# Nota Crédito
'DIAN 2.1: Nota Crédito'
# Nota Débito
'DIAN 2.1: Nota Débito'
```

---

### 7. AuthorizationProvider faltante (Regla FAB31)
**Síntoma:** "AuthorizationProviderID no corresponde al NIT de la DIAN (800197268)"

**Causa:** La sección `sts:AuthorizationProvider` no existía en el bloque `DianExtensions`. Es obligatoria y DEBE contener el NIT de la DIAN (800197268, no el del facturador).

**Trampa para el desarrollador:** Olvidar que DianExtensions necesita información de la DIAN misma, no solo del facturador.

```xml
<sts:AuthorizationProvider>
  <sts:AuthorizationProviderID schemeID="4" schemeName="31"
    schemeAgencyID="195"
    schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">
    800197268
  </sts:AuthorizationProviderID>
</sts:AuthorizationProvider>
```

---

### 8. QR Code faltante (Regla FAB36)
**Síntoma:** "No se encuentra informado el QR Code"

**Causa:** El bloque `sts:QRCode` no existía en `DianExtensions`. Es obligatorio y contiene una URL al catálogo DIAN con el CUFE/CUDE como parámetro.

**Formato:**
```
https://catalogo-vpfe-hab.dian.gov.co/document/searchqr?documentkey={CUFE}
```

**Trampa para el desarrollador:** El QR Code requiere el CUFE, que se calcula con datos del XML. Esto crea una dependencia circular: necesitas el CUFE para el QR, pero el QR va DENTRO del XML. La solución es computar el CUFE primero (solo depende de datos, no del XML), luego construir el XML con ambos.

---

### 9. Documento duplicado (Regla 90)
**Síntoma:** "Documento procesado anteriormente"

**Causa:** Cada ejecución del wizard generaba los mismos consecutivos empezando en `990000000`. Si se reenvía, la DIAN rechaza por duplicado.

**Trampa para el desarrollador:** Asumir que se puede reusar el mismo número de documento en reintentos. La DIAN mantiene un registro permanente de cada consecutivo, incluso en ambiente de pruebas.

**Fix:** Offset dinámico basado en timestamp:
```python
import time
offset = int(time.time()) % 4000000
start_number = DIAN_HAB_RANGE_FROM + offset  # Único por ejecución
```

---

### 10. Método de pago inválido (Regla FAN02)
**Síntoma:** "Método de pago inválido"

**Causa:** `PaymentMeans > ID` tenía texto (`'Medio de pago'`) en vez de un número, y faltaba `PaymentID`.

**Trampa para el desarrollador:** El campo `ID` en `PaymentMeans` es numérico (secuencia), no descriptivo. Y `PaymentID` es el identificador del pago (puede ser el número de documento).

```python
# ❌ INCORRECTO
_cbc(pm, 'ID', 'Medio de pago')

# ✅ CORRECTO
_cbc(pm, 'ID', '1')            # Secuencia numérica
_cbc(pm, 'PaymentMeansCode', '10')  # 10=Efectivo
_cbc(pm, 'PaymentID', doc_number)   # Obligatorio
```

---

### 11. Delivery Address faltante (Regla FAJ28)
**Síntoma:** "No fue informado el conjunto formado por los elementos: ID, CityName, CountrySubentity, CountrySubentityCode, PostalZone, AddressLine, Line, Country, IdentificationCode"

**Causa:** Faltaba la sección `cac:Delivery > cac:DeliveryAddress` completa.

**Trampa para el desarrollador:** Asumir que las direcciones en `AccountingCustomerParty` son suficientes. La DIAN exige TAMBIÉN una dirección de entrega separada.

```xml
<cac:Delivery>
  <cac:DeliveryAddress>
    <cbc:ID>11001</cbc:ID>
    <cbc:CityName>Bogotá, D.C.</cbc:CityName>
    <cbc:PostalZone>110111</cbc:PostalZone>
    <cbc:CountrySubentity>Bogotá</cbc:CountrySubentity>
    <cbc:CountrySubentityCode>11</cbc:CountrySubentityCode>
    <cac:AddressLine><cbc:Line>Cra 7 # 45-12</cbc:Line></cac:AddressLine>
    <cac:Country>
      <cbc:IdentificationCode>CO</cbc:IdentificationCode>
      <cbc:Name languageID="es">Colombia</cbc:Name>
    </cac:Country>
  </cac:DeliveryAddress>
</cac:Delivery>
```

---

### 12. TaxScheme del receptor inválido (Regla FAK41)
**Síntoma:** "El contenido de este elemento no corresponde al Nombre y código válido"

**Causa:** Se usó `TaxScheme.ID = 'ZZ'` y `TaxScheme.Name = 'No Aplica'` para el consumidor final. No son valores del catálogo DIAN.

**Trampa para el desarrollador:** Confundir "responsabilidad tributaria" con "esquema tributario". El TaxScheme SIEMPRE debe ser un código del catálogo DIAN (`01` = IVA). La NO-responsabilidad se indica con `TaxLevelCode = 'R-99-PN'`.

```python
# ❌ INCORRECTO — ZZ no es código DIAN
'tax_scheme_id': 'ZZ',
'tax_scheme_name': 'No Aplica',

# ✅ CORRECTO — Esquema = IVA, responsabilidad = R-99-PN
'tax_scheme_id': '01',
'tax_scheme_name': 'IVA',
'tax_level_code': 'R-99-PN',  # No responsable
```

---

### 13. AllowanceCharge faltante en líneas NC/ND (Regla FBE01)
**Síntoma:** Campos mandatorios faltantes en líneas de detalle.

**Causa:** Las líneas de CreditNote y DebitNote no incluían el bloque `AllowanceCharge`.

**Trampa para el desarrollador:** Asumir que AllowanceCharge es opcional si no hay descuento. Para la DIAN es OBLIGATORIO en cada línea, aunque sea 0.

```xml
<cac:AllowanceCharge>
  <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
  <cbc:MultiplierFactorNumeric>0.00</cbc:MultiplierFactorNumeric>
  <cbc:Amount currencyID="COP">0.00</cbc:Amount>
  <cbc:BaseAmount currencyID="COP">100000.00</cbc:BaseAmount>
</cac:AllowanceCharge>
```

---

### 14. AdditionalAccountID erróneo para consumidor final
**Síntoma:** Warnings del receptor sobre tipo de persona.

**Causa:** Se usaba `AdditionalAccountID = '1'` (jurídica) para el consumidor final.

**Valores correctos:**
- `1` = Persona jurídica
- `2` = Persona natural

---

### 15. Parser SOAP crashea con NoneType
**Síntoma:** `'NoneType' object is not subscriptable` al leer respuesta DIAN.

**Causa:** `XmlBase64Bytes` puede tener `.text = None` cuando la DIAN no devuelve ApplicationResponse.

**Trampa para el desarrollador:** Asumir que todos los campos del SOAP response tienen contenido. Siempre validar `elem is not None and elem.text` antes de procesar.

---

## 🔍 Causa Raíz General

1. **Falta de validación previa contra XSD** antes de enviar a la DIAN.
2. **Datos de prueba inventados** en vez de tomarse del RUT oficial.
3. **SendTestSetAsync tratado como validador** cuando solo es un canal de envío.
4. **Diferencia sutil entre el estándar UBL genérico y los requerimientos DIAN** — la DIAN agrega reglas propias (AuthorizationProvider, QR, Delivery obligatorio, etc.)

---

## ✅ Arquitectura que Funciona

### Flujo de envío correcto:

```
1. Computar CUFE/CUDE (SHA384)
2. Construir XML UBL 2.1 con DianExtensions (incluye QR con CUFE)
3. Firmar con XAdES-EPES (SignaturePolicyId, NO SignaturePolicy)
4. Enviar 1 factura via SendBillSync (pre-test)
5. Si IsValid=true → enviar batch de 50 via SendTestSetAsync
6. Consultar GetStatusZip con Track ID
```

### Dependencia circular CUFE ↔ XML:
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

### Parser de respuesta DIAN robusto:
```python
# SIEMPRE capturar estos campos
result = {
    'StatusCode': ...,
    'IsValid': ...,
    'StatusDescription': ...,
    'ErrorMessageList': ...,        # Lista de reglas que fallaron
    'XmlDocumentComment': ...,      # Comentario de validación
    'ApplicationResponse': ...,     # Decodificar de XmlBase64Bytes
    'raw_response': ...,            # SIEMPRE incluir raw para debug
}
```

---

## 💡 Las 15 Reglas de Oro

1. **NUNCA confiar en SendTestSetAsync para diagnosticar.** Siempre pre-validar con SendBillSync.

2. **Datos del emisor = RUT exacto.** Carácter por carácter: razón social, dirección, códigos DANE.

3. **UBLVersionID = `'UBL 2.1'`** (con prefijo), NO `'2.1'`.

4. **CustomizationID varía:** 10 (FV), 20 (NC ref), 22 (NC sin ref), 30 (ND ref), 32 (ND sin ref).

5. **ProfileID incluye tipo de documento:** `'DIAN 2.1: Factura Electrónica de Venta'`, etc.

6. **AuthorizationProvider es OBLIGATORIO** con NIT de la DIAN: `800197268`.

7. **QR Code es OBLIGATORIO** en `DianExtensions`. Calcular CUFE primero.

8. **AllowanceCharge es OBLIGATORIO** en cada línea, incluso si es 0.00.

9. **Delivery > DeliveryAddress es OBLIGATORIO** para facturas.

10. **TaxScheme siempre es `01`/IVA.** La no-responsabilidad se indica con `TaxLevelCode`, no con el TaxScheme.

11. **Consecutivos son irrepetibles.** Usar offset dinámico para evitar Regla 90.

12. **PaymentMeans > ID es numérico,** no descriptivo. Incluir PaymentID.

13. **SignaturePolicyId** (no SignaturePolicy) dentro de `SignaturePolicyIdentifier`.

14. **Fecha de generación = fecha de firma = fecha de transmisión** (Regla FAD09e).

15. **`elem.text` puede ser None** en respuestas SOAP. Siempre validar antes de usar.

---

## 📋 Checklist Pre-Envío

- [ ] Datos del emisor = RUT exacto (campo por campo)
- [ ] `UBLVersionID` = `'UBL 2.1'`
- [ ] `CustomizationID` correcto por tipo de documento
- [ ] `ProfileID` incluye tipo de documento
- [ ] `AuthorizationProvider` con NIT DIAN `800197268`
- [ ] `QR Code` en DianExtensions con CUFE
- [ ] `AllowanceCharge` en TODAS las líneas (incluso 0)
- [ ] `cac:Delivery > DeliveryAddress` completo
- [ ] `TaxScheme` = `01`/IVA (no ZZ)
- [ ] `SignaturePolicyId` (no SignaturePolicy)
- [ ] `PaymentMeans` con ID numérico + PaymentID
- [ ] Consecutivos únicos por ejecución
- [ ] Fecha = hoy (no cachear)
- [ ] SendBillSync pre-test antes del batch
- [ ] Certificado .p12 vigente
- [ ] NIT sin DV en cálculos, DV como atributo separado

---

## 📊 Resumen de Reglas DIAN Encontradas

| Regla | Tipo | Descripción | Fácil de cometer |
|-------|------|-------------|-------------------|
| ZB01 | Rechazo | Fallo esquema XSD | ⭐⭐⭐⭐⭐ |
| FAD03 | Rechazo | ProfileID incompleto | ⭐⭐⭐⭐ |
| FAD06 | Rechazo | CUFE incorrecto | ⭐⭐⭐⭐⭐ |
| FAB10a | Rechazo | Prefijo ≠ sucursal | ⭐⭐⭐ |
| FAB31 | Rechazo | AuthorizationProvider faltante | ⭐⭐⭐⭐ |
| FAB35 | Rechazo | Tipo doc identidad ≠ 31 | ⭐⭐⭐ |
| FAB36 | Rechazo | QR Code faltante | ⭐⭐⭐⭐ |
| FAJ28 | Rechazo | Delivery address faltante | ⭐⭐⭐⭐⭐ |
| FAK24 | Rechazo | DV incorrecto | ⭐⭐⭐ |
| FAN02 | Rechazo | Método pago inválido | ⭐⭐⭐ |
| FBE01 | Rechazo | AllowanceCharge faltante | ⭐⭐⭐⭐ |
| CBF03a | Rechazo | CustomizationID único por tipo | ⭐⭐⭐⭐ |
| Regla 90 | Rechazo | Documento duplicado | ⭐⭐⭐ |
| FAK41 | Notificación | Código inválido en catálogo | ⭐⭐⭐⭐ |
| FAK28 | Notificación | RegistrationAddress faltante | ⭐⭐⭐ |
