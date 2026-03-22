# Odoo V19: _sql_constraints eliminado — usar models.Constraint con prefijo _

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al definir una restricción UNIQUE en el campo `token` del modelo `insotech.license`, usamos el patrón clásico `_sql_constraints = [(...)` que funcionaba en V18 y anteriores.

## 🚨 El Problema o Error
```text
WARNING odoo.registry: Model attribute '_sql_constraints' is no longer supported,
please define model.Constraint on the model.
```
Luego al intentar usar `_constraints = [models.Constraint(...)]`:
```text
WARNING odoo.registry: Model attribute '_constraints' is no longer supported,
please use @api.constrains on methods instead.
```
Y al usar `token_unique = models.Constraint(...)` (sin prefijo `_`):
```text
CRITICAL odoo.modules.module: Couldn't load module insotech_saas_server
```

## 🔍 Causa Raíz
La clase `Constraint` hereda de `TableObject`, que en su `__set_name__` tiene:
```python
# odoo/orm/table_objects.py (V19)
assert name.startswith('_'), "Names of SQL objects in a model must start with '_'"
```

Los constraints en V19 son **atributos de clase** (no listas), y **DEBEN** empezar con `_`.

## ✅ Solución Adoptada
```python
# ANTES (V18) ❌
_sql_constraints = [
    ('token_unique', 'UNIQUE(token)', 'El token debe ser único.'),
]

# INTENTO INTERMEDIO (mal) ❌
_constraints = [models.Constraint('UNIQUE(token)', 'msg')]

# INTENTO SIN PREFIJO (crash) ❌
token_unique = models.Constraint('UNIQUE(token)', 'msg')

# CORRECTO (V19) ✅
_token_unique = models.Constraint(
    'UNIQUE(token)',
    'El token de licencia debe ser único.',
)
```

**Clave:** El atributo es a nivel de clase, NO dentro de una lista, y el nombre DEBE empezar con `_`.

## 💡 Buenas Prácticas / Cómo evitarlo
- **Patrón V19**: `_nombre = models.Constraint('SQL_DEFINITION', 'mensaje')`
- **Siempre prefijo `_`**. Sin él, `__set_name__` de `TableObject` arroja `AssertionError` y el módulo no carga.
- **No confundir**: `_constraints` (Python constraints, también deprecado) vs `_sql_constraints` (SQL, deprecado) vs `models.Constraint` (nuevo V19).
- **Fuente de verdad**: `odoo/orm/table_objects.py` en GitHub.

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Crítico — cambio universal que afecta a todos los módulos)
