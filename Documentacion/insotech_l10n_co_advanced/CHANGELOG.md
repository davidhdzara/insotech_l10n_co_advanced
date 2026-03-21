# Changelog — insotech_l10n_co_advanced

Todos los cambios relevantes de este módulo se documentan en este archivo.

---

## [19.0.1.0.0] — 2026-03-21

### Añadido
- **Protección de consecutivos DIAN**: Secuencia temporal `PRE-INV/YYYY/NNNNN` al confirmar facturas EDI colombianas.
- **Campo `insotech_reserved_dian_name`**: Almacena el nombre legal del diario asignado por `_post()` antes de renombrar a PRE-INV. Se restaura cuando la DIAN acepta.
- **Campo `insotech_dian_status`**: Tracking del estado DIAN con valores `not_applicable`, `pending`, `accepted`, `rejected`.
- **Campo `insotech_pre_inv_name`**: Nombre temporal PRE-INV para referencia.
- **Campo `insotech_is_co_edi`**: Computado, determina si la factura es EDI colombiana.
- **Override `_get_last_sequence_domain()`**: Excluye nombres `PRE-INV%` del `SequenceMixin` para evitar contaminación del patrón de secuencia del diario.
- **Override `_post()`**: Intercepta la confirmación para proteger consecutivos DIAN.
- **Método `_insotech_process_dian_acceptance()`**: Mutación de PRE-INV a nombre legal al recibir aceptación DIAN.
- **Método `_insotech_process_dian_rejection()`**: Manejo de rechazo DIAN sin perder consecutivo.
- **Banner amarillo**: "Pendiente de validación DIAN" visible mientras la factura espera respuesta.
- **Banner rojo**: "Rechazada por la DIAN" con instrucciones de corrección.
- **Botón "Reintentar Envío DIAN"**: Permite reenviar facturas rechazadas sin crear nuevas.
- **Botón "Forzar Aceptación DIAN"**: Acción de emergencia para administradores contables.
- **Secuencia `ir.sequence`**: `insotech.pre.inv` con prefijo `PRE-INV/%(year)s/` y padding de 5 dígitos.
- **Validación de licencia SaaS**: Bloquea envío a DIAN (no la confirmación) si la licencia Insotech no está activa.
- **Mensajes chatter con `Markup`**: HTML renderizado correctamente (negritas, emojis, saltos de línea).
- **Hooks en `l10n_co_dian`**: Tres puntos de intercepción para validación de licencia antes del envío DIAN.
- **Logging completo**: Trazabilidad en logs del servidor con prefijo `Insotech:`.

### Fixes de Despliegue (durante implementación inicial)
- **Profundidad de submódulo**: El submódulo creaba ruta de 2 niveles no descubrible por Odoo.sh. Se cambió a copia directa en raíz del repo.
- **XPath inexistente**: `//page[@name='other_info']//group[@name='accounting_info']` no existe en Odoo 19. Reemplazado por `//header position="before"`.
- **Banner no visible**: Campos declarados dentro del `<sheet>` pero referenciados fuera. Movidos a `//header position="before"`.
- **Contaminación del SequenceMixin**: El SequenceMixin veía nombres PRE-INV y derivaba el patrón de secuencia incorrecto. Solucionado con override de `_get_last_sequence_domain()`.
- **Chatter con HTML crudo**: `_()` escapaba el HTML. Reemplazado por `Markup()` de `markupsafe`.

### Notas Técnicas
- Compatible con Odoo 19 Enterprise + localización colombiana (`l10n_co_dian`).
- Usa approach defensivo para compatibilidad: verifica múltiples nombres de método de `l10n_co_dian`.
- No modifica código nativo de Odoo ni de `insotech_core`.
- El `SequenceMixin` de Odoo 19 usa `_get_last_sequence_domain()` internamente. Nuestro override añade `AND name NOT LIKE 'PRE-INV%'` para proteger la integridad de la secuencia del diario.
- Los campos invisibles deben declararse **antes** del `<header>` en la vista XML para que estén disponibles en los dominios `invisible` de los banners.
