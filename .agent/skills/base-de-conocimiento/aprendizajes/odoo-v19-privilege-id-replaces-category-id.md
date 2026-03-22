# Odoo V19: category_id eliminado de res.groups — usar privilege_id

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al crear grupos de seguridad para el módulo `insotech_saas_server`, definimos `ir.module.category` y referenciamos `category_id` en `res.groups` — patrón estándar de Odoo V18 y anteriores.

## 🚨 El Problema o Error
```text
CRITICAL odoo.service.server: Failed to initialize database
ERROR odoo.registry: Failed to load registry
```
El servidor crasheaba al intentar cargar `insotech_security.xml` sin un mensaje de error específico claro, solo "Failed to load registry" tras procesar el archivo de seguridad.

## 🔍 Causa Raíz
En Odoo V19, el sistema de seguridad fue **completamente reestructurado**:
- **`ir.module.category`** ya no se usa para agrupar res.groups
- **`category_id`** fue eliminado de `res.groups`
- **`res.groups.privilege`** es el nuevo modelo intermedio
- **`privilege_id`** reemplaza a `category_id`

La nueva arquitectura de 3 niveles es: **App → Privilege → Groups → Users**

## ✅ Solución Adoptada
```xml
<!-- ANTES (V18 — rompe en V19) ❌ -->
<record id="my_category" model="ir.module.category">
    <field name="name">Mi App</field>
</record>
<record id="my_group" model="res.groups">
    <field name="category_id" ref="my_category"/>
</record>

<!-- DESPUÉS (V19) ✅ -->
<record id="my_privilege" model="res.groups.privilege">
    <field name="name">Mi Privilegio</field>
</record>
<record id="my_group" model="res.groups">
    <field name="privilege_id" ref="my_privilege"/>
</record>
```

## 💡 Buenas Prácticas / Cómo evitarlo
- **Al migrar de V18 → V19**, busca y reemplaza TODOS los `ir.module.category` por `res.groups.privilege`.
- **Busca en tu XML**: `category_id` debe ser `privilege_id` en TODOS los `res.groups`.
- **También cambió**: `res.users.groups_id` → `group_ids` y `res.groups.users` → `user_ids`.

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Crítico — rompe TODOS los módulos al migrar)
