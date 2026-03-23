# Insotech — Localización Colombiana Avanzada

## Descripción General

Módulo para Odoo 19 Enterprise que extiende la localización nativa colombiana (`l10n_co_dian`) para **proteger los consecutivos de resolución DIAN** contra rechazos técnicos y errores de datos.

- **Nombre técnico**: `insotech_l10n_co_advanced`
- **Versión**: 19.0.1.0.0
- **Categoría**: Accounting/Localizations
- **Licencia**: OPL-1 (Propietaria)
- **Dependencias**: `account`, `l10n_co_edi`, `l10n_co_dian`, `insotech_core`
- **Autor**: Insotech

---

## Problema que Resuelve

Cuando Odoo confirma una factura, el `SequenceMixin` asigna inmediatamente el siguiente consecutivo de la resolución DIAN (ej. `INV/2026/00001`). Si la DIAN rechaza el XML por cualquier error (NIT inválido, correo mal formado, etc.), ese número **se pierde**. Esto crea huecos en la numeración legal que la DIAN puede sancionar.

---

## Arquitectura del Módulo

```
insotech_l10n_co_advanced/
├── __init__.py                    # Importa models
├── __manifest__.py                # Manifiesto v19.0.1.1.0
├── data/
│   └── ir_sequence_data.xml       # Secuencia PRE-INV/YYYY/NNNNN
├── models/
│   ├── __init__.py                # Importa account_move + account_edi_document + account_journal
│   ├── account_move.py            # Lógica principal (herencia account.move)
│   ├── account_edi_document.py    # Hook automático de respuesta DIAN
│   └── account_journal.py         # Validación de formato secuencia DIAN
├── security/
│   └── ir.model.access.csv        # ACL (solo header)
└── views/
    ├── account_move_views.xml      # Banners, botones, campos ocultos
    └── account_journal_views.xml   # Desactivación de vista legacy
```

---

## Flujo de Secuencias — Patrón PRE-INV → Número Legal

```
           Borrador
              │
              ▼
    Confirmar (_post)
              │
    ┌────────────────────────────────────────────────┐
    │ 1. Verifica l10n_co_dian_provider en el diario │
    │ 2. super()._post() → Odoo asigna FE/2026/0001 │
    │ 3. Guarda FE/2026/0001 en reserved_dian_name   │
    │ 4. Renombra a PRE-INV/2026/00001               │
    │ 5. Estado → 'pending'                          │
    └──────────┬─────────────────────────────────────┘
               │
      Enviar a DIAN (botón "Enviar")
               │
    ┌────────────────────────────────────────────────┐
    │ SWAP: PRE-INV/2026/00001 → FE1                │
    │ (lee journal.code + extrae número + offset)    │
    │ l10n_co_dian genera XML con <cbc:ID>FE1</…>    │
    └──────────┬─────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   Aceptada      Rechazada
   (automático)  (automático)
        │             │
        ▼             ▼
  ┌────────────┐  ┌──────────────────┐
  │   FE1      │  │ PRE-INV/2026/... │
  │(DIAN name  │  │ (restaurado)     │
  │ se queda)  │  │ Corregir error   │
  │ ✅ Legal   │  │ y reintentar     │
  └────────────┘  │ ❌ Sin pérdida   │
                  └──────────────────┘
```

---

## Detección de Diarios EDI Colombianos

El módulo **solo interviene** en diarios que tienen configuración DIAN activa. La detección usa los campos reales de Odoo 19 Enterprise (verificados en staging 2026-03-21):

### Campos verificados en `account.journal`

| Campo | Tipo | Descripción |
|---|---|---|
| `l10n_co_dian_provider` | Selection | **Proveedor DIAN** — campo principal de activación |
| `l10n_co_edi_dian_authorization_number` | Char | Número de resolución DIAN |
| `l10n_co_edi_dian_authorization_date` | Date | Fecha inicio resolución |
| `l10n_co_edi_dian_authorization_end_date` | Date | Fecha fin resolución |
| `l10n_co_edi_min_range_number` | Integer | Primer número autorizado |
| `l10n_co_edi_max_range_number` | Integer | Último número autorizado |
| `l10n_co_dian_technical_key` | Char | Clave técnica de la resolución |

