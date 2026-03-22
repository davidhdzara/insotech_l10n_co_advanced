# Error de Compilación SCSS "Style Error"

**Fecha de Registro:** 2026-03-10
**Contexto del Problema:**
Al intentar cargar el tema de InSoTech (`theme_insotech`), la interfaz entera colapsaba mostrando un modal de alerta o un error 500 en consola indicando: `"Style error. The style compilation failed. This is an administrator or developer error that must be fixed for the entire database before continuing working"`. Además, los estilos del sitio se dejaban de cargar.

## 🚨 El Problema o Error
El compilador nativo de SCSS de Odoo V19 explota cuando encuentra directivas CSS vacías o mal formateadas. Esta rotura interrumpe el proceso global de minificación y empaquetamiento de assets (Los `assets_frontend` o `assets_backend`), dejando a la base de datos sin un archivo base `.css` para servir. 

El error exacto del compilador no siempre dice qué archivo está dañado en el modal, obligando a rastrear el log del servidor o el historial de Git.

## 🔍 Causa Raíz
En este caso, la causa fue una sobrescritura o eliminación parcial de código durante una refactorización de clases utilitarias del Theme en el archivo `theme_insotech/static/src/scss/theme.scss`.
Habían quedado declaradas variables CSS huérfanas:
```scss
.btn_cta {
    background-
    border-
    // Faltaban las terminaciones '-color' o el valor directamente.
}
```

> **NOTA CRÍTICA Odoo.sh:** Este error de sintaxis no es puramente un fallo de renderizado local. Cuando Odoo.sh intenta correr el test de construcción y minificación al procesar el commit (`_assets_frontend`), detecta que el compilador LibSass falla y, en lugar de crashear el servidor completo con un Fatal Error, **Odoo.sh registra la rama con un estado "Warning" (Advertencia en amarillo)**, logrando ocultar el origen a menos que se realice una auditoría manual extensa.

## ✅ Solución Adoptada
1. Rastrear inmediatamente los últimos commits o archivos `.scss` modificados.
2. Completar o purgar las directivas CSS truncadas dándoles sintaxis válida:
```scss
.btn_cta {
    background-color: var(--o-we-color-primary, #003498) !important;
    border: 2px solid var(--o-we-color-primary, #003498) !important;
}
```
3. **Paso crítico post-fix**: Dado que Odoo "cachea" este error para evitar bucles de compilación, no basta con arreglar el código. El usuario debe:
   - Activar el **Modo Desarrollador** (`?debug=1`).
   - Hacer clic en el icono del "Bicho" en la barra superior.
   - Seleccionar **Regenerate Assets Bundles**.
   - (Alternativa externa): Actualizar la aplicación temática desde la vista Apps de Odoo (`-u theme_insotech`).

## 💡 Buenas Prácticas / Cómo evitarlo
- **JAMÁS dejar llaves, puntos o guiones incompletos en SCSS**. Los linters de Python o XML no detectan estos errores de SCSS, por lo que una revisión visual tras un reemplazo masivo (ej. Buscar/Reemplazar) es obligatoria.
- Ante la duda o al trabajar localmente sin editor SCSS, siempre verifica que las reglas compilen localmente antes de hacer push.
