# PRE-INV enviado a la DIAN en vez del nombre real (FAD05a/b/c)

- **Fecha:** 2026-03-23
- **Módulo:** `insotech_l10n_co_advanced`
- **Contexto:** Primera factura real en producción — errores FAD05a/b/c
- **Severidad:** 🔴 Bloqueante → ✅ Resuelto

## Síntomas

```
FAD05a: Número de factura contiene caracteres adicionales como espacios o guiones
FAD05b: Número de factura inferior al inicial del rango autorizado
FAD05c: Número de factura superior al final del rango otorgado
```

## Causa Raíz

**Problema 1:** `_post()` renombra la factura de `FE/2026/00001` a `PRE-INV/2026/00001` ANTES de que `l10n_co_dian` lea `move.name` para generar el XML. La DIAN recibe `PRE-INV/2026/00001` como `<cbc:ID>`.

**Problema 2:** El `sequence_prefix` del diario genera `FE/2026/00001` (con barras y año), pero DIAN espera `FE1` (prefijo + número, sin separadores).

## Solución

### Fix de código (account_move.py)
Agregados dos métodos helper de swap de nombre:
- `_insotech_swap_to_dian_name()` — restaura `insotech_reserved_dian_name` como `move.name` antes de la generación del XML
- `_insotech_swap_to_pre_inv_name()` — restaura PRE-INV si el envío falla

Los hooks DIAN (`_l10n_co_dian_post`, `_l10n_co_edi_send`, `_hook_invoice_document_before_pdf`) ahora:
1. Swap a nombre real DIAN antes de `super()`
2. Si excepción → swap de vuelta a PRE-INV

`_insotech_process_dian_rejection()` ahora restaura PRE-INV explícitamente.

### Fix de configuración (manual en producción)
El `sequence_prefix` del diario debe configurarse para NO incluir `/%(year)s/`. Editar la referencia de la última factura confirmada para que siga el formato `{Prefijo}{Número}` (ej: `FE1`).

## 💡 Regla de oro #18
**Nunca enviar un nombre temporal (PRE-INV) a la DIAN.** Los hooks de envío deben SIEMPRE restaurar el nombre real antes de llamar `super()`.

## 💡 Regla de oro #19
**El formato del `sequence_prefix` del diario DIAN debe ser solo el prefijo sin separadores.** DIAN espera `{Prefijo}{Número}` (FE1, FEI23, FEGU500), no `FE/2026/00001`.
