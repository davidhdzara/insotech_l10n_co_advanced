# Odoo v19: Paginación Personalizada de Artículos en el Blog

**Fecha de Registro:** 2026-03-10
**Contexto del Problema:**
Al maquetar una cuadrícula B2B con un diseño asimétrico (2 columnas en lugar de 3) nos vimos en la necesidad de limitar visualmente la cantidad de posts por página en el Blog Index `posts_loop` a exactamente **4 artículos**. 

## 🚨 El Problema o Error
Limitarlo con CSS usando reglas condicionales estéticas como `& > div:nth-child(n+5) { display: none !important; }` escondía matemáticamente los artículos restantes en la pantalla (las cajas 5 a la 12), pero el paginador inferior en Odoo seguía asumiendo que el usuario ya estaba viendo 12 elementos simultáneos (el valor _default_ estático del framewok), destrozando así la numeración y el paso a la Página 2 (`/blog/page/2`).

## 🔍 Causa Raíz
A diferencia de otros módulos de E-Commerce en donde la paginación de los productos puede ser controlada desde QWeb u Opciones Web (`ppg` parameter), en el modelo de Blog Nativo, Odoo controla la paginación con código fuerte (hardcoded) en el controlador de Python central `main.py` -> `class WebsiteBlog(http.Controller):`

Odoo consume una propiedad privada de clase `@property def _blog_post_per_page(self):` para saber cuántos registrar antes de invocar la URL de next page.

## ✅ Solución Adoptada
Es obligatorio invadir el controlador del módulo original. En la carpeta `controllers/main.py` de nuestro tema (Theme InSoTech), realizamos un `import` de la clase nativa y la heredamos (Override) sobrescribiendo únicamente la propiedad de límite.

```python
# -*- coding: utf-8 -*-
from odoo.addons.website_blog.controllers.main import WebsiteBlog

class InsotechWebsiteBlog(WebsiteBlog):
    
    @property
    def _blog_post_per_page(self):
        """ 
        OVERRIDE: Limitar estricta y nativamante la paginación de Odoo 
        en InSoTech a 4, garantizando que el `pager` divida las páginas en 4s
        perfectamente para el layout de "Bento Grid" B2B Básico 2x2.
        """
        return 4
```

Recuerda siempre registrar el archivo en el `controllers/__init__.py` y en la raíz del tema `__init__.py`.

## 💡 Buenas Prácticas / Cómo evitarlo
- **NUNCA manipular paginaciones masivas mediante trucos de ocultamiento CSS (`display: none`).** Esto rompe la experiencia de usuario general porque deja "huérfanos" (ítems invisibles en memoria que no paginan al backend).
- Si el requerimiento de diseño exige un número de GridLayout matemático no divisible del nativo de Odoo (ej, 4 en lugar del default de 12 o 16), siempre opta por inyectar un controlador para que la carga de Servidor sea óptima y la numeración Pager cuadre.
