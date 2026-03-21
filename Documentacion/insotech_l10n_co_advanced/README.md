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

### Contexto Regulatorio (DIAN)

> *"Si la factura no es validada ni aceptada, se deben corregir los errores informados por la DIAN, firmar electrónicamente y transmitirla nuevamente con el mismo número. El número de consecutivo no se consume."*
> — Resolución DIAN 000042 de 2020

---

## Arquitectura del Módulo

```
insotech_l10n_co_advanced/
├── __init__.py                    # Importa models
├── __manifest__.py                # Manifiesto v19.0.1.0.0
├── data/
│   └── ir_sequence_data.xml       # Secuencia PRE-INV/YYYY/NNNNN
├── models/
│   ├── __init__.py                # Importa account_move
│   └── account_move.py           # Lógica principal (herencia account.move)
├── security/
│   └── ir.model.access.csv       # ACL (solo header, no crea modelos nuevos)
└── views/
    └── account_move_views.xml     # Banners, botones, campos ocultos
```

---

## Flujo de Secuencias — Patrón PRE-INV → Número Legal

```
           Borrador
              │
              ▼
    Confirmar (_post)
              │
    ┌─────────────────────────────────────────────┐
    │ 1. super()._post() → Odoo asigna INV/2026/01│
    │ 2. Guarda INV/2026/01 en reserved_dian_name  │
    │ 3. Renombra a PRE-INV/2026/00001             │
    │ 4. Estado → 'pending'                        │
    └──────────┬──────────────────────────────────┘
               │
      Enviar a DIAN (Print & Send)
               │
        ┌──────┴──────┐
        │             │
   Aceptada      Rechazada
        │             │
        ▼             ▼
  ┌────────────┐  ┌──────────────────┐
  │INV/2026/01 │  │ PRE-INV/2026/... │
  │(restaurado │  │ Corregir error   │
  │ de reserva)│  │ y reintentar     │
  │ ✅ Legal   │  │ ❌ Sin pérdida   │
  └────────────┘  └──────────────────┘
```

---

## Modelo: `account.move` (Herencia)

### Campos Añadidos

| Campo | Tipo | Descripción |
|---|---|---|
| `insotech_dian_status` | Selection | Estado DIAN: `not_applicable`, `pending`, `accepted`, `rejected`. Con tracking. |
| `insotech_pre_inv_name` | Char | Nombre temporal PRE-INV asignado al confirmar |
| `insotech_reserved_dian_name` | Char | Nombre legal del diario reservado por `_post()`. Se restaura al aceptar DIAN. |
| `insotech_is_co_edi` | Boolean (computed, stored) | `True` si la factura es EDI colombiana (empresa CO + diario de ventas) |

### Métodos Principales

#### `_post(soft=True)` — Override

1. Llama `super()._post()` → Odoo asigna el nombre del diario (ej. `INV/2026/00001`).
2. Guarda ese nombre en `insotech_reserved_dian_name`.
3. Genera nombre temporal con `ir.sequence` → `PRE-INV/2026/00001`.
4. Renombra la factura al nombre temporal.
5. Establece `insotech_dian_status = 'pending'`.
6. Registra en chatter con `Markup()`.

> **Importante**: Usa `skip_account_move_synchronization=True` en el contexto para evitar que el `SequenceMixin` interfiera con el cambio de nombre.

#### `_get_last_sequence_domain(relaxed=False)` — Override

**Fix crítico** para evitar contaminación del `SequenceMixin`. Agrega:

```sql
AND name NOT LIKE 'PRE-INV%'
```

Sin este override, el `SequenceMixin` ve los nombres `PRE-INV` como el patrón del diario y genera más nombres `PRE-INV` para las siguientes facturas, en vez de usar la secuencia real.

#### `_insotech_process_dian_acceptance()`

1. Lee `insotech_reserved_dian_name` → nombre legal reservado.
2. Renombra la factura al nombre legal.
3. Establece `insotech_dian_status = 'accepted'`.
4. Incrementa `insotech_usage_count` en la compañía (licencia SaaS).
5. Registra en chatter.

#### `_insotech_process_dian_rejection(error_message)`