### Lógica de detección

```python
# 1. Verificación primaria: ¿Tiene proveedor DIAN configurado?
if journal.l10n_co_dian_provider:
    return True  # ✅ Intervenir

# 2. Verificación secundaria: ¿Tiene resolución DIAN?
if journal.l10n_co_edi_dian_authorization_number:
    return True  # ✅ Intervenir

# Si ninguna condición se cumple → NO intervenir
return False
```

> **Nota**: Si el diario NO tiene DIAN configurado, la factura fluye normalmente sin PRE-INV. La protección se activa automáticamente al configurar la resolución DIAN en el diario.

---

## Modelo: `account.move` (Herencia)

### Campos Añadidos

| Campo | Tipo | Descripción |
|---|---|---|
| `insotech_dian_status` | Selection | Estado DIAN: `not_applicable`, `pending`, `accepted`, `rejected`. Con tracking. |
| `insotech_pre_inv_name` | Char | Nombre temporal PRE-INV asignado al confirmar |
| `insotech_reserved_dian_name` | Char | Nombre legal del diario reservado por `_post()`. Se restaura al aceptar DIAN. |
| `insotech_is_co_edi` | Boolean (computed, stored) | `True` si la factura es EDI colombiana |

### Métodos Principales

#### `_post(soft=True)` — Override

1. Llama `super()._post()` → Odoo asigna el nombre del diario (ej. `INV/2026/00001`).
2. Guarda ese nombre en `insotech_reserved_dian_name`.
3. Genera nombre temporal con `ir.sequence` → `PRE-INV/2026/00001`.
4. Renombra la factura al nombre temporal.
5. Establece `insotech_dian_status = 'pending'`.

#### `_get_last_sequence_domain(relaxed=False)` — Override

**Fix crítico** para evitar contaminación del `SequenceMixin`. Agrega `AND name NOT LIKE 'PRE-INV%'` al SQL. Sin esto, el SequenceMixin ve los nombres PRE-INV como el patrón del diario y genera más nombres PRE-INV en lugar de la secuencia real.

#### `_insotech_process_dian_acceptance()`

Computa el nombre DIAN-compliant (`FE1`) usando `_insotech_compute_dian_compliant_name()` y lo establece como nombre definitivo. Incrementa `insotech_usage_count`.

#### `_insotech_process_dian_rejection(error_message)`

Restaura el nombre PRE-INV (desde `insotech_pre_inv_name`). Registra el error en chatter. El consecutivo DIAN **no se pierde**.

#### `_insotech_compute_dian_compliant_name()`

Transforma el nombre reservado de Odoo al formato DIAN:
- Lee prefijo de `journal.code` (dinámico: FE, FEI, FEGU, NC, ND, DS…)
- Extrae el número trailing del nombre reservado
- **Auto-offset**: si `raw_number < min_range`, calcula `min_range + (raw_number - 1)`
- **Validación**: si `dian_number > max_range`, lanza `UserError` (resolución agotada)

Ejemplos:
| Nombre reservado | `journal.code` | Rango | Resultado |
|---|---|---|---|
| `FE/2026/00001` | `FE` | 1–5000 | `FE1` |
| `FE/2026/00003` | `FEGU` | 5001–10000 | `FEGU5003` |
| `FEI/2026/00500` | `FEI` | 1–500 | `FEI500` |
| `FE/2026/05001` | `FE` | 1–5000 | `UserError` ⚠️ |

#### `_insotech_swap_to_dian_name()`

Swap temporal: renombra `move.name` de PRE-INV al nombre DIAN-compliant antes de que `l10n_co_dian` genere el XML. Solo actúa si `insotech_dian_status == 'pending'`.

#### `_insotech_swap_to_pre_inv_name()`

