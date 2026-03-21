# Changelog — insotech_l10n_co_advanced

Todos los cambios relevantes de este módulo se documentan en este archivo.

---

## [19.0.1.0.0] — 2026-03-21

### Añadido
- **Protección de consecutivos DIAN**: Secuencia temporal `PRE-INV/YYYY/NNNNN` al confirmar facturas EDI colombianas.
- **Campo `insotech_reserved_dian_name`**: Almacena el nombre legal del diario asignado por `_post()` antes de renombrar a PRE-INV. Se restaura cuando la DIAN acepta.
- **Campo `insotech_dian_status`**: Tracking del estado DIAN (`not_applicable`, `pending`, `accepted`, `rejected`).
- **Campo `insotech_pre_inv_name`**: Nombre temporal PRE-INV para referencia.
- **Campo `insotech_is_co_edi`**: Computado, determina si la factura es EDI colombiana.
- **Override `_get_last_sequence_domain()`**: Excluye `PRE-INV%` del SequenceMixin para evitar contaminación del patrón de secuencia.
- **Override `_post()`**: Intercepta la confirmación para proteger consecutivos DIAN.
- **Hook automático `account.edi.document`**: Override de `write()` que detecta cuando `l10n_co_dian` procesa la respuesta DIAN. Llama automáticamente `_insotech_process_dian_acceptance()` o `_insotech_process_dian_rejection()`.
- **Banner amarillo**: "Pendiente de validación DIAN" visible mientras la factura espera respuesta.
- **Banner rojo**: "Rechazada por la DIAN" con instrucciones de corrección.
- **Botón "Reintentar Envío DIAN"**: Permite reenviar facturas rechazadas sin crear nuevas.
- **Botón "Forzar Aceptación DIAN"**: Acción de emergencia para administradores contables.
- **Secuencia `ir.sequence`**: `insotech.pre.inv` con prefijo `PRE-INV/%(year)s/` y padding de 5 dígitos.
- **Validación de licencia SaaS**: Bloquea envío a DIAN (no la confirmación) si la licencia Insotech no está activa.
- **Mensajes chatter con `Markup`**: HTML renderizado correctamente (negritas, emojis, saltos de línea).
- **Hooks en `l10n_co_dian`**: Tres puntos de intercepción para validación de licencia antes del envío DIAN.
- **Logging completo**: Trazabilidad en logs del servidor con prefijo `Insotech:`.

### Investigación de Campos Odoo 19 (verificada en staging)

#### Campos `l10n_co_dian` en `account.journal`
| Campo | Tipo | Descripción |
|---|---|---|
| `l10n_co_dian_provider` | Selection | Proveedor DIAN (campo principal de activación) |
| `l10n_co_dian_technical_key` | Char | Clave técnica de la resolución |
| `l10n_co_edi_dian_authorization_number` | Char | Número de resolución |
| `l10n_co_edi_dian_authorization_date` | Date | Fecha inicio resolución |
| `l10n_co_edi_dian_authorization_end_date` | Date | Fecha fin resolución |
| `l10n_co_edi_min_range_number` | Integer | Número inicial autorizado |
| `l10n_co_edi_max_range_number` | Integer | Número final autorizado |

#### Campos `l10n_co_edi` en `account.move`
| Campo | Tipo | Descripción |
|---|---|---|
| `l10n_co_edi_cufe_cude_ref` | Char | CUFE/CUDE/CUDS |
| `l10n_co_edi_type` | Selection | Tipo de Documento |
| `l10n_co_edi_operation_type` | Selection | Tipo de operación |
| `l10n_co_edi_transaction` | Char | ID de transacción |

#### Campos de `account.edi.document`
| Campo | Tipo | Descripción |
|---|---|---|
| `state` | Selection | Estado EDI (`to_send` → `sent` = aceptada) |
| `error` | HTML | Mensaje de error DIAN |
| `move_id` | Many2one | Factura vinculada |
| `edi_format_name` | Char | Nombre del formato EDI |

### Fixes de Despliegue (durante implementación inicial)
- **Profundidad de submódulo**: Ruta de 2 niveles no descubrible por Odoo.sh → copia directa.
- **XPath inexistente en Odoo 19**: `//page[@name='other_info']//group[@name='accounting_info']` → `//header position="before"`.
- **Banner no visible**: Campos declarados dentro del `<sheet>` → movidos a `//header position="before"`.
- **Contaminación del SequenceMixin**: PRE-INV como patrón de secuencia → override de `_get_last_sequence_domain()`.
- **Chatter con HTML crudo**: `_()` escapaba HTML → `Markup()` de `markupsafe`.
- **Detección de diarios demasiado amplia**: Fallback `journal.type == 'sale'` → campos reales `l10n_co_dian_provider`.

### Notas Técnicas
- Compatible con Odoo 19 Enterprise + localización colombiana (`l10n_co_dian`).
- Odoo 19.1 usa exclusivamente conexión directa con DIAN (sin Carvajal).
- Odoo 19 NO usa `ir.sequence` para `account.move`. Las secuencias se computan internamente via `SequenceMixin._compute_name()`.
- Los campos invisibles en vistas XML deben declararse **antes** del `<header>` para estar disponibles en dominios `invisible`.
- El hook en `account.edi.document` no bloquea la aceptación DIAN si falla. Es fail-safe.
