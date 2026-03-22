# Uso de Entidades HTML y XMLSyntaxError (Odoo V19 lxml strict parser)

**Contexto:**
Durante el desarrollo de vistas XML (`<template>`) para temas en Odoo V19, es fácil copiar código directamente desde editores HTML o navegadores web que usan entidades HTML nativas para símbolos visuales (ejemplo: usar `&bull;` para el punto •). 

Sin embargo, tras inyectar dicho código y reiniciar Odoo, el servicio completo se desploma en la fase de registro de base de datos con este error:

```python
2026-03-07 17:38:17,341 4 ERROR insotech-feature odoo.registry: Failed to load registry
2026-03-07 17:38:17,343 4 CRITICAL insotech-feature odoo.service.server: Failed to initialize database
(...)
lxml.etree.XMLSyntaxError: Entity 'bull' not defined, line 14, column 45
odoo-bin process returned error code 255. 
```

## Aprendizaje: El Parser de LXML no conoce Entidades HTML 

Odoo V19 utiliza la librería `lxml.etree` de Python para pre-compilar todos los archivos `.xml` en el módulo. Por diseño, el estándar puro de XML soporta extremadamente pocas entidades (solo cinco principales: `&lt;`, `&gt;`, `&amp;`, `&apos;`, `&quot;`). El resto de las entidades HTML como `&bull;` o `&nbsp;` o `&copy;` no existen sin un DTD específico, por lo que el parser aborta la lectura entera.

### Solución / Patrón Estricto: Reemplazar entidades HTML por Códigos Unicode 

Para cualquier decoración textual que originalmente usarías con un "amperstand notation" en HTML puro, **debes usar** su equivalente directo en Hexadecimal/Decimal de Unicode que Odoo puede codificar sin problema, o derechamente el glifo inyectado.

**Incorrecto (XMLSyntaxError y Crash del Server) ❌**
```xml
<!-- En un archivo theme_insotech.../mi_snippet.xml -->
<div class="fw-bold">
    Reinventa &bull; Automatiza &bull; Evoluciona
</div>
```

**Correcto (Aprobado por el Parser lxml de Odoo V19) ✅**
```xml
<!-- Usando el equivalente numérico Unicode Decimal o Hex -->
<div class="fw-bold">
    Reinventa &#8226; Automatiza &#8226; Evoluciona
</div>
```

**Correcto alternativo ✅**
```xml
<!-- Si el archivo XML está correctamente codificado en UTF-8 y se declara al top <?xml version="1.0" encoding="utf-8"?>  -->
<div class="fw-bold">
    Reinventa • Automatiza • Evoluciona
</div>
```

Esta simple práctica evitará "destruir" arranques de base de datos donde una sola viñeta decorativa arroja el temido código de error 255 de Odoo.
