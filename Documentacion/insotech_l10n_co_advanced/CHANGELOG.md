# Changelog — insotech_l10n_co_advanced

## [19.0.1.0.0] — 2026-03-21

### Añadido
- **Protección de consecutivos DIAN**: Secuencia temporal `PRE-INV/YYYY/NNNNN` al confirmar facturas EDI colombianas.
- **Mutación a secuencia legal**: Asignación automática del número definitivo de resolución DIAN tras aceptación (`FE-XXX`).
- **Manejo de rechazo DIAN**: Las facturas rechazadas conservan el nombre temporal. El usuario corrige y reintenta sin perder consecutivos.
- **Validación de licencia SaaS**: Bloqueo de envío a DIAN si la licencia Insotech no está activa (vía `insotech_core`).
- **Banner de estado DIAN**: Alertas visuales en la vista de factura (pendiente / rechazada).
- **Botón "Reintentar Envío DIAN"**: Permite reenviar facturas rechazadas sin crear facturas nuevas.
- **Botón "Forzar Aceptación DIAN"**: Acción de emergencia para administradores contables.
- **Secuencia `ir.sequence`**: `insotech.pre.inv` para numeración temporal con padding de 5 dígitos.
- **Campo `insotech_dian_status`**: Tracking del estado DIAN con valores `pending`, `accepted`, `rejected`.
- **Logging completo**: Mensajes en chatter y logs del servidor para trazabilidad.

### Notas Técnicas
- Compatible con Odoo 19 Enterprise + localización colombiana (`l10n_co_dian`).
- Usa approach defensivo para compatibilidad: verifica múltiples nombres de método de `l10n_co_dian`.
- No modifica código nativo de Odoo ni de `insotech_core`.
