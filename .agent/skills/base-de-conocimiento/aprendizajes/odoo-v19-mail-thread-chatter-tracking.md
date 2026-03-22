# Odoo V19: mail.thread obligatorio para chatter y tracking

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al crear el modelo `insotech.license` con `tracking=True` en el campo `state` y `<chatter/>` en la vista formulario, el build de Odoo.sh fallaba sin un error claro.

## 🚨 El Problema o Error
El build se marcaba como **"Test: Failed"** sin un traceback explícito relacionado. El módulo se cargaba pero no funcionaba correctamente.

## 🔍 Causa Raíz
`tracking=True` en un campo y `<chatter/>` en la vista XML **requieren** que el modelo herede `mail.thread`. Sin esta herencia:
- `tracking=True` no genera registros de cambios
- `<chatter/>` en la vista causa errores de frontend
- Las pruebas automáticas fallan

Además, `mail.thread` requiere que `mail` esté en las dependencias del módulo.

## ✅ Solución Adoptada
```python
# Modelo — agregar herencia
class InsotechLicense(models.Model):
    _name = 'insotech.license'
    _inherit = ['mail.thread']  # ← AGREGAR ESTO
```

```python
# __manifest__.py — agregar dependencia
'depends': ['base', 'mail', 'contacts'],  # ← 'mail' es obligatorio
```

## 💡 Buenas Prácticas / Cómo evitarlo
- **Regla de oro**: Si usas `tracking=True` o `<chatter/>`, SIEMPRE hereda `mail.thread`.
- **Checklist**: `tracking=True` → ¿hereda `mail.thread`? → ¿`mail` en depends?

> **📝 Blog Potential:** ⭐⭐⭐ (Medio — error común pero documentado en la doc oficial)
