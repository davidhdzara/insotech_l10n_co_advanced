# Guía de Migración: Odoo 19 → Odoo 18

> **Objetivo**: Este documento lista todo lo que debe verificarse y probablemente cambiarse al portar `insotech_l10n_co_advanced` de Odoo 19 a Odoo 18.

---

## 1. Investigación Obligatoria Antes de Codificar

Antes de tocar código, abre una instancia Odoo 18 con `l10n_co_dian` instalado y verifica estos puntos en `Ajustes → Técnico → Estructura de la BD → Modelos`:

### 1.1 Campos en `account.journal` (filtrar por `l10n_co`)

En Odoo 19 encontramos:
| Campo v19 | Tipo | ¿Existe en v18? |
|---|---|---|
| `l10n_co_dian_provider` | Selection | **VERIFICAR** — puede tener otro nombre o no existir |
| `l10n_co_dian_technical_key` | Char | VERIFICAR |
| `l10n_co_edi_dian_authorization_number` | Char | VERIFICAR |
| `l10n_co_edi_dian_authorization_date` | Date | VERIFICAR |
| `l10n_co_edi_dian_authorization_end_date` | Date | VERIFICAR |
| `l10n_co_edi_min_range_number` | Integer | VERIFICAR |
| `l10n_co_edi_max_range_number` | Integer | VERIFICAR |

> **Impacto**: El método `_insotech_check_journal_dian_enabled()` depende de `l10n_co_dian_provider`. Si en v18 el campo se llama diferente, debe actualizarse.

### 1.2 Campos en `account.move` (filtrar por `l10n_co`)

En Odoo 19 encontramos:
| Campo v19 | ¿Existe en v18? |
|---|---|
| `l10n_co_edi_cufe_cude_ref` | VERIFICAR |
| `l10n_co_edi_type` | VERIFICAR |
| `l10n_co_edi_operation_type` | VERIFICAR |
| `l10n_co_edi_transaction` | VERIFICAR |
| `l10n_co_edi_attachment_url` | VERIFICAR |

### 1.3 Modelo `account.edi.document`

| Pregunta | v19 | v18 |
|---|---|---|
| ¿Existe el modelo? | ✅ Sí | **VERIFICAR** — en v18 puede existir o puede estar fusionado en otro modelo |
| Campo `state` | Selection | VERIFICAR valores posibles |
| Campo `error` | HTML | VERIFICAR |
| Campo `edi_format_name` | Char | VERIFICAR |

> **Impacto crítico**: Si `account.edi.document` no existe en v18 o su estructura es diferente, el hook automático (`account_edi_document.py`) debe adaptar su estrategia.

---

## 2. Diferencias Conocidas de Arquitectura

### 2.1 Sistema de Secuencias

| Aspecto | Odoo 19 | Odoo 18 (probable) |
|---|---|---|
| Asignación de name en facturas | `SequenceMixin._compute_name()` | Posiblemente `ir.sequence` clásico |
| `_get_last_sequence_domain()` | Existe, lo override-amos | **VERIFICAR** si existe |
| `ir.sequence` para diarios | NO se usa | **Posiblemente SÍ** se usa |

#### Si Odoo 18 usa `ir.sequence`:
- El override de `_get_last_sequence_domain()` probablemente no aplica.
- La estrategia de protección podría cambiar: en vez de guardar el nombre y renombrar, podría ser viable **interceptar el consumo del `ir.sequence`** directamente (decrementando `number_next_actual` después del `_post()`).
- Investigar si `journal.sequence_id` existe y apunta al `ir.sequence` del diario.

### 2.2 Método de Confirmación

| Aspecto | Odoo 19 | Odoo 18 |
|---|---|---|
| Método | `_post(soft=True)` | **VERIFICAR**: ¿`_post()`? ¿`action_post()`? |
| Parámetro `soft` | Existe | VERIFICAR |

> **Cómo verificar**: Buscar `def _post` o `def action_post` en el código fuente de `account.move` en v18.

### 2.3 Proveedor DIAN

