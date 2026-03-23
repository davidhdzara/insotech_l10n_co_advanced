# Odoo V19 Enterprise: product.product_category_goods missing + habilitador nativo DIAN

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al intentar usar el botón "Certificar con la DIAN" en Ajustes → Contabilidad (módulo `l10n_co_dian`), el sistema crashea porque falta un identificador externo.

## 🚨 El Problema o Error
```text
ValueError: External ID not found in the system: product.product_category_goods

File ".../l10n_co_dian/models/res_config_settings.py", line 204
  'categ_id': self.env.ref('product.product_category_goods').id,
```

El método `_l10n_co_dian_certify_create_or_update_product()` intenta crear un producto para el set de pruebas DIAN y referencia la categoría `product.product_category_goods` que no existe en la BD.

## 🔍 Causa Raíz
El XML ID `product.product_category_goods` se define normalmente en la **demo data** del módulo `product`. Si la instancia se creó sin demo data (común en producción/staging en Odoo.sh), este XML ID no existe aunque las categorías de producto sí estén creadas.

## ✅ Solución Adoptada
Crear manualmente el identificador externo:

1. Activar **modo desarrollador**
2. Ir a **Ajustes → Técnico → Identificadores Externos**
3. Clic **Nuevo** y llenar:
   - **Módulo:** `product`
   - **Nombre externo:** `product_category_goods`
   - **Modelo:** `product.category`
   - **ID del Registro:** ID de la categoría principal (ej. "All" → ver ID en la URL)
4. **Guardar**

## 💡 Descubrimiento Importante

El botón nativo **"Certificar con la DIAN"** (`action_l10n_co_certify_with_dian` en `l10n_co_dian/models/res_config_settings.py`) cumple una función similar al wizard `insotech_dian_wizard`:
- Captura Software ID, PIN, Test Set ID
- Configura modos de operación
- Ejecuta el proceso de certificación automáticamente

**Nuestro módulo `insotech_dian_wizard` es complementario:**
- Almacena los datos de forma independiente (sin depender de `l10n_co_dian`)
- Permite gestionar el estado de configuración (`not_configured` → `in_progress` → `enabled`)
- Puede usarse como paso previo antes de ejecutar el habilitador nativo

## 💡 Buenas Prácticas / Cómo evitarlo
- **Antes de desplegar**: verificar que los XML IDs de demo data referenciados por `l10n_co_dian` existan en la BD.
- **En instancias sin demo data**: siempre crear manualmente `product.product_category_goods`.
- **Conocer el flujo nativo**: `l10n_co_dian` tiene su propio habilitador en Ajustes → Contabilidad. Nuestro wizard complementa, no reemplaza.

> **📝 Blog Potential:** ⭐⭐⭐⭐ (Alto — afecta a toda instancia colombiana sin demo data)
