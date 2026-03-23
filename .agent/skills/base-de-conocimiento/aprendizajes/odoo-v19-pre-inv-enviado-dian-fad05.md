# PRE-INV enviado a la DIAN en vez del nombre real (FAD05a/b/c)

- **Fecha:** 2026-03-23
- **Módulo:** `insotech_l10n_co_advanced`
- **Contexto:** Primera factura real en producción — errores FAD05a/b/c
- **Severidad:** 🔴 Bloqueante → ✅ Resuelto en producción

## Síntomas

```
FAD05a: Número de factura contiene caracteres adicionales como espacios o guiones
FAD05b: Número de factura inferior al inicial del rango autorizado
FAD05c: Número de factura superior al final del rango otorgado
```

## Causa Raíz

**Problema 1 (nombre):** `_post()` renombra la factura a `PRE-INV/2026/00001` ANTES de que `l10n_co_dian` lea `move.name` para generar el XML.

**Problema 2 (formato):** El `sequence_prefix` del diario genera `FE/2026/00001` (con barras y año), pero DIAN espera `FE1` (prefijo + número, sin separadores).

**Problema 3 (punto de intercepción):** Los métodos `_l10n_co_dian_post`, `_l10n_co_edi_send`, y `_hook_invoice_document_before_pdf` **NO existen** en Odoo 19. El flujo real es:
```
"Enviar" → action_send_and_print() → account.move.send wizard → l10n_co_dian genera XML
```

## Solución Final

### 1. Override de `action_send_and_print()` (CRÍTICO)
Este es el **ÚNICO punto de intercepción confiable**. Se ejecuta cuando el usuario presiona "Enviar":
```python
def action_send_and_print(self, **kwargs):
    self._insotech_swap_to_dian_name()  # PRE-INV → FE1
    try:
        return super().action_send_and_print(**kwargs)
    except Exception:
        self._insotech_swap_to_pre_inv_name()  # Restaurar PRE-INV
        raise
```

### 2. Transformación dinámica de nombre
`_insotech_compute_dian_compliant_name()` transforma:
- Lee prefijo de `journal.code` (dinámico: FE, FEI, FEGU, NC…)
- Extrae número trailing con regex
- Auto-offset si `min_range > 1` (ej: 5001-10000)
- Valida contra `max_range` (UserError si agotado)

```
FE/2026/00001  → FE1
FEI/2026/00023 → FEI23
FE/2026/00003 (min_range=5001) → FE5003 (auto-offset)
```

### 3. Flujo completo probado en producción
```
Confirmar → PRE-INV/2026/00017
  ↓
Enviar → swap: PRE-INV → FE1
  ↓
l10n_co_dian → <cbc:ID>FE1</cbc:ID>
  ↓
DIAN → ✅ Aceptada → nombre final = FE1
  ↓ (si rechaza)
DIAN → ❌ → swap back PRE-INV → reintentar sin perder consecutivo
```

## 💡 Regla de oro #18
**Nunca enviar un nombre temporal (PRE-INV) a la DIAN.** El swap DEBE ocurrir en `action_send_and_print()` — es el único punto de intercepción confiable en Odoo 19.

## 💡 Regla de oro #19
**El formato del `sequence_prefix` del diario DIAN es irrelevante** — nuestro código transforma `FE/2026/00001` → `FE1` dinámicamente. No requiere configuración manual del prefijo.

## 💡 Regla de oro #20
**NUNCA asumir nombres de métodos de `l10n_co_dian`.** Los métodos `_l10n_co_dian_post`, `_l10n_co_edi_send`, `_hook_invoice_document_before_pdf` NO existen en Odoo 19. Usar siempre puntos de entrada estándar de Odoo (`action_send_and_print`) que SÍ están documentados.

## 💡 Regla de oro #21
**Auto-offset para rangos DIAN que inician en num > 1.** Si la resolución DIAN asigna rango 5001-10000 pero el SequenceMixin de Odoo empieza en 1, el código debe calcular `dian_number = min_range + (raw_number - 1)`.
