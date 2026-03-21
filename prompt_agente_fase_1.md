# Prompt para Implementación de la Fase 1 (Motor SaaS Insotech)

Copia y pega el siguiente texto al otro agente de desarrollo para que inicie la implementación estructural del proyecto:

***

**Actúa como un desarrollador experto de software especializado en Odoo 19 y Python.**
Tu objetivo exclusivo en esta sesión es desarrollar e implementar las tareas 1.1, 1.2 y 1.3 del proyecto "Insotech Advanced Localization", correspondientes a la creación del motor base de licenciamiento SaaS.

**Contexto de Diseño:**
Debes crear un módulo base e independiente llamado `insotech_core`. Este módulo servirá como validador para que otros submódulos funcionen.

### Requerimientos Técnicos:

**1. Estructura y Manifiesto (`insotech_core/`)**
Crea el andamio del módulo para Odoo 19. Debe contener el `__init__.py` y un `__manifest__.py` con la descripción "Insotech Core Licensing Engine", categoría técnica e instalable. Depende únicamente de `base` y `web`.

**2. Modelo de Configuración de Compañía (`insotech_core/models/res_company.py`)**
Necesitamos almacenar el token de licencia del cliente.
- Hereda el modelo `res.company`.
- Añade el campo: `insotech_license_token` (fields.Char, string="Token de Licencia Insotech").
- Hereda `res.config.settings` para que este campo sea editable en los Ajustes Generales de la empresa.

**3. Vistas (`insotech_core/views/res_config_settings_views.xml`)**
- Crea un `xpath` dentro de la vista de ajustes de Odoo (`res.config.settings.view.form`) y añade un nuevo bloque/sección llamado "Licenciamiento Insotech".
- Muestra el campo `insotech_license_token` allí para que un administrador pueda tipear su llave.

**4. El Validador API y Reporte de Uso (`insotech_core/models/insotech_license.py` o dentro de `res.company`)**
- Crea un método principal (ej. `_validate_and_report_license()`) que utilice la librería estándar `requests` de Python.
- Este método debe hacer una petición HTTP POST (con timeout máximo de 4 segundos) a:
  `https://www.insotech.it/insotech/api/v1/verify`
- El *payload* o JSON de la petición debe enviar:
   - `token`: El valor de `insotech_license_token` de la compañía.
   - `vat`: El NIT (`vat`) de la compañía local.
   - `url`: La URL base de la base de datos de Odoo.
   - `usage_count`: Un entero numérico con la cantidad de facturas emitidas desde el último "ping" exitoso. (Debes crear un campo numérico oculto en `res.company` que actué como contador temporal).
   - `reset_counter`: Un booleano.

- **Manejo de Respuestas (Período de Gracia):**
  - Si la API responde `HTTP 200` y `{"status": "active"}`, el método retorna `True`. (Aquí debes reiniciar el `usage_count` local a cero y guardar la fecha actual en un campo `last_successful_ping`).
  - Si la API responde con código `Error 40X/50X`, Timeout o Fallo de Red: El sistema **NO DEBE BLOQUEARSE INMEDIATAMENTE**. Debe calcular si han pasado menos de 72 horas desde el `last_successful_ping`. Si es así, retorna `True` (Período de gracia por si `insotech.it` está caído). Si han pasado más de 72 horas sin internet/conexión, retorna `False` (Bloqueo).
  - Si la API responde `{"status": "blocked"}` o `{"status": "exhausted"}`, retorna `False` sin importar el período de gracia.

**Instrucción de Calidad:**
No intentes aplicar ofuscación de código, Pyarmor o compilación en Cython en este paso. Escribe código de la calidad de la OCA, en texto plano, aplicando buenas prácticas de `try/except` para que Odoo no se caiga si `insotech.it` está fuera de línea.

***
