# Odoo V19: Campos eliminados de ir.cron (numbercall, state, priority)

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al definir acciones planificadas (cron jobs) para el módulo `insotech_saas_server`, usamos la estructura XML clásica de V18 que incluía `numbercall`, `state` y `priority`.

## 🚨 El Problema o Error
```text
CRITICAL odoo.modules.module: Couldn't load module insotech_saas_server
ValueError: Invalid field 'numbercall' in 'ir.cron'

ParseError: while parsing ir_cron_data.xml:6, somewhere inside
<record id="cron_check_subscriptions" model="ir.cron">
    <field name="numbercall">-1</field>  ← ESTE CAMPO YA NO EXISTE
```

## 🔍 Causa Raíz
En Odoo V19, el modelo `ir.cron` fue simplificado:
- **`numbercall`** eliminado — los cron siempre corren indefinidamente
- **`state`** eliminado — `code` es el único tipo (ya no existe `object`)
- **`priority`** eliminado — la prioridad se maneja de otra forma

## ✅ Solución Adoptada
```xml
<!-- ANTES (V18) ❌ -->
<record id="mi_cron" model="ir.cron">
    <field name="name">Mi Tarea</field>
    <field name="model_id" ref="model_mi_modelo"/>
    <field name="state">code</field>
    <field name="code">model.mi_metodo()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
    <field name="priority">100</field>
</record>

<!-- DESPUÉS (V19) ✅ -->
<record id="mi_cron" model="ir.cron">
    <field name="name">Mi Tarea</field>
    <field name="model_id" ref="model_mi_modelo"/>
    <field name="code">model.mi_metodo()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active">True</field>
</record>
```

## 💡 Buenas Prácticas / Cómo evitarlo
- **Al migrar**: buscar `numbercall` y `state` en TODOS los archivos que definan `ir.cron`.
- **Campos válidos en V19**: `name`, `model_id`, `code`, `interval_number`, `interval_type`, `active`, `nextcall`, `user_id`.

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Crítico — rompe CUALQUIER módulo con cron jobs al migrar)
