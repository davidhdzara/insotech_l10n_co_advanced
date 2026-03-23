# Odoo.sh: Cada push genera una nueva URL en ramas Development

**Fecha de Registro:** 2026-03-22
**Contexto del Problema:**
Al probar el módulo `insotech_saas_server` en la rama `dev-saas-server`, se intentó acceder a la URL del build anterior después de hacer un nuevo push. La URL devolvía "Page not found".

## 🚨 El Problema o Error
Después de hacer push de un nuevo commit, la URL del build previo (`insotech-dev-saas-server-29976742.dev.odoo.com`) dejó de funcionar. Al intentar acceder, Odoo redirigía a una página de error "Page not found — does not exist (anymore?)".

## 🔍 Causa Raíz
En Odoo.sh, las ramas de **Development** generan un **nuevo build con un identificador único** (y por tanto una **nueva URL**) con cada push. La URL anterior se destruye automáticamente.

Formato: `<nombre-rama>-<build-id>.dev.odoo.com`

El `<build-id>` cambia en cada push, lo que invalida la URL anterior.

## ✅ Solución Adoptada
Después de cada push:
1. Ir a Odoo.sh → rama → esperar el nuevo build
2. Hacer clic en **CONNECT** para activar la instancia
3. Copiar la **nueva URL** que genera Odoo.sh
4. Usar esa nueva URL para todas las pruebas

## 💡 Buenas Prácticas / Cómo evitarlo
- **NUNCA hardcodees URLs de ramas dev** en scripts de pruebas — siempre obtén la URL fresca de Odoo.sh
- **Las ramas Staging y Production** mantienen URLs estables (no cambian con cada push)
- **Si necesitas una URL estable para pruebas**, mueve la rama a Staging
- **Antes de correr `curl`** contra la instancia, verifica que el build esté en estado "CONNECTED" en Odoo.sh

> **📝 Blog Potential:** ⭐⭐⭐ (Útil para principiantes en Odoo.sh)
