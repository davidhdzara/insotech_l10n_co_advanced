# Prompt para Implementación de la Fase 3: Servidor API SaaS (`insotech_saas_server`)

Copia y pega el siguiente texto al agente de desarrollo:

***

**Actúa como un desarrollador experto de Odoo 19 Enterprise especializado en controllers HTTP, modelos de suscripción, y APIs REST.**

Tu objetivo es construir el módulo `insotech_saas_server` que vive **exclusivamente** en el repositorio privado de Odoo.sh de Insotech. Este módulo es el servidor que recibe las peticiones de validación de licencia de todos los clientes y partners que usan los módulos Insotech.

---

## PASO 0 — OBLIGATORIO: LEE ANTES DE ESCRIBIR CÓDIGO

Lee estos archivos en orden. Contienen el contexto de negocio y la arquitectura:

1. `Documentacion/Información base/06_Estrategia_SaaS_Odoo_SH.md` — Los 3 modelos comerciales (Interno, Partner, Pay-per-use).
2. `Documentacion/insotech_core/README.md` — Cómo funciona el lado cliente: payload, respuesta esperada, grace period.
3. `insotech_core/models/res_company.py` — El código que ENVÍA las peticiones. Tu módulo va a RECIBIRLAS.
4. `Documentacion/aprendizajes/odoo_sh_deployment.md` — Reglas de despliegue en Odoo.sh.

Todos los archivos están en: `/home/david/odoo-projects/insotech_l10n_co_advanced/`

---

## CONTEXTO

### Repositorios del proyecto

| Repo | Uso | Visibilidad |
|---|---|---|
| `davidhdzara/insotech_l10n_co_advanced` | Producto (módulos que van al cliente) | GitHub público |
| `davidhdzara/insotech` | Odoo.sh de Insotech (ERP propio) | **Privado** |

**Tu código va en `davidhdzara/insotech`, NUNCA en el repo del producto.**

### Lo que ya existe en el lado CLIENTE

El módulo `insotech_core` (ya instalado en los Odoos de los clientes) envía un POST así:

```
POST https://www.insotech.it/insotech/api/v1/verify
Content-Type: application/json

{
    "token": "INS-2026-ABC123",
    "vat": "901234567",
    "url": "https://cliente.odoo.com",
    "usage_count": 42,
    "reset_counter": true
}
```

Y espera una respuesta así:
```json
{ "status": "active" }
```

Valores posibles de `status`:
- `active` — Licencia válida, puede emitir facturas.
- `blocked` — Licencia bloqueada (no pagó, suspendida).
- `exhausted` — Límite de facturas alcanzado (solo para pay-per-use).

**Timeout del cliente: 4 segundos.** Tu Controller debe responder en menos de 4s.

---

## PASOS GIT (Ejecutar primero)

Antes de crear el módulo, prepara la rama de desarrollo:

```bash
# 1. Ir al repo de Odoo.sh
cd /home/david/odoo-projects/insotech

# 2. Traer lo último de producción
git fetch origin
git checkout produccion
git pull origin produccion

# 3. Crear rama de desarrollo
git checkout -b dev-saas-server

# 4. Push para crear la rama en Odoo.sh
git push origin dev-saas-server
```

> **Nota:** Si la rama `produccion` no existe o se llama diferente, pregunta al usuario cuál es la rama principal de Odoo.sh.

---

## TAREAS A IMPLEMENTAR

### Tarea 3.2 — Modelo `insotech.license`

Crea el módulo `insotech_saas_server/` en la raíz del repo de Odoo.sh con esta estructura:

```
insotech_saas_server/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── license_api.py              ← Controller HTTP (/verify + /health)
├── models/
│   ├── __init__.py
│   ├── insotech_license.py         ← Modelo de licencia
│   └── insotech_license_log.py     ← Modelo de auditoría (cada ping)
├── security/
│   ├── ir.model.access.csv
│   └── insotech_security.xml       ← Grupos de acceso
├── views/
│   ├── insotech_license_views.xml  ← Formulario y lista de licencias
│   └── insotech_license_log_views.xml ← Vista de logs de auditoría
├── data/
│   ├── ir_cron_data.xml            ← Cron de verificación + purge logs
│   └── demo_data.xml               ← Licencias demo para testing
```

