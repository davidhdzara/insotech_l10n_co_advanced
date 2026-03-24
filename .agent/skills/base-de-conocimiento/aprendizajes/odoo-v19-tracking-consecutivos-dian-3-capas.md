# Odoo V19: Tracking de Consecutivos DIAN (3 capas)

- **Fecha:** 2026-03-24
- **Módulo:** `insotech_l10n_co_advanced`
- **Contexto:** Protección contra duplicación de consecutivos DIAN tras restauración de BD
- **Severidad:** 🟡 Preventivo

## Problema

Si un cliente restaura la BD, migra de versión, o instala Odoo desde cero, el `SequenceMixin` empieza desde 1. Si ya se consumieron consecutivos en DIAN (ej: FE1-FE5), Odoo no lo sabe e intenta enviar FE1 de nuevo → DIAN rechaza (Regla 90 — duplicado).

**Caso real:** InSoTech envió FE1 exitosamente el 23/03/2026, restauró la BD, y Odoo intentaba enviar FE1 de nuevo.

## Investigación API DIAN

| Endpoint | ¿Sirve? | Limitación |
|---|:-:|---|
| `GetNumberingRange` | ❌ | Solo retorna rango autorizado |
| `GetStatus` | ⚠️ | Requiere `trackId` (UUID), no número |
| Portal DIAN web | ✅ | Manual, sin API pública |

**No existe endpoint DIAN para "último consecutivo usado".**

## ✅ Solución: 3 Capas de Protección

### Capa 1: Persistencia automática
**Archivo:** `account_move.py` → `_insotech_process_dian_acceptance()`

Al aceptar DIAN → guarda el número en `ir.config_parameter`:
```
insotech.dian.last_consecutive.{journal_id} = 3
```
- ✅ Sobrevive actualizaciones de módulo
- ✅ Se incluye en backups de BD
- ❌ No sobrevive instalación desde cero sin backup

### Capa 2: Protección pre-envío
**Archivo:** `account_move.py` → `_insotech_check_duplicate_consecutive()`

Antes de enviar a DIAN:
1. Calcula qué número se enviaría
2. Compara contra `ir.config_parameter`
3. Si N ≤ último aceptado → bloquea con UserError
4. Muestra el siguiente consecutivo disponible

### Capa 3: Detección + override manual
**Archivo:** `account_journal.py` → `action_insotech_detect_last_consecutive()`

Botón en el diario → escanea 3 fuentes:
1. `l10n_co_dian.document` (Enterprise)
2. Facturas posted no-PRE-INV
3. `ir.config_parameter` (valor previo)

Campo `insotech_last_dian_consecutive` (stored) para override manual.

## 💡 Regla de oro #24
**Siempre persistir el último consecutivo DIAN en `ir.config_parameter`.** La BD puede ser restaurada, pero `ir.config_parameter` sobrevive si el backup se hizo correctamente. Para instalaciones desde cero, el usuario DEBE configurar manualmente el último consecutivo en el diario.

## 💡 Regla de oro #25
**Python (.py) se recarga al reiniciar el servidor; XML (.xml) solo se actualiza con Module Upgrade.** Si cambias vistas XML, el cliente DEBE hacer "Actualizar" del módulo en Aplicaciones, no solo reiniciar.
