# Odoo V19: GetNumberingRange falla en producción

- **Fecha:** 2026-03-22
- **Última actualización:** 2026-03-23
- **Módulo:** `l10n_co_dian` (nativo Odoo 19)
- **Contexto:** Configuración de diario de ventas para facturación electrónica en producción
- **Severidad:** 🔴 Bloqueante → ✅ Resuelto

## Síntomas

### Error 401
```
NIT: 9017972495 no autorizado para consultar rangos de numeración del NIT: 901797249-5
```
**Causa:** Odoo concatena NIT + DV en un solo string (`901797249` + `5` = `9017972495`) al llamar `GetNumberingRange`. La DIAN espera solo el NIT sin DV.

### Error 302
```
No registra prefijos asociados al código de software: edbcc67c-8baf-4d31-999b-248d742ea430
```
**Causa:** La DIAN demora horas en sincronizar las asociaciones de prefijos entre el portal web (`catalogo-vpfe.dian.gov.co`) y la API SOAP. Si se asoció el prefijo el mismo día, el API aún no lo reconoce.

## 🔍 Investigación WSDL (verificada 2026-03-23)

### Parámetros del SOAP `GetNumberingRange`
Verificado directamente desde el WSDL de producción (`vpfe.dian.gov.co/WcfDianCustomerServices.svc?xsd=xsd0`):

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `accountCode` | string | NIT del solicitante (**sin DV**) |
| `accountCodeT` | string | NIT de la empresa a consultar (**sin DV**) |
| `softwareCode` | string | ID del software registrado en DIAN |

### Cadena completa del error 401
```
res.company.vat = '9017972495' (NIT+DV concatenados)
  → l10n_co_dian toma company.vat
  → Envía como accountCode al SOAP
  → DIAN rechaza: "NIT: 9017972495 no autorizado"
```

### Endpoints SOAP
| Entorno | URL |
|---------|-----|
| Producción | `vpfe.dian.gov.co/WcfDianCustomerServices.svc` |
| Habilitación/Pruebas | `vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc` |

Odoo determina cuál usar según el modo de operación. Con TestSetID desactivado, apunta a producción.

## ✅ Solución Implementada

### Fix del NIT (error 401)
Override de `button_l10n_co_dian_fetch_numbering_range` en `insotech_l10n_co_advanced/models/account_journal.py`:

```python
# Antes de llamar super():
# 1. Detectar si company.vat tiene DV concatenado
# 2. Quitar DV temporalmente
# 3. Llamar super() (que hace el SOAP call)
# 4. Restaurar vat original en finally block
```

**Importante:** La sanitización es temporal (se restaura con `finally`). No se modifica permanentemente el campo `vat` de la empresa.

### Fix del error 302
Override captura UserError con referencia a "302" o "prefijos" y muestra mensaje claro:
- Verificar "Sincronizar a Producción" en portal DIAN
- Esperar 2-24 horas para sincronización API
- Verificar modo de operación = Producción en Odoo
- Como fallback: llenar campos del diario manualmente (campos nativos)

### Limpieza de código invasivo
Se eliminó un wizard y vistas que violaban la filosofía del módulo:
- `wizard/dian_manual_config_wizard.py` → Eliminado
- `wizard/dian_manual_config_wizard_views.xml` → Eliminado
- `views/account_journal_views.xml` → Eliminado
- Los campos nativos del diario (resolución, rangos, clave técnica) ya existen en Odoo y no necesitan wizard adicional.

## 💡 Regla de oro #16 (actualizada)
**Siempre almacenar NIT y DV por separado.** El NIT de la empresa en `res.company.vat` debe ser solo `901797249`. El DV va en `l10n_co_verification_code` = `5`. El override en `account_journal.py` sanitiza automáticamente si están concatenados, pero lo ideal es corregir la configuración.

## 💡 Regla de oro #17
**Nunca agregar wizards ni botones para llenar campos que ya existen nativamente en Odoo.** Los campos de resolución DIAN (`l10n_co_edi_dian_authorization_number`, `l10n_co_edi_min_range_number`, etc.) ya están en la vista del diario. Si el API falla, el usuario puede llenarlos directamente.
