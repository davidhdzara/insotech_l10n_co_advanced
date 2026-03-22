---
name: Desarrollo Frontend OWL en Odoo V19
description: Guía especializada para el desarrollo de componentes reactivos y dinámicos utilizando Odoo Web Library (OWL) y el nuevo sistema de "Interactions" en Odoo V19.
---

# Desarrollo Frontend Avanzado con OWL en Odoo V19

Esta skill está diseñada para complementar el desarrollo de themes y módulos en Odoo V19, enfocándose puramente en la interactividad avanzada y reactividad ofrecida por **OWL (Odoo Web Library)**, el framework frontend oficial de Odoo.

## 1. El Nuevo Sistema de "Interactions" (V19)

Odoo V19 introduce el sistema de **"Interaction"**, reemplazando progresivamente el uso antiguo de `public.Widget` (jQuery-based) para comportamientos de frontend adheridos a elementos del DOM.

*   **¿Qué es?**: Un mecanismo para adjuntar lógicas impulsadas por OWL a selectores CSS específicos en la vista web.
*   **¿Cómo integrarlo?**:
    En lugar de extender `public.Widget`, define una **Interaction** y regístrala en el registry correspondiente (usualmente `@web/public/public_widget_registry` o dependencias del nuevo sistema de interacciones importado de `@web/...`).
*   Esto permite un encapsulamiento más limpio de templates y lógica OWL nativa con manejo automático del ciclo de vida.

## 2. Desarrollo de Componentes OWL: Reglas Clave

Al construir un componente OWL para tu theme (ej. un mini-carrito reactivo, un filtro de catálogo asíncrono, etc.):

*   **Inicialización (`setup` vs `constructor`)**: Nunca sobrescribas el `constructor()` en JavaScript cuando construyas un componente OWL para Odoo, ya que es incompatible con múltiples mecanismos del framework. Toda inicialización, declaración de hooks o inyección de servicios debe realizarse rigurosamente dentro del método `setup()`.
*   **Gestión del Estado (`useState`)**: Para que la interfaz reaccione a cambios de datos (Data Binding), utiliza el hook `useState`. Cualquier mutación directa a una variable fuera de `useState` no desencadenará un re-render (Virtual DOM).
*   **Nomenclatura de Plantillas (XML)**: Utiliza siempre el prefijo del módulo en el nombre de la plantilla para evitar colisiones: `t-name="nombre_del_modulo.NombreDelComponente"`.

## 3. Organización y Performance

Los datasets en Odoo pueden crecer rápidamente (ej. e-commerce con miles de productos). La performance del frontend es crítica.

*   **Division de Archivos**: Mantén tus componentes estructurados por lógica de dominio. Ejemplo: `my_component.js`, `my_component.xml` y `my_component.scss` para cada entidad (ej. `ProductFilter`).
*   **Re-Renderizados Redundantes**: Diseña tus estados (`useState`) y la estructura de componentes dividiendo componentes "padres" e "hijos" correctamente, de manera que un cambio menor en un dato no obligue a OWL a re-renderizar un componente masivo completo, usando "DOM diffing" eficientemente.
*   **Componentes Genéricos**: Antes de desarrollar selectores personalizados, date pickers o modales desde cero con OWL puro, importa y reutiliza los componentes genéricos (Generic Components) ya provistos por Odoo en `@web/core/ui/...` y otros directorios del framework base.

## 4. Estructura de Registro V19

Siempre asegúrate de registrar tu componente o servicio en la categoría (registry) correcta en el lado del cliente.
Dependiendo de si el componente OWL pertenece a la interfaz del web client (backend) o a la página pública (sitio web), el método de inicialización e inyección cambia:

*   Por lo general, en websites/themes, los componentes OWL de alto grado deben inyectarse al DOM a través del nuevo interaction system (o enganchándose usando `amount/mountComponent`) sobre un selector específico una vez que el DOM de la página está listo.

---
## Directiva de Acción

Cuando debas crear lógicas complejas de UI (Reactividad, llamadas AJAX, modales dinámicos):
1. **NO** utilices jQuery. Su uso está obsoleto en el frontend moderno de Odoo V19.
2. Usa **Interactions** (OWL-powered) para atar comportamientos a nodos del DOM del theme.
3. Respeta el método `setup()` y evita el `constructor`.
