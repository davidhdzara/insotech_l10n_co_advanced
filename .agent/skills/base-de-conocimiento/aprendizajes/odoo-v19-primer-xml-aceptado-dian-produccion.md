# Análisis del Primer XML Aceptado por DIAN (Producción)

- **Fecha:** 2026-03-23 17:02 COT
- **Módulo:** `insotech_l10n_co_advanced`
- **Factura:** FE1
- **Resultado:** ✅ Aceptada (ResponseCode 02)

## Elementos Clave del XML

| Campo XML | Valor | Correcto |
|---|---|:-:|
| `<cbc:ID>` | `FE1` | ✅ |
| `<cbc:ParentDocumentID>` | `FE1` | ✅ |
| `<sts:Prefix>` | `FE` | ✅ |
| `<sts:From>` | `1` | ✅ |
| `<sts:To>` | `5000` | ✅ |
| `<cbc:InvoiceAuthorization>` | `18764107498052` | ✅ |
| `CustomizationID` | `10` (Factura de Venta) | ✅ |
| `ProfileID` | `DIAN 2.1: Factura Electrónica de Venta` | ✅ |
| `ProfileExecutionID` | `1` (Producción) | ✅ |
| `UBLVersionID` | `UBL 2.1` | ✅ |
| `CUFE` (UUID) | `2809c221...` | ✅ |
| `AuthorizationProviderID` | `800197268` (NIT DIAN) | ✅ |
| `QRCode` | URL catálogo DIAN + CUFE | ✅ |
| `TaxScheme ID` | `01` (IVA) | ✅ |
| `SignaturePolicyId` | Política v2 DIAN | ✅ |

## ⚠️ Observación: PaymentID

```xml
<cbc:PaymentID>FE/2026/00001</cbc:PaymentID>
```

Este campo aún tiene el formato viejo con barras (`/`). DIAN **no lo rechazó** — aparentemente no valida este campo contra las reglas FAD05. Sin embargo, es inconsistente con el `<cbc:ID>FE1</cbc:ID>`.

**Causa:** `l10n_co_dian` genera `PaymentID` a partir de `move.name` en un momento diferente al `<cbc:ID>`. Cuando swapeamos el nombre, el `PaymentID` ya fue generado con el nombre anterior (o se genera desde un campo diferente).

**Acción:** No bloqueante. Monitorear si DIAN endurece esta validación en el futuro.

## Respuesta DIAN (ApplicationResponse)

```xml
<cbc:ResponseCode>02</cbc:ResponseCode>
<cbc:Description>Documento validado por la DIAN</cbc:Description>
```

ResponseCode `02` = Documento validado exitosamente.

Notificación informativa: `RUT01` — "La validación del estado del RUT próximamente estará disponible." (No es error, es informativo.)

## 💡 Regla de oro #23
**El campo `<cbc:PaymentID>` en el XML UBL NO es validado por DIAN contra reglas FAD05.** Puede contener barras sin causar rechazo. Sin embargo, mantener consistencia es buena práctica para futuras versiones de la norma.