**`__manifest__.py`:**
```python
{
    'name': 'Insotech SaaS License Server',
    'version': '19.0.1.0.0',
    'category': 'Technical Settings',
    'summary': 'Servidor de licenciamiento SaaS para módulos Insotech',
    'author': 'Insotech',
    'website': 'https://www.insotech.it',
    'depends': ['base', 'contacts', 'sale_subscription'],
    'data': [
        'security/insotech_security.xml',
        'security/ir.model.access.csv',
        'views/insotech_license_views.xml',
        'views/insotech_license_log_views.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
```

> **IMPORTANTE:** La dependencia `sale_subscription` es el módulo nativo de Suscripciones de Odoo 19 Enterprise. Si en la instancia de Odoo.sh el nombre técnico es diferente, adapta. Investiga antes de asumir.

**Modelo `insotech.license`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Nombre/descripción de la licencia |
| `token` | Char (required, unique, index) | Token único que el cliente configura en su Odoo |
| `partner_id` | Many2one → `res.partner` | Contacto del cliente o partner |
| `subscription_id` | Many2one → `sale.order` | Suscripción de Odoo vinculada (opcional) |
| `license_type` | Selection | `internal` / `partner` / `payperuse` |
| `state` | Selection | `active` / `blocked` / `exhausted` / `expired` |
| `max_usage` | Integer | Límite de facturas (0 = ilimitado). Solo para `payperuse`. |
| `current_usage` | Integer | Acumulado de facturas reportadas en el periodo actual |
| `total_usage` | Integer | Acumulado histórico total de facturas |
| `allowed_vat` | Char | NIT autorizado (si vacío, acepta cualquiera) |
| `allowed_url` | Char | URL autorizada del Odoo del cliente (si vacío, acepta cualquiera) |
| `last_ping` | Datetime | Última vez que el cliente se comunicó |
| `last_ping_ip` | Char | IP del último ping |
| `notes` | Text | Notas internas |

**Funcionalidades del modelo:**
- Al crear una licencia, si no se proporciona `token`, generar uno automático usando **UUID4** (`import uuid; str(uuid.uuid4())`). Formato final: `INS-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. UUID4 tiene 2^122 combinaciones, inmune a brute-force.
- Método `_check_license(token, vat, url)` que retorna el `status` correspondiente.
- Un botón "Bloquear" y "Activar" en la vista formulario para cambiar el estado manualmente.

---

### Tarea 3.2b — Modelo de Auditoría `insotech.license.log`

**Archivo:** `insotech_saas_server/models/insotech_license_log.py`

Cada ping que reciba el Controller debe persistirse en este modelo (no solo en `_logger`):

| Campo | Tipo | Descripción |
|---|---|---|
| `license_id` | Many2one → `insotech.license` | Licencia consultada (nullable si token no existe) |
| `timestamp` | Datetime | Momento del ping (`fields.Datetime.now()`) |
| `ip_address` | Char | IP del request |
| `vat` | Char | NIT reportado por el cliente |
| `url` | Char | URL reportada por el cliente |
| `token_used` | Char (index) | Token enviado en el request |
| `usage_count` | Integer | Facturas reportadas en este ping |
| `result` | Selection | `active` / `blocked` / `exhausted` / `not_found` |
| `is_suspicious` | Boolean (default=False) | `True` si el VAT/URL no coincide con los autorizados |

**Vista:** Lista de solo lectura con filtros por `is_suspicious`, por `result`, por `license_id`.

**Menú:** Sub-menú bajo **Insotech → Licencias → Log de Auditoría**.

**CRON de purge:** Crear una acción programada semanal que elimine registros del log con más de **180 días** de antigüedad para no saturar la BD.

---

### Tarea 3.4 — Controller API `/verify`

**Archivo:** `insotech_saas_server/controllers/license_api.py`

Crea un Controller HTTP que responda en la ruta `/insotech/api/v1/verify`:

```python
from odoo import http
from odoo.http import request
import json

