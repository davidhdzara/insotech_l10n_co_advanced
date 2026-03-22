# Bug: Bucle Infinito removeAllColor() en Odoo V19 Edit Mode

**Fecha:** Marzo 2026
**Contexto:** Desarrollo de Snippets (Componentes) para Website Builder
**Síntoma:** `Uncaught Javascript Error > Infinite Loop in removeAllColor()` al hacer clic sobre un bloque o intentar editar la página. El navegador colapsa y la interfaz gráfica de Odoo explota.

---

## 🛑 El Problema (Root Cause)

Odoo V19 tiene un bug severo en el analizador de Javascript del **Editor WYSIWYG** (específicamente en `ColorPlugin` y `LinkPlugin`). 

Este error se dispara **inmediatamente** cuando el constructor de sitios de Odoo intenta parsear un enlace (`<a>`) que cumple simultáneamente con estas tres condiciones mortales:

1. Es una etiqueta puramente de hipervínculo tipo texto nativo (`<a>`).
2. Tiene incorporadas clases utilitarias de color aplicadas directamente a ella (Ej. `text-primary` o `text-dark`).
3. **Lo más grave:** Contiene elementos anidados dentro del enlace (como una etiqueta `<i>` para iconos de FontAwesome) que *también* tienen clases de color o estilos en línea.

### Ejemplo de CÓDIGO TÓXICO que Rompe Odoo:
```html
<a href="/operaciones" class="text-primary text-decoration-none">
    Ver soluciones <i class="fa fa-arrow-right ms-1 text-primary"></i>
</a>
```

Cuando el usuario hace clic para editar, el iterador DOM de `ColorPlugin.removeAllColor` entra en un bucle recursivo infinito tratando de "limpiar" los colores del texto padre y del icono hijo para mostrar la paleta de colores del tema. Nunca logra resolver el árbol DOM y causa un Memory Leak (crasheo).

---

## ✅ La Solución Definitiva (Bypass)

Para mantener la funcionalidad del enlace intacta y mantener exactamente la misma apariencia de "texto clickeable", eludiendo por completo la falla del plugin, se debe **transmutar el enlace en un Botón Nivel Odoo**.

Odoo procesa los `<a class="btn">` mediante un plugin completamente diferente al de los enlaces de texto normales.

### Instrucciones Exactas:
Cualquier enlace complejo dentro de un Snippet debe llevar OBLIGATORIAMENTE las clases `btn btn-link`. 

### Ejemplo de CÓDIGO SEGURO:
```html
<!-- Se agrega btn btn-link, y se remueven clases de "text-decoration-none" ya que btn-link lo maneja nativamente -->
<a href="/operaciones" class="btn btn-link px-0 text-start text-primary">
    Ver soluciones <i class="fa fa-arrow-right ms-1"></i>
</a>
```

### Ventajas de esta solución:
1. **Seguridad Absoluta:** Oculta el enlace complejo del `LinkPlugin` defectuoso. Odoo ahora te muestra el cuadro de diálogo de "Estilo de Botón" (Button Style) en el panel derecho en lugar del selector de color de texto.
2. **UX sin Cambios:** Gracias a la clase `btn-link px-0 text-start`, visualmente el botón luce exactamente igual a un texto plano para el usuario final del sitio web. No hay bordes ni fondos como en un botón normal.
3. **Escalabilidad:** Permite inyectar CSS avanzado (como `.stretched-link` o animaciones de hover `scale()`) sin que el editor nativo sobrescriba los colores durante su análisis.