1. Mantiene el nombre `PRE-INV` intacto.
2. Establece `insotech_dian_status = 'rejected'`.
3. Registra motivo del rechazo en chatter.
4. **No se pierde ningún consecutivo.**

#### `_compute_insotech_is_co_edi()`

Campo computado que determina si una factura es EDI colombiana verificando:
1. `move_type` es `out_invoice` o `out_refund`.
2. La empresa tiene país `CO`.
3. El diario tiene EDI DIAN habilitado (verifica múltiples campos posibles + fallback a diario de ventas CO).

### Hooks en `l10n_co_dian`

Tres métodos de intercepción que validan la licencia SaaS antes de enviar a la DIAN:
- `_l10n_co_dian_post()`
- `_l10n_co_edi_send()`
- `_hook_invoice_document_before_pdf()`

Cada uno llama `_insotech_validate_license_before_dian()` y luego delega a `super()`.

### Acciones de Usuario

| Botón | Acción | Visibilidad |
|---|---|---|
| **Reintentar Envío DIAN** | Resetea a `pending`, abre wizard de envío | Solo facturas rechazadas |
| **Forzar Aceptación DIAN** | Llama `_insotech_process_dian_acceptance()` | Solo admin contable, facturas pending/rejected |

---

## Datos: Secuencia PRE-INV

```xml
<record id="insotech_l10n_co_advanced_seq_pre_inv" model="ir.sequence">
    <field name="name">Insotech: Factura Pre-Validación DIAN</field>
    <field name="code">insotech.pre.inv</field>
    <field name="prefix">PRE-INV/%(year)s/</field>
    <field name="padding">5</field>
    <field name="number_increment">1</field>
    <field name="number_next_actual">1</field>
</record>
```

---

## Vista: `account.move` Form (Herencia)

### Hereda de: `account.view_move_form`
### Prioridad: 100

| XPath | Posición | Elemento |
|---|---|---|
| `//header` `before` | Campos ocultos | `insotech_dian_status`, `insotech_is_co_edi`, `insotech_reserved_dian_name` (invisible) |
| `//header` `after` | Banner amarillo | "Pendiente de validación DIAN" (visible si `pending`) |
| `//header` `after` | Banner rojo | "Rechazada por la DIAN" (visible si `rejected`) |
| `//header` `inside` | Botón retry | "Reintentar Envío DIAN" (visible si `rejected`) |
| `//header` `inside` | Botón forzar | "Forzar Aceptación DIAN" (admin, visible si `pending`/`rejected`) |

> **Nota Odoo 19**: Los campos ocultos se declaran **antes** del `<header>` (no dentro del `<sheet>`) para que estén disponibles en la evaluación de dominios `invisible` de los banners.

---

## Validación de Licencia SaaS

Antes de transmitir el XML a la DIAN, el módulo valida la licencia usando `insotech_core`:

```python
company._validate_and_report_license()
```

- **Licencia activa** → Permite envío a DIAN.
- **Licencia inactiva** → Bloquea envío con `UserError`. Las facturas se pueden seguir creando y confirmando.
- **Error de validación** → Se permite el envío (fail-open) para no bloquear operaciones del cliente.

---

## Logging

| Logger | Nivel | Escenario |
|---|---|---|
| `Insotech` | `INFO` | Protección activada, DIAN aceptada, nombre mutado |
| `Insotech` | `WARNING` | DIAN rechazada, admin forzó aceptación, método DIAN no encontrado |
| `Insotech` | `ERROR` | Error inesperado en protección o aceptación |

Filtro en logs de Odoo: `Insotech:`

---

## Mensajes en Chatter

Todos los mensajes usan `Markup` (de `markupsafe`) para renderizado HTML correcto:

| Evento | Emoji | Mensaje |
|---|---|---|
| Confirmación | 🔒 | **Protección de consecutivo DIAN activada** — Nombre temporal: PRE-INV/... |
| Aceptación | ✅ | **Factura aceptada por la DIAN** — Número definitivo: INV/2026/... |
| Rechazo | ❌ | **Factura rechazada por la DIAN** — Motivo: [detalle] |
| Reintento | 🔄 | **Reintento de envío a la DIAN** |

> **Nota técnica**: Se usa `Markup()` en vez de `_()` porque `_()` escapa el HTML y muestra tags crudos como `<b>` en texto plano.
