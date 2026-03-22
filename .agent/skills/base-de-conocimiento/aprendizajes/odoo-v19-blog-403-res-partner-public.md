# Odoo v19: 403 Forbidden (res.partner) al leer datos de autor en vistas públicas (Blog)

**Fecha de Registro:** 2026-03-10
**Contexto del Problema:**
Al intentar rediseñar la vista individual del blog (`blog_templates.xml`) para mostrar el nombre unificado del autor (`t-field="blog_post.author_id.name"` o `widget="contact"`), los usuarios desconectados o en modo incógnito (Public user - id=3) experimentaban una denegación de acceso total de Odoo (Error `403: Forbidden`).

## 🚨 El Problema o Error
```text
403: Forbidden
The page you were looking for could not be authorized.
Sorry, Public user (id=3) doesn't have 'read' access to:
- Contact (res.partner)
```

## 🔍 Causa Raíz
El modelo de seguridad de Odoo restringe de forma nativa la lectura directa a la tabla de contactos y proveedores (`res.partner`) para los usuarios públicos (no autenticados). Dado que `blog_post.author_id` guarda una relación `Many2one` hacia un partner, al intentar extraer su `.name` Odoo ejecutaba una query SQL directa con ORM hacia `res.partner`, haciendo saltar inmediatamente las _Record Rules_ de privacidad.

## ✅ Solución Adoptada
**1. Para Texto Plano (Nombres):**
Odoo provee campos computados de tipo texto específicamente inseguros en ciertos modelos para evitar precisamente esto. En `blog.post`, el campo de texto es `author_name`.
**Incorrecto:** `<span t-field="blog_post.author_id.name"/>`
**Correcto:** `<span t-out="blog_post.author_name"/>`

**2. Para Archivos / Imágenes Asociadas:**
Al renderizar el avatar de la relación, utilicé la elevación de privilegios nativa de QWeb invocando `.sudo()` directamente antes del campo relacional, lo que omite temporalmente las reglas de lectura:
**Correcto:** `<span t-field="blog_post.sudo().author_avatar" t-options="{'widget': 'image'}"/>`

## 💡 Buenas Prácticas / Cómo evitarlo
- **JAMÁS iterar o extraer propiedades a través de relaciones `Many2one` (usando dot notation) hacia Modelos Sensibles (`res.partner`, `res.users`, `hr.employee`) en plantillas QWeb web orientadas al público.**
- **SIEMPRE verificar si existen campos paralelos "seguros" (e.g. `partner_name`, `author_name`) o en su defecto invocar explícitamente `sudo()` para proteger la experiencia del usuario anónimo.**
