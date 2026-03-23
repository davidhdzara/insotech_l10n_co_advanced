# Odoo V19: type='jsonrpc' NO es compatible con requests.post(json=payload)

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
El módulo `insotech_saas_server` usaba `type='jsonrpc'` en el controller `/verify`. El build de Odoo.sh pasaba correctamente, pero en runtime la API no podía recibir los datos del cliente (`insotech_core`).

## 🚨 El Problema o Error
El cliente envía un POST plano:
```python
requests.post('https://www.insotech.it/insotech/api/v1/verify', json=payload, timeout=4)
```
Esto genera un body JSON plano: `{"token": "...", "vat": "..."}`.

Pero `type='jsonrpc'` en V19 espera el formato JSON-RPC 2.0:
```json
{"jsonrpc": "2.0", "method": "call", "id": 1, "params": {"token": "...", "vat": "..."}}
```

Los `kwargs` del controller llegaban **vacíos** porque Odoo buscaba los datos dentro de `params`, que no existía.

## 🔍 Causa Raíz
- En Odoo V19, `type='json'` es un alias deprecado de `type='jsonrpc'`. Ambos hacen lo mismo.
- `type='jsonrpc'` parsea el body esperando la estructura JSON-RPC 2.0 y pasa `params` como kwargs.
- `requests.post(url, json=payload)` envía JSON plano (sin envelope JSON-RPC), por lo tanto Odoo no encuentra `params` y los kwargs quedan vacíos.
- **El build NO detecta este problema** porque Odoo.sh solo verifica instalación del módulo, no llamadas API runtime.

## ✅ Solución Adoptada
Cambiar a `type='http'` y parsear el JSON manualmente:

```python
import json

@http.route('/insotech/api/v1/verify', type='http', auth='none',
            methods=['POST'], csrf=False)
def verify_license(self, **kwargs):
    try:
        data = json.loads(request.httprequest.data or '{}')
    except (ValueError, TypeError):
        return request.make_json_response(
            {'status': 'blocked'}, status=400,
        )
    token = data.get('token', '')
    # ... lógica ...
    return request.make_json_response({'status': status})
```

**Puntos clave:**
- `request.httprequest.data` contiene el body raw del request
- `json.loads()` lo parsea a dict de Python
- `request.make_json_response()` serializa la respuesta como JSON con Content-Type correcto
- `try/except` defensivo para JSON malformado

## 💡 Buenas Prácticas / Cómo evitarlo
- **NO uses `type='jsonrpc'` si el cliente envía JSON plano** (ej. con `requests.post(json=...)`)
- **`type='jsonrpc'`** es solo para comunicación con el framework JS interno de Odoo (OWL `rpc()`)
- **`type='http'`** es para APIs REST externas que reciben POST con JSON plano
- **El build de Odoo.sh NO prueba runtime API** — hay que probar manualmente con curl/requests
- **Regla de oro**: revisa SIEMPRE qué envía el cliente antes de definir el `type` del controller

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Crítico — todo desarrollador que haga APIs REST en Odoo 19 caerá en esta trampa)
