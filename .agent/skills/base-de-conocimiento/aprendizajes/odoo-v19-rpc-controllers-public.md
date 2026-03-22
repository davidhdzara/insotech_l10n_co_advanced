---
title: "Creación de Controladores RPC Públicos en Odoo V19"
date: "2026-03-09"
description: "Guía para exponer endpoints HTTP/RPC para usuarios anónimos (website) y conectarlos con modelos del backend de Odoo."
---

# Controladores RPC y Formularios Públicos en Odoo V19

Cuando construyes widgets de frontend (ej. un bot, un formulario de contacto custom, una calculadora) usando JavaScript / OWL, y usas `rpc("/mi/ruta", {...})`, necesitas crear toda la estructura de backend para recibir, procesar y guardar esa información en la base de datos de Odoo.

De acuerdo a nuestra [Estructura Completa de un Módulo Odoo](../odoo-v19-buenas-practicas/SKILL.md), esto requiere la creación de carpetas clave: `controllers`, `models` y `security`.

## 1. El Controlador (`controllers/main.py`)

El controlador es la puerta de entrada HTTP/RPC genérica.

**Mejores Prácticas:**
*   **Importaciones:** Importar `http` de `odoo`.
*   **Ruta (`@http.route`)**:
    *   `auth="public"`: Obligatorio si el widget puede ser usado por visitantes web no logueados (Anónimos). En Odoo, el usuario anónimo corre bajo el entorno Public.
    *   `type="json"`: Obligatorio cuando el llamado desde JS proviene de `rpc()`, pues este envía y recibe un payload de datos en formato JSON.
    *   `csrf=False`: A veces necesario en llamados API externos o JS reactivos puros ajenos a vistas de portal tradicionales. Sin embargo, lo ideal es enviar el token del CSRF si el formulario se renderizó en Odoo, o evitar colocar `csrf=False` a menos que sea 100% necesario por problemas de *CORS* o arquitectura PWA.
*   **Gestión de Errores**: Siempre atrae (`try...except`) errores generados por validaciones o base de datos y devuélvelos en formato JSON seguro: `return {'success': False, 'error': str(e)}`. Odoo no crasheará y el widget frontend podrá mostrar un lindo mensaje de error.
*   **Sudo (`sudo()`)**: Como la ruta es pública, el ORM negará la creación de registros en la base de datos (ej. crear un CRM Lead) a un visitante anónimo. Para saltarnos la seguridad en este endpoint delimitado, debemos invocar `request.env['modelo'].sudo().create(...)`.

### Ejemplo Práctico:

```python
from odoo import http
from odoo.http import request

class InsobotController(http.Controller):

    @http.route('/insobot/lead/create', type='json', auth='public', website=True)
    def create_lead_from_insobot(self, **kw):
        # 1. Recuperar los datos del Request (enviados desde insobot_widget.js)
        name = kw.get('name')
        email = kw.get('email')
        phone = kw.get('phone')
        intent = kw.get('intent')

        if not name or not email:
            return {'success': False, 'error': 'Faltan campos requeridos'}

        try:
            # 2. Uso del SUPERUSUARIO (sudo) para crear el registro
            # El usuario público no tiene permisos para escribir en crm.lead
            request.env['crm.lead'].sudo().create({
                'name': f'Prospecto Bot: {name}',
                'contact_name': name,
                'email_from': email,
                'phone': phone,
                'description': f'Interesado en: {intent}',
            })
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': 'No se pudo crear el lead: ' + str(e)}
```

## 2. Inscribiendo la Estructura en el Módulo

### `__init__.py` Raíz
Asegúrate de que en la raíz de tu módulo, el archivo `__init__.py` posea la instrucción para cargar la carpeta del controlador:
```python
from . import controllers
```

### `controllers/__init__.py`
Asegúrate de importar el archivo:
```python
from . import main
```

## 3. Seguridad y Archivos Huérfanos
Los controladores **no** se registran en el `__manifest__.py`. Solo Python debe encargarse de cargarlos a través de los archivos `__init__.py`. 
A diferencia de los archivos estáticos de JavaScript o CSS, que sí o sí deben ir en el arreglo de `assets` o `data`.
