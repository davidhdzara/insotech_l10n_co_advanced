# Odoo V19: sale_subscription como dependencia rompe builds con l10n_co

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al desarrollar el módulo `insotech_saas_server` con `sale_subscription` listado en `depends` del `__manifest__.py`, el build de Odoo.sh fallaba consistentemente con errores de "Invalid invoice configuration" relacionados con Carvajal y DIAN.

## 🚨 El Problema o Error
```text
ERROR odoo.addons.account.demo.account_demo: Error while posting demo data
odoo.exceptions.UserError: Invalid invoice configuration:
Carvajal credentials are not set on the company...
'Obligaciones y Responsabilidades' on the Customer Fiscal Data section needs to be set...
```

El build se marcaba como **"Test: Failed"** en Odoo.sh, aunque el código del módulo era correcto.

## 🔍 Causa Raíz
`sale_subscription` tiene dependencias transitivas hacia `account` y módulos de facturación. Al instalarse, Odoo.sh ejecuta la demo data de contabilidad que intenta postear facturas electrónicas. Con la localización colombiana (`l10n_co_edi`) activa, las validaciones de Carvajal/DIAN bloquean el posteo porque:
- No hay credenciales de Carvajal configuradas en la compañía demo
- Los partners demo no tienen "Obligaciones y Responsabilidades"
- El diario de Compras no tiene configurada la Resolución DIAN

**Las otras ramas del mismo repo no tenían este problema** porque ninguna dependía de `sale_subscription`.

## ✅ Solución Adoptada
1. **Quitar `sale_subscription` de `depends`** y dejarlo como dependencia blanda.
2. **Agregar `sale`** (módulo ligero, sin demo data de contabilidad problemática) para tener acceso al modelo `sale.order`.
3. **Envolver las verificaciones de suscripción en `try/except`** para que funcionen si `sale_subscription` está instalado sin romper si no lo está.

```python
# __manifest__.py — antes (rompe el build)
'depends': ['base', 'mail', 'contacts', 'sale_subscription'],

# __manifest__.py — después (funciona)
'depends': ['base', 'mail', 'contacts', 'sale'],
```

## 💡 Buenas Prácticas / Cómo evitarlo
- **NUNCA listar `sale_subscription` como dependencia dura** en repositorios con localización colombiana activa, a menos que estés preparado para configurar demo data de Carvajal/DIAN.
- **Usa dependencias blandas**: verifica en runtime si el módulo está instalado (`subscription_state` envuelto en `try/except`).
- **Antes de agregar una dependencia**, evalúa sus dependencias transitivas y su demo data.

> **📝 Blog Potential:** ⭐⭐⭐⭐⭐ (Muy alto — afecta a TODOS los desarrolladores colombianos)
