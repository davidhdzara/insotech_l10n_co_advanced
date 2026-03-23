# Odoo V19: Deprecaciones en Controllers y Search Views

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al desarrollar un controller HTTP y vistas de búsqueda para el módulo `insotech_saas_server`, usamos patrones de V18 que generaron warnings y errores de validación RELAXNG en V19.

## 🚨 El Problema o Error
### 1. Controller `type='json'` deprecado
```text
DeprecationWarning: Since 19.0, @route(type='json') is a deprecated alias to @route(type='jsonrpc')
```

### 2. Search view `expand` attribute inválido
```text
WARNING odoo.tools.view_validation: Invalid attribute expand for element group
WARNING odoo.tools.view_validation: Expecting an element field, got nothing
ERROR odoo.registry: Failed to load registry → ParseError: Invalid view insotech.license.search
```
La combinación de `expand` inválido + validación RELAXNG estricta **crashea el registro completo**.

## 🔍 Causa Raíz
### Controller
V19 distingue entre `jsonrpc` (protocolo JSON-RPC estándar) y `json` (alias deprecado). Aunque funciona, el warning contamina los logs y en futuras versiones dejará de funcionar.

### Search Views
En V19, los atributos `expand` y `string` fueron **eliminados** del elemento `<group>` en search views. El schema RELAXNG de Odoo V19 los rechaza, causando un error fatal.

## ✅ Solución Adoptada
```python
# Controller — ANTES ❌
@http.route('/mi/ruta', type='json', auth='none')

# Controller — DESPUÉS ✅ (para comunicación interna OWL/JS)
@http.route('/mi/ruta', type='jsonrpc', auth='none')
```

```xml
<!-- Search View — ANTES ❌ -->
<group expand="0" string="Agrupar por">
    <filter name="group_state" string="Estado" context="{'group_by': 'state'}"/>
</group>

<!-- Search View — DESPUÉS ✅ -->
<group>
    <filter name="group_state" string="Estado" context="{'group_by': 'state'}"/>
</group>
```

> [!CAUTION]
> **`type='jsonrpc'` NO sirve para APIs REST externas.**
> Si el cliente envía JSON plano (`requests.post(url, json=payload)`),
> usa `type='http'` con `json.loads(request.httprequest.data)`.
> Ver: [type='http' vs type='jsonrpc' para APIs REST](odoo-v19-type-http-vs-jsonrpc-api-rest.md)

## 💡 Buenas Prácticas / Cómo evitarlo
- **`type='jsonrpc'`** → solo para comunicación con OWL/JS interno de Odoo (`rpc()`)
- **`type='http'`** → para APIs REST que reciben JSON plano de clientes externos
- **Buscar/Reemplazar global**: `type='json'` → `type='jsonrpc'` al migrar (excepto APIs REST)
- **En search views**: eliminar `expand` y `string` de TODOS los `<group>`.
- **Validar XML**: Los errores RELAXNG en V19 son fatales. Un solo atributo inválido puede matar el registry completo.

> **📝 Blog Potential:** ⭐⭐⭐⭐ (Alto — afecta a todo módulo con controllers o search views)