| Aspecto | Odoo 19 | Odoo 18 |
|---|---|---|
| Conexión DIAN | Directa (exclusivamente) | Puede incluir Carvajal como intermediario |
| Módulo | `l10n_co_dian` | **VERIFICAR**: ¿mismo nombre? ¿existe `l10n_co_edi_carvajal`? |

> **Impacto**: Si v18 usa Carvajal, el procesamiento de respuesta puede ser diferente. Los hooks de licencia (`_l10n_co_dian_post`, `_l10n_co_edi_send`) podrían tener nombres distintos.

### 2.4 Vistas XML

| Aspecto | Odoo 19 | Odoo 18 |
|---|---|---|
| Campos invisibles antes del header | `//header position="before"` | **VERIFICAR** si funciona igual |
| XPath de pestaña "Otra Información" | `//page[@name='other_info']` no existe | **VERIFICAR** si existe en v18 |
| Widget de banners | `alert alert-warning` | **VERIFICAR** compatibilidad |

---

## 3. Checklist de Migración

### Fase 1: Investigación (sin tocar código)
- [ ] Instalar Odoo 18 con `l10n_co_dian`
- [ ] Verificar campos de `account.journal` (tabla 1.1)
- [ ] Verificar campos de `account.move` (tabla 1.2)
- [ ] Verificar existencia y campos de `account.edi.document` (tabla 1.3)
- [ ] Verificar si `_post()` o `action_post()` es el método correcto
- [ ] Verificar si Odoo 18 usa `SequenceMixin` o `ir.sequence` para facturas
- [ ] Verificar si existe `_get_last_sequence_domain()`
- [ ] Verificar nombres de módulos DIAN (`l10n_co_dian`, `l10n_co_edi`, `l10n_co_edi_carvajal`)
- [ ] Documentar hallazgos en la cabecera del nuevo `account_move.py`

### Fase 2: Adaptación de código
- [ ] Actualizar `__manifest__.py` → versión `18.0.1.0.0`, dependencias
- [ ] Adaptar `_insotech_check_journal_dian_enabled()` con campos de v18
- [ ] Adaptar override de `_post()` (o `action_post()`)
- [ ] Adaptar o reescribir fix del SequenceMixin
- [ ] Adaptar hook en `account.edi.document` (o buscar alternativa)
- [ ] Adaptar hooks de licencia (nombres de métodos de envío DIAN)
- [ ] Verificar XPaths de la vista XML

### Fase 3: Testing
- [ ] Crear factura → verificar PRE-INV
- [ ] Enviar a DIAN (modo test) → verificar hook automático
- [ ] Verificar rechazo DIAN → PRE-INV se mantiene
- [ ] Verificar aceptación DIAN → nombre restaurado
- [ ] Verificar que SequenceMixin no se contamina

---

## 4. Lo que NO cambia entre versiones

Estos elementos son independientes de la versión y se reutilizan directamente:

- **Lógica de negocio**: Patrón PRE-INV → nombre legal
- **Campo `insotech_reserved_dian_name`**: Siempre se necesita
- **Secuencia `ir.sequence` PRE-INV**: `insotech.pre.inv`
- **Validación de licencia**: `insotech_core._validate_and_report_license()`
- **Mensajes de chatter**: Emojis y formato con `Markup`
- **Banners de estado**: Concepto y diseño visual
- **Logging**: Prefijo `Insotech:` y niveles

---

## 5. Riesgos Específicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| `account.edi.document` no existe en v18 | Media | Alto | Buscar modelo alternativo o usar `write()` en `account.move` directamente |
| `SequenceMixin` funciona diferente | Alta | Alto | Re-investigar cómo v18 asigna secuencias |
| Carvajal como intermediario en v18 | Media | Medio | Los hooks de licencia deben interceptar el método de Carvajal |
| XPaths incompatibles | Baja | Bajo | Probar la vista en v18 antes de desplegar |
| Nombre de `_post()` diferente | Media | Alto | Búsqueda en código fuente de v18 |
