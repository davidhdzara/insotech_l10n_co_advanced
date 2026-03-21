# Changelog — insotech_core

Todos los cambios relevantes de este módulo se documentan en este archivo.

---

## [19.0.1.0.0] — 2026-03-21

### Agregado
- **Estructura del módulo**: `__init__.py`, `__manifest__.py` con dependencias `base` y `web`.
- **Modelo `res.company`**: Campos `insotech_license_token` (Char), `insotech_usage_count` (Integer), `insotech_last_successful_ping` (Datetime).
- **Modelo `res.config.settings`**: Campo `related` para exponer `insotech_license_token` en la vista de Ajustes.
- **Método `_validate_and_report_license()`**: Validación de licencia contra API REST con:
  - Envío de payload (token, NIT, URL, contador de uso).
  - Manejo de respuestas: `active`, `blocked`, `exhausted`.
  - Período de gracia de **72 horas** ante fallos de conectividad.
  - Timeout de **4 segundos** para no bloquear operaciones.
  - Logging completo con niveles `ERROR` y `WARNING`.
- **Vista de Ajustes XML**: Sección "Insotech" con bloque "Licenciamiento Insotech" usando el xpath `//form` para máxima compatibilidad con Odoo 19.

### Notas Técnicas
- El xpath `//form` con `position="inside"` y un bloque `<app>` es la forma estándar de agregar secciones a los Ajustes Generales en Odoo 19, donde la vista base es un `<form>` vacío.
- El campo `insotech_license_token` usa `copy=False` implícito a través del campo `related` en `res.config.settings`, evitando que se copie al duplicar compañías.
- Los campos `insotech_usage_count` y `insotech_last_successful_ping` tienen `copy=False` explícito para evitar transferencia de datos de licencia entre compañías.