class InsotechLicenseAPI(http.Controller):

    @http.route(
        '/insotech/api/v1/verify',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def verify_license(self, **kwargs):
        """Validate a license token and report usage."""
        # 1. Extraer datos del payload
        # 2. Buscar la licencia por token
        # 3. Validar VAT y URL si están configurados
        # 4. Registrar el usage_count reportado
        # 5. Actualizar last_ping
        # 6. Verificar límites (max_usage para pay-per-use)
        # 7. Retornar {"status": "active"/"blocked"/"exhausted"}
```

**Lógica de validación:**

```
¿Token existe?
   No → { "status": "blocked" }
   Sí ↓

¿Estado de la licencia?
   blocked → { "status": "blocked" }
   expired → { "status": "blocked" }
   exhausted → { "status": "exhausted" }
   active ↓

¿VAT/URL coinciden? (si están configurados)
   No → { "status": "blocked" } + log de alerta
   Sí ↓

¿Es pay-per-use Y current_usage >= max_usage?
   Sí → { "status": "exhausted" }
   No ↓

Registrar usage_count, actualizar last_ping
→ { "status": "active" }
```

**Registro de consumo (SQL atómico para evitar race conditions):**

No uses el ORM para incrementar contadores. Usa SQL atómico:

```python
# ❌ MAL — race condition si dos pings simultáneos del mismo token
license.current_usage += usage_count

# ✅ BIEN — atómico, sin race conditions
self.env.cr.execute(
    "UPDATE insotech_license SET current_usage = current_usage + %s, "
    "total_usage = total_usage + %s, last_ping = %s, last_ping_ip = %s "
    "WHERE id = %s",
    (usage_count, usage_count, fields.Datetime.now(), ip, license.id)
)
self.env.cr.commit()  # Asegurar persistencia inmediata
license.invalidate_recordset()  # Limpiar caché ORM
```

- Actualizar `last_ping` con `fields.Datetime.now()`.
- Guardar la IP del request para auditoría.
- **Crear un registro en `insotech.license.log`** con todos los datos del ping y el resultado.

**Seguridad:**
- `auth='none'` porque los clientes no tienen usuarios en nuestro Odoo.
- `csrf=False` porque es una API externa.
- Usar `sudo()` para las operaciones de BD dentro del controller.
- Loggear todos los intentos (exitosos y fallidos) con `_logger`.
- **Si VAT/URL no coinciden** con los autorizados, marcar `is_suspicious=True` en el log.
- **Rate limiting externo:** Se configura en Cloudflare (no en código). El Controller NO necesita implementar rate limiting.

---

### Tarea 3.4b — Endpoint Health-Check `/health`

Agregar al mismo Controller un endpoint GET simple para monitoreo externo:

```python
@http.route(
    '/insotech/api/v1/health',
    type='http',
    auth='none',
    methods=['GET'],
    csrf=False,
)
def health_check(self, **kwargs):
    """Simple health check for uptime monitoring (UptimeRobot, etc.)."""
    return request.make_json_response({'status': 'ok'})
```

Este endpoint:
- No requiere token ni autenticación.
- Retorna `{"status": "ok"}` y HTTP 200.
- Se usa para configurar monitores externos (UptimeRobot, Pingdom, Cloudflare Health Checks).

---

### Tarea 3.5 — Conexión con Suscripciones (Opcional pero deseable)

Si el campo `subscription_id` está lleno, verificar que la suscripción esté en estado activo (`in_progress`). Si la suscripción está cerrada, pausada, o vencida → la licencia se considera `blocked` aunque su `state` diga `active`.

Para pay-per-use: investigar cómo registrar el `usage_count` como "cantidad entregada" (`qty_delivered`) en la línea de suscripción, para que Odoo genere la factura automáticamente al cierre del periodo.

> Si la integración con `sale_subscription` resulta compleja, déjala como TODO documentado en el código y enfócate en que el Controller funcione correctamente con el modelo `insotech.license` puro.

---

## VISTA — Panel de Gestión de Licencias

Crea una interfaz administrativa para ver y gestionar las licencias:

1. **Vista Lista (Tree):** Token, Partner, Tipo, Estado, Uso Actual, Último Ping.
2. **Vista Formulario:** Todos los campos, con botones "Bloquear" / "Activar" en el header.
3. **Menú:** Crea una entrada de menú accesible desde el menú principal de Odoo: **Insotech → Licencias**.
4. **Filtros predefinidos:** Por estado (activas, bloqueadas), por tipo (internal, partner, payperuse).

---

## CRON — Acciones Programadas

Crea **3 acciones programadas**:

### Cron 1: Verificación de vencimientos (diario)
1. Busque licencias con suscripción vencida → las pase a `expired`.
2. Busque licencias pay-per-use que hayan alcanzado su `max_usage` → las pase a `exhausted`.

### Cron 2: Reset de consumo mensual (1er día de cada mes)
1. Resetear `current_usage` a 0 para todas las licencias pay-per-use activas.
2. Loggear el reset con el valor anterior para auditoría.

### Cron 3: Purge de logs de auditoría (semanal)
1. Eliminar registros de `insotech.license.log` con más de 180 días de antigüedad.

---

## REGLAS ABSOLUTAS

1. **Este código NUNCA va al repo del producto (`insotech_l10n_co_advanced`).** Solo vive en `davidhdzara/insotech`.
2. **El Controller debe responder en menos de 4 segundos.** El cliente tiene timeout. Usa `sudo()` y consultas eficientes.
3. **No modifiques** ningún módulo existente (`insotech_core`, `insotech_l10n_co_advanced`, `theme_insotech`).
4. **Logging completo.** Todo ping debe quedar en los logs para auditoría.
5. **PEP8, docstrings, calidad OCA.**

---

## CONVENCIONES

- **Versión:** `19.0.1.0.0`
- **Licencia:** `OPL-1`
- **IDs XML:** Prefijo `insotech_saas_server_`
- **Commit:** `[ADD] insotech_saas_server: servidor de licenciamiento SaaS con API /verify`
- **Push a:** `origin dev-saas-server`

---

## DATOS DEMO (`data/demo_data.xml`)

Crea 3 licencias de ejemplo para facilitar pruebas en la rama de desarrollo:

```xml
<odoo>
  <data noupdate="0">
    <!-- Licencia Interna (ilimitada) -->
    <record id="demo_license_internal" model="insotech.license">
      <field name="name">Demo — Uso Interno</field>
      <field name="license_type">internal</field>
      <field name="state">active</field>
      <field name="max_usage">0</field>
    </record>

    <!-- Licencia Partner -->
    <record id="demo_license_partner" model="insotech.license">
      <field name="name">Demo — Partner Reseller</field>
      <field name="license_type">partner</field>
      <field name="state">active</field>
      <field name="max_usage">0</field>
    </record>

    <!-- Licencia Pay-per-use (límite 100 facturas) -->
    <record id="demo_license_payperuse" model="insotech.license">
      <field name="name">Demo — Pay per Use</field>
      <field name="license_type">payperuse</field>
      <field name="state">active</field>
      <field name="max_usage">100</field>
    </record>
  </data>
</odoo>
```

> Los tokens se auto-generarán como UUID4 al crearse. Consulta los tokens generados en **Insotech → Licencias** después de instalar.

---

## VERIFICACIÓN

Antes de terminar, verifica que:
1. El módulo se declara correctamente con `python -c "import ast; ast.literal_eval(open('insotech_saas_server/__manifest__.py').read())"`.
2. Los archivos CSV de seguridad no tienen errores de formato.
3. El Controller `/verify` es accesible vía `curl`:
```bash
curl -X POST https://[tu-url-dev].odoo.com/insotech/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","params":{"token":"TEST","vat":"901234567","url":"http://test.com","usage_count":5,"reset_counter":true}}'
```
4. El health-check responde:
```bash
curl https://[tu-url-dev].odoo.com/insotech/api/v1/health
# Esperado: {"status": "ok"}
```
5. Verificar que las 3 licencias demo existen en **Insotech → Licencias**.
6. Verificar que el log de auditoría registra cada ping en **Insotech → Licencias → Log de Auditoría**.

***