Restaura el nombre PRE-INV si el envío a DIAN falla con excepción.

---

## Modelo: `account.journal` (Herencia)

### Métodos Añadidos

#### `_insotech_get_dian_prefix()`

Retorna `journal.code` como prefijo DIAN (dinámico por cliente).

#### `_insotech_check_dian_sequence_format()`

Valida que el formato de secuencia del diario sea DIAN-compatible. Detecta si el último move tiene `/` en su nombre y genera warning. No bloquea.

#### `_insotech_is_dian_enabled()`

Verifica si el diario tiene configuración DIAN activa (reutilizable).

---

## Modelo: `account.edi.document` (Herencia) — Hook Automático DIAN

### Propósito

Detectar automáticamente cuando `l10n_co_dian` procesa la respuesta de la DIAN y llamar los métodos de aceptación/rechazo sin intervención manual.

### Campos monitoreados (verificados en staging)

| Campo | Tipo | Rol |
|---|---|---|
| `state` | Selection | Estado del documento EDI (`to_send` → `sent` = aceptado) |
| `error` | HTML | Mensaje de error DIAN |
| `move_id` | Many2one | Referencia a la factura |
| `edi_format_id` | Many2one | Formato EDI |
| `edi_format_name` | Char | Nombre del formato (para filtrar por DIAN) |
| `blocking_level` | Selection | Nivel de bloqueo |

### Lógica del hook (`write()` override)

```python
# Cuando l10n_co_dian actualiza account.edi.document:
if state cambia a 'sent':
    → move_id._insotech_process_dian_acceptance()
    
if error se llena por primera vez (y state != 'sent'):
    → move_id._insotech_process_dian_rejection(error_message)
```

### Filtro de formato DIAN

Solo procesa documentos EDI cuyo `edi_format_name` contenga: `colombia`, `dian`, `ubl 2.1`, o `co `.

### Fail-safe

Si el hook falla, **no bloquea** la aceptación DIAN. El administrador puede usar el botón "Forzar Aceptación DIAN" como respaldo.

---

## Vista: `account.move` Form (Herencia)

| XPath | Elemento |
|---|---|
| `//header before` | Campos ocultos: `insotech_dian_status`, `insotech_is_co_edi`, `insotech_reserved_dian_name` |
| `//header after` | Banner amarillo: "Pendiente de validación DIAN" |
| `//header after` | Banner rojo: "Rechazada por la DIAN" |
| `//header inside` | Botón "Reintentar Envío DIAN" (rechazadas) |
| `//header inside` | Botón "Forzar Aceptación DIAN" (admin, pending/rejected) |

> **Odoo 19**: Campos ocultos se declaran **antes** del `<header>` para disponibilidad en dominios `invisible`.

---

## Validación de Licencia SaaS

Antes de transmitir el XML a la DIAN, valida la licencia usando `insotech_core._validate_and_report_license()`. Bloquea envío, no confirmación. Fail-open ante errores de validación.

---

## Mensajes en Chatter

Todos usan `Markup` (markupsafe) para renderizado HTML correcto:

| Evento | Emoji | Mensaje |
|---|---|---|
| Confirmación | 🔒 | Protección de consecutivo DIAN activada |
| Aceptación | ✅ | Factura aceptada por la DIAN — Número definitivo: INV/... |
| Rechazo | ❌ | Factura rechazada por la DIAN — Motivo: [detalle] |
| Reintento | 🔄 | Reintento de envío a la DIAN |

> Se usa `Markup()` en vez de `_()` porque `_()` escapa el HTML.

---

## Logging

Prefijo en logs: `Insotech:`

| Nivel | Escenario |
|---|---|
| `INFO` | Protección activada, DIAN aceptada, nombre mutado |
| `WARNING` | DIAN rechazada, admin forzó aceptación, método no encontrado |
| `ERROR` | Error inesperado en protección, aceptación o hook |
| `DEBUG` | Detección de diarios DIAN (activado/desactivado) |
