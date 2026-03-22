# Prompt: Revisión y Finalización de Fase 3 — Servidor API SaaS

Copia y pega el siguiente texto al agente:

***

**Actúa como un desarrollador senior de Odoo 19 Enterprise con experiencia en controllers HTTP, APIs REST, y despliegues en Odoo.sh.**

Un agente previo construyó el módulo `insotech_saas_server` en la rama `dev-saas-server` del repositorio `davidhdzara/insotech`. El módulo está **99% completo**, pero necesita revisión, corrección de bugs, y verificación funcional.

---

## PASO 0 — OBLIGATORIO: LEE ANTES DE TOCAR CÓDIGO

Lee estos archivos primero. Son la base de conocimiento del proyecto:

1. `.agent/skills/odoo-v19-buenas-practicas/SKILL.md` — Convenciones Odoo V19
2. `.agent/skills/base-de-conocimiento/SKILL.md` — Aprendizajes y errores conocidos

Directorio de referencia: `/home/david/odoo-projects/insotech_l10n_co_advanced/`

Luego lee TODO el código existente del módulo:

Directorio del módulo: `/home/david/odoo-projects/insotech/insotech_saas_server/`

Archivos a leer (en este orden):
1. `__manifest__.py`
2. `models/insotech_license.py` (365 líneas)
3. `models/insotech_license_log.py` (102 líneas)
4. `controllers/license_api.py` (195 líneas)
5. `views/insotech_license_views.xml` (164 líneas)
6. `views/insotech_license_log_views.xml` (115 líneas)
7. `security/insotech_security.xml` y `security/ir.model.access.csv`
8. `data/ir_cron_data.xml` y `data/demo_data.xml`

---

## CONTEXTO

### Qué hace este módulo
Es el servidor que recibe peticiones de validación de licencia de clientes que usan los módulos Insotech. Vive EXCLUSIVAMENTE en el Odoo.sh privado de Insotech (`www.insotech.it`).

### Qué hace el lado CLIENTE (`insotech_core`)
El módulo `insotech_core` envía un POST así:

```python
# En insotech_core/models/res_company.py
payload = {
    "token": self.insotech_license_token,
    "vat": self.vat,
    "url": url,
    "usage_count": self.insotech_usage_count,
    "reset_counter": True,
}
response = requests.post(
    "https://www.insotech.it/insotech/api/v1/verify",
    json=payload,
    timeout=4,
)
result = response.json()
# Espera: {"status": "active"} o {"status": "blocked"} o {"status": "exhausted"}
```

Lee el código completo del cliente en:
`/home/david/odoo-projects/insotech_l10n_co_advanced/insotech_core/models/res_company.py`

---

## PROBLEMAS IDENTIFICADOS A REVISAR

### 🔴 Problema 1: `type='jsonrpc'` vs `type='json'` en el Controller

El controller usa `type='jsonrpc'` (línea 39 de `license_api.py`). Pero el cliente (`insotech_core`) envía un POST plano con `requests.post(url, json=payload)`. Necesitas verificar:

- Si `insotech_core` envía el payload en formato JSON-RPC 2.0 (`{"jsonrpc": "2.0", "method": "call", "params": {...}}`) o como JSON plano.
- Si `type='jsonrpc'` en el controller es compatible con lo que envía el cliente.
- Si no es compatible, cambiar a `type='json'` o `type='http'` según corresponda.

**LEE el código del cliente** en `res_company.py` para determinar qué formato usa realmente.

### 🟡 Problema 2: `models.Constraint` — Sintaxis V19

La línea 137-140 de `insotech_license.py` usa `models.Constraint()` que es sintaxis nueva de Odoo 19. Verifica que funcione correctamente. Si Odoo.sh rechaza esta sintaxis, usar el formato clásico `_sql_constraints`.

### 🟡 Problema 3: `sale_subscription` no está en dependencias

El `__manifest__.py` tiene `'sale'` pero NO `'sale_subscription'`. El modelo usa `subscription_state` del sale.order que puede no existir sin el módulo de suscripciones. Verifica:
- ¿`sale_subscription` es un módulo separado en Odoo 19 o está fusionado en `sale`?
- Si es separado, ¿debe ser dependencia obligatoria o se maneja defensivamente?

### 🟢 Problema 4: Build de Odoo.sh

El módulo fue pusheado a la rama `dev-saas-server`. Necesitas verificar:
- Que el build de Odoo.sh no falle (no tenemos acceso visual, pero podemos verificar la estructura del módulo con lint).
- Que los archivos `.pyc` en `controllers/__pycache__/` y `models/__pycache__/` no estén commiteados en git.

---

## TUS TAREAS

### Tarea 1: Auditoría y Fix de Compatibilidad API

1. Lee `insotech_core/models/res_company.py` completo.
2. Determina el formato del POST que envía.
3. Ajusta el `type=` del controller en `license_api.py` para que sea compatible.
4. Verifica que la respuesta del controller (`return {'status': status}`) sea lo que el cliente espera.

### Tarea 2: Verificar/Corregir `models.Constraint`

1. Verifica si `models.Constraint` la sintaxis correcta en Odoo 19.
2. Si no funciona, reemplazar por `_sql_constraints` clásico.

### Tarea 3: Resolver dependencia `sale_subscription`

1. Investigar si Odoo 19 Enterprise tiene `subscription_state` en `sale.order` con solo la dependencia `sale`.
2. Si requiere `sale_subscription`, agregar a las dependencias.
3. Si no se quiere como dependencia dura, hacer el chequeo defensivo (ya está parcialmente hecho con try/except).

### Tarea 4: Limpiar archivos innecesarios

1. Verificar si hay `.pyc` commiteados. Si sí, eliminarlos y agregar `__pycache__/` al `.gitignore`.

### Tarea 5: Test funcional del endpoint

1. Simular un POST al endpoint `/insotech/api/v1/verify` usando el formato correcto.
2. Verificar que responde `{"status": "active"}` para un token válido.
3. Verificar que responde `{"status": "blocked"}` para un token inexistente.
4. Verificar que el health-check `GET /insotech/api/v1/health` responde `{"status": "ok"}`.

### Tarea 6: Commit y Push

Después de todos los fixes:
```bash
cd /home/david/odoo-projects/insotech
git add -A
git commit -m "[FIX] insotech_saas_server: correcciones de compatibilidad API y limpieza"
git push origin dev-saas-server
```

---

## REGLAS

1. **No reescribas código que funciona.** Solo corrige lo que está roto o es incompatible.
2. **Lee el código del cliente antes de cambiar el controller.** La compatibilidad es lo más importante.
3. **No uses `self.env.cr.commit()`.** Las transacciones las maneja Odoo.
4. **PEP8, docstrings, calidad OCA.**
5. **Trabaja en el repo `/home/david/odoo-projects/insotech/` en la rama `dev-saas-server`.**

***
