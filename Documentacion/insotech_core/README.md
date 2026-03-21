# Insotech Core Licensing Engine

## Descripción General

Módulo base e independiente para Odoo 19 que sirve como **motor de licenciamiento SaaS** para todos los submódulos del ecosistema Insotech. Valida que el cliente tenga una licencia activa antes de permitir el funcionamiento de los módulos dependientes.

- **Nombre técnico**: `insotech_core`
- **Versión**: 19.0.1.0.0
- **Categoría**: Technical Settings
- **Licencia**: OPL-1 (Propietaria)
- **Dependencias**: `base`, `web`
- **Autor**: Insotech

---

## Arquitectura del Módulo

```
insotech_core/
├── __init__.py                  # Importa el paquete models
├── __manifest__.py              # Manifiesto del módulo
├── models/
│   ├── __init__.py              # Importa res_company
│   └── res_company.py           # Modelo principal + Ajustes
└── views/
    └── res_config_settings_views.xml   # Vista de Ajustes
```

---

## Modelos

### 1. `res.company` (Herencia)

Se hereda el modelo `res.company` para añadir los siguientes campos:

| Campo | Tipo | Descripción |
|---|---|---|
| `insotech_license_token` | `Char` | Token de licencia SaaS provisto por Insotech |
| `insotech_usage_count` | `Integer` | Contador de operaciones realizadas desde el último reporte |
| `insotech_last_successful_ping` | `Datetime` | Fecha/hora del último ping exitoso contra la API |

### 2. `res.config.settings` (Herencia)

Se hereda el modelo `res.config.settings` para exponer el campo `insotech_license_token` en la interfaz de Ajustes mediante un campo `related`:

```python
insotech_license_token = fields.Char(
    related='company_id.insotech_license_token',
    readonly=False,
    string="Token de Licencia Insotech"
)
```

---

## Método Principal: `_validate_and_report_license()`

### Propósito
Método que los submódulos dependientes deben invocar para validar que la licencia del cliente está activa antes de ejecutar su lógica de negocio.

### Flujo de Validación

```
┌─────────────────────────┐
│  ¿Tiene token?          │
│  (insotech_license_token)│
└──────────┬──────────────┘
           │
     No ───┤───── return False
           │
     Sí ───▼
┌─────────────────────────┐
│  POST a API Insotech    │
│  https://www.insotech.it│
│  /insotech/api/v1/verify│
│  Timeout: 4 segundos    │
└──────────┬──────────────┘
           │
  ┌────────┴────────┐
  │                 │
200 OK         Error/Timeout
  │                 │
  ▼                 ▼
┌──────────┐  ┌──────────────┐
│ status?  │  │ Período de   │
└────┬─────┘  │ gracia (72h) │
     │        └──────┬───────┘
     │               │
 "active" ──► return True (resetea contadores)
 "blocked" ──► return False
 "exhausted" ──► return False
 otro/error ──► evalúa período de gracia
```

### Período de Gracia (72 horas)

Si la API no responde (timeout, error de red, error HTTP), el sistema **no bloquea inmediatamente** al cliente. En su lugar:

1. Verifica el campo `insotech_last_successful_ping`.
2. Si el último ping exitoso fue **hace menos de 72 horas** → `return True` (permite operar).
3. Si fue **hace más de 72 horas** o es `null` → `return False` (bloquea).

Esto garantiza que una caída temporal del servidor de Insotech no afecte las operaciones del cliente.

### Payload enviado a la API

```json
{
    "token": "TOKEN_DEL_CLIENTE",
    "vat": "NIT_DE_LA_EMPRESA",
    "url": "https://cliente.odoo.com",
    "usage_count": 42,
    "reset_counter": true
}
```

### Respuesta esperada de la API

```json
{
    "status": "active"
}
```

Valores posibles de `status`:
- `active` — Licencia válida y vigente
- `blocked` — Licencia bloqueada manualmente por Insotech
- `exhausted` — Licencia agotada (límite de uso superado)

---

## Vista de Ajustes

La vista hereda `base.res_config_settings_view_form` usando el xpath `//form` con `position="inside"`, creando una sección completamente nueva llamada **"Insotech"** en el panel lateral de Ajustes.

### Ubicación en Odoo
`Ajustes → Insotech → Licenciamiento Insotech`

### Estructura XML

```xml
<app string="Insotech" name="insotech_core">
    <block title="Licenciamiento Insotech">
        <setting>
            <field name="insotech_license_token" placeholder="XXXX-XXXX-XXXX"/>
        </setting>
    </block>
</app>
```

> **Nota sobre Odoo 19**: La vista base de `res.config.settings` en Odoo 19 es un `<form>` vacío. Todas las secciones (General, Ventas, Contabilidad, etc.) son agregadas por vistas heredadas de otros módulos usando `<app>`. Nuestro módulo sigue exactamente este patrón.

---

## Cómo Usan Este Módulo los Submódulos Dependientes

Cualquier submódulo de Insotech que dependa de la licencia debe:

1. Declarar `insotech_core` como dependencia en su `__manifest__.py`:
   ```python
   'depends': ['insotech_core', ...]
   ```

2. Invocar la validación antes de su lógica crítica:
   ```python
   company = self.env.company
   if not company._validate_and_report_license():
       raise UserError("Licencia Insotech no válida. Contacte a soporte.")
   # ... lógica del submódulo ...
   ```

---

## Logging

El módulo utiliza el logger estándar de Python con el nombre del módulo. Los mensajes se registran en los logs de Odoo con los siguientes niveles:

| Nivel | Escenario |
|---|---|
| `ERROR` | Licencia rechazada (`blocked`/`exhausted`) o período de gracia expirado |
| `WARNING` | Timeout, error de red, operando bajo período de gracia, status desconocido |
| `INFO` | (No se usa actualmente, disponible para expansiones futuras) |

Filtro de busqueda en logs: `Insotech:`
