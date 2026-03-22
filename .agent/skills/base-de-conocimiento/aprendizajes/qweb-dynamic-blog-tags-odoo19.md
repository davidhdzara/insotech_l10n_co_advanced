# Estructura Dinámica de Componentes de Blog en Odoo 19

**Fecha de Registro:** 2026-03-10
**Contexto del Problema:**
Desarrollando el rediseño del módulo nativo `website_blog` para la aplicación web InSoTech Insights, necesitamos integrar componentes que dinámicamente mostrasen información desde el backend (Trending Topics) sin sacrificar la posibilidad de estructurar libremente el frontend QWeb mediante "Dropzones" del Website Builder.

## 🚨 El Problema o Diferencia
En Odoo 19, inyectar "Trending Topics" manualmente bloquea al administrador si las categorías cambian seguido. Si usamos Snippets estáticos (`s_`), el usuario tiene que administrar el texto plano HTML, lo que no escala.

## 🔍 Causa Raíz
El motor nativo de Blog de Odoo muestra *Tags* asociados a un artículo, pero no tiene un snippet nativo pre-construido diseñado exclusivamente para iterar los "Tags Globales" de todos los posts a nivel de página/sidebar.

## ✅ Solución Adoptada
Inyección del ORM directamente a través del contexto de renderizado QWeb usando la global `request.env`. Se creó un snippet dinámico que no requiere un controlador en Python, ideal para temas ligeros (`theme_insotech`):

```xml
<t t-set="trending_tags" t-value="request.env['blog.tag'].sudo().search([('post_ids.website_published', '=', True)], limit=5)"/>
<t t-if="trending_tags" t-foreach="trending_tags" t-as="tag">
    <a t-attf-href="/blog/tag/#{slug(tag)}">
        <span t-out="tag.name"/>
        <t t-out="len(tag.post_ids.filtered(lambda p: p.website_published))"/> posts
    </a>
</t>
```

Esta solución:
1.  Busca solo los Tags (`blog.tag`) que tengan *Posts Publicados*.
2.  Itera sus objetos.
3.  Calcula y mapea en tiempo real la cantidad de publicaciones publicadas asociadas a ese Tag.
4.  No interfiere con el Core y mantiene el QWeb seguro usando `t-out`.

## 💡 Buenas Prácticas / Cómo evitarlo
*   **Performance (LCP / FCP):** Siempre añadir un `limit` a la consulta de `request.env` dentro de QWeb (ej. `limit=5`) para prevenir cuellos de botella al renderizar si el blog crece a cientos de tags.
*   **Security:** Uso obligatorio de `sudo()` cuando el módulo `blog.tag` puede tener reglas de visibilidad, para garantizar que el Sidebar no falle al visitante anónimo pero siga filtrando por estado *publicado*.
*   **Fallback QWeb:** Añadir siempre un `t-else` para manejar graciosamente bases de datos nuevas sin tags registrados.
