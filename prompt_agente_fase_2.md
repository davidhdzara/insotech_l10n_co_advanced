# Prompt para Implementación de la Fase 2: Facturación Segura DIAN (Odoo 19)

Copia y pega el siguiente texto al agente de desarrollo:

***

**Actúa como un desarrollador experto de Odoo 19 especializado en localizaciones latinoamericanas y facturación electrónica colombiana (DIAN).**

Tu objetivo es construir el módulo `insotech_l10n_co_advanced` para Odoo 19, que resuelve el problema crítico de **pérdida de consecutivos de resolución DIAN** cuando una factura electrónica es rechazada.

---

## PASO 0 — OBLIGATORIO: LEE ANTES DE ESCRIBIR CÓDIGO

**Antes de escribir una sola línea de código**, debes leer todos estos archivos en orden. Contienen la arquitectura, aprendizajes técnicos de Odoo 19, y decisiones de negocio ya tomadas que NO debes contradecir:

### Aprendizajes Técnicos (Lecciones aprendidas que evitarán errores)
1. `Documentacion/aprendizajes/odoo_sh_deployment.md` — Reglas de addons_path, submódulos, vistas de Ajustes en Odoo 19 (xpaths que SÍ y NO funcionan), y flujos de push.

### Documentación del Módulo `insotech_core` (YA CONSTRUIDO — NO LO MODIFIQUES)
2. `Documentacion/insotech_core/README.md` — Arquitectura, campos, método `_validate_and_report_license()`, diagrama de flujo, payload y respuestas.
3. `Documentacion/insotech_core/GUIA_DESPLIEGUE.md` — Cómo se instala en Odoo.sh, On-Premise y Docker.

### Código fuente del módulo `insotech_core` (SOLO LECTURA — NO LO MODIFIQUES)
4. `insotech_core/models/res_company.py` — Lee el código completo. Tu módulo va a invocar el método `_validate_and_report_license()` que vive aquí. Entiende sus retornos (`True`/`False`) y cómo incrementar `insotech_usage_count`.

### Documentación Base del Proyecto (Contexto de negocio)
5. `Documentacion/Información base/01_Paso_a_Paso_Facturacion_Electronica.md` — Flujo completo de habilitación DIAN.
6. `Documentacion/Información base/02_Localizacion_Colombia_Odoo18_sh.md` — Capacidades nativas de la localización.
7. `Documentacion/Información base/04_Limitaciones_Localizacion_Colombia.md` — Los problemas que este módulo resuelve.
8. `Documentacion/Información base/05_Novedades_Resoluciones_DIAN_2026.md` — Normativa vigente.

Todos los archivos están relativos a la raíz del repositorio: `/home/david/odoo-projects/insotech_l10n_co_advanced/`

---

## CONTEXTO TÉCNICO

### Arquitectura del Proyecto
El proyecto tiene **2 módulos** que viven en la raíz del mismo repositorio:

```
insotech_l10n_co_advanced/         ← Repositorio raíz
├── insotech_core/                 ← ✅ YA CONSTRUIDO (Fase 1) — NO TOCAR
│   ├── __manifest__.py
│   ├── models/res_company.py      ← Método _validate_and_report_license()
│   └── views/res_config_settings_views.xml
├── insotech_l10n_co_advanced/     ← 🚧 TÚ VAS A CONSTRUIR ESTO (Fase 2)
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── account_move.py
│   └── views/
│       └── account_move_views.xml
└── Documentacion/
```

### Cómo funciona `insotech_core` (lo que YA existe)
El módulo `insotech_core` añade a `res.company`:
- `insotech_license_token` (Char) — Token SaaS del cliente.
- `insotech_usage_count` (Integer) — Contador de facturas emitidas.
- `insotech_last_successful_ping` (Datetime) — Última validación exitosa.

Y el método `_validate_and_report_license()` que:
- Envía POST a `https://www.insotech.it/insotech/api/v1/verify`
- Retorna `True` si la licencia es válida (o si estamos bajo período de gracia de 72h).
- Retorna `False` si la licencia está `blocked`, `exhausted`, o el grace period expiró.

---

## TAREAS A IMPLEMENTAR

### Tarea 2.1 — Estructura del Módulo `insotech_l10n_co_advanced`

Crea la carpeta `insotech_l10n_co_advanced/` (dentro de la raíz del repositorio, al mismo nivel que `insotech_core/`) con la siguiente estructura:

```
insotech_l10n_co_advanced/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv
├── models/
│   ├── __init__.py
│   └── account_move.py
└── views/
    └── account_move_views.xml
```

**`__manifest__.py`:**
```python
{
    'name': 'Insotech — Localización Colombiana Avanzada',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Protección de consecutivos DIAN y facturación electrónica segura para Colombia',
    'description': """
        Extiende la localización nativa colombiana para proteger los consecutivos
        de resolución DIAN contra rechazos técnicos y errores de datos.
    """,
    'author': 'Insotech',
    'website': 'https://www.insotech.it',
    'depends': ['account', 'l10n_co_edi', 'l10n_co_dian', 'insotech_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
```

> **IMPORTANTE sobre las dependencias:** `l10n_co_edi` y `l10n_co_dian` son los módulos nativos de Odoo 19 para la facturación electrónica colombiana. Si al investigar el código fuente de Odoo 19 descubres que estos módulos tienen nombres técnicos diferentes (ej. se fusionaron o renombraron), adapta las dependencias según la realidad del código fuente de Odoo 19. No inventes dependencias que no existan.

**`security/ir.model.access.csv`:**
Solo el header (no hay modelos nuevos, solo herencias):
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

---

### Tarea 2.2 — Secuencia Provisional `PRE-INV` (Interceptar `_post()`)

**Archivo:** `insotech_l10n_co_advanced/models/account_move.py`

Hereda `account.move` y sobreescribe el flujo de confirmación para que las facturas de venta electrónicas colombianas **NO consuman el consecutivo de la resolución DIAN** al momento de confirmar.

**Lógica requerida:**

1. **Antes de todo**, investiga el código fuente de Odoo 19 para entender:
   - Cómo funciona `_post()` en `account.move` (o si en Odoo 19 cambió a `action_post`).
   - En qué momento exacto Odoo asigna el `name` (número de secuencia) a la factura.
   - Cómo funciona el sistema EDI de Colombia (`l10n_co_dian`) en Odoo 19: qué método envía el XML a la DIAN y cómo se recibe el `ApplicationResponse`.

2. **Implementa la interceptación:**
   - Cuando se confirma una factura de venta (`move_type in ('out_invoice', 'out_refund')`) cuyo diario está habilitado para EDI colombiano:
     - Asigna un nombre temporal con formato `PRE-INV/%(year)s/%(seq)05d` (ej. `PRE-INV/2026/00001`) usando una `ir.sequence` propia del módulo (deberás crearla en un archivo `data/ir_sequence_data.xml`).
     - Ejecuta el `super()._post()` normalmente para asentar la contabilidad.
     - **PERO intercepta la asignación del nombre legal** para que NO consuma el `ir.sequence` del diario (el consecutivo de la resolución DIAN).
   - Para facturas que NO sean EDI colombiano, deja pasar el flujo normalmente sin intervenir.

3. **Alternativa técnica (elige la mejor):**
   Si la interceptación de `_post()` resulta demasiado invasiva o frágil en Odoo 19, una alternativa válida es:
   - Dejar que `_post()` funcione normalmente (que asigne el nombre del diario).
   - Inmediatamente después, **renombrar** el `name` de la factura al temporal `PRE-INV/...` y **devolver** el número al `ir.sequence` (decrementando `number_next_actual`).
   - Documentar claramente si usas este enfoque y por qué.

---

### Tarea 2.3 — Mutación a Secuencia Legal (`FE-`) tras Aceptación DIAN

**Archivo:** El mismo `account_move.py`

Cuando el proceso EDI de Odoo envía la factura a la DIAN y recibe un `ApplicationResponse` con estado **Aceptado**:

1. **Toma el siguiente número** del `ir.sequence` oficial del diario (el que tiene el prefijo de la resolución DIAN, ej. `FE-`).
2. **Reemplaza** el `name` temporal (`PRE-INV/2026/00001`) por el definitivo (`FE-845`).
3. **Incrementa** el campo `insotech_usage_count` de `res.company` en +1:
   ```python
   self.company_id.sudo().write({
       'insotech_usage_count': self.company_id.insotech_usage_count + 1
   })
   ```

**Si la DIAN rechaza:**
- La factura conserva su nombre temporal `PRE-INV/2026/00001`.
- El error de rechazo se registra en el Chatter de la factura.
- El usuario puede corregir el error (ej. arreglar el NIT del cliente) y volver a intentar el envío.
- **NINGÚN consecutivo de la resolución DIAN se ha perdido.**

**Investigación necesaria:** Debes encontrar en el código fuente de Odoo 19 el punto exacto donde el módulo `l10n_co_dian` procesa la respuesta de la DIAN. Puede ser un método como `_process_response()`, `_l10n_co_edi_process_response()`, o similar. Herédalo para inyectar la lógica de mutación.

---

### Tarea 2.4 — Bloqueo por Licencia SaaS

**Archivo:** El mismo `account_move.py`

Antes de permitir el envío del XML a la DIAN, valida la licencia:

```python
# Antes de enviar a la DIAN
company = self.company_id
if not company._validate_and_report_license():
    raise UserError(
        "Su licencia Insotech no está activa o ha expirado. "
        "Por favor, contacte a soporte en www.insotech.it para renovarla."
    )
```

Este chequeo debe ocurrir **justo antes** de la llamada HTTP al webservice de la DIAN, no al confirmar la factura. Así, si la licencia expira, el cliente puede seguir creando borradores y confirmando facturas internamente, pero no podrá transmitirlas electrónicamente.

---

## REGLAS ABSOLUTAS (NO NEGOCIABLES)

1. **NUNCA modifiques archivos de `insotech_core/`.** Ese módulo está auditado y cerrado.
2. **NUNCA modifiques código nativo de Odoo** (`l10n_co_dian`, `l10n_co_edi`, `account`). Siempre usa `_inherit`.
3. **NO seas invasivo con las vistas.** Solo usa `xpath` para inyectar elementos nuevos, nunca reemplaces vistas completas.
4. **INVESTIGA el código fuente real de Odoo 19** antes de asumir nombres de métodos o campos. Los nombres pueden haber cambiado respecto a Odoo 18.
5. **Manejo robusto de errores.** Usa `try/except` donde sea necesario. El módulo no debe crashear Odoo bajo ninguna circunstancia.
6. **Calidad OCA.** PEP8, docstrings, logging con `_logger`.

---

## VISTA XML (Tarea complementaria)

**Archivo:** `insotech_l10n_co_advanced/views/account_move_views.xml`

Inyecta vía `xpath` en la vista formulario de `account.move`:
1. Un **banner de alerta** (widget `alert` o `div` con clase `alert alert-warning`) visible cuando la factura tiene nombre temporal (`PRE-INV`), indicando: *"Esta factura está pendiente de validación por la DIAN. El número definitivo se asignará tras la aceptación."*
2. Un botón **"Reintentar Envío DIAN"** visible solo cuando la factura fue rechazada por la DIAN, para que el usuario pueda corregir y reenviar sin crear una factura nueva.

---

## DOCUMENTACIÓN REQUERIDA

Al finalizar, crea la carpeta `Documentacion/insotech_l10n_co_advanced/` con:
1. `README.md` — Descripción del módulo, arquitectura, flujo de secuencias, campos añadidos.
2. `CHANGELOG.md` — Versión 19.0.1.0.0 con todas las funcionalidades implementadas.

---

## CONVENCIONES

- **Versión:** `19.0.1.0.0`
- **Licencia:** `OPL-1`
- **IDs XML:** Prefijo `insotech_l10n_co_advanced_`
- **Python:** PEP8, docstrings descriptivos
- **Commit message final:** `[ADD] insotech_l10n_co_advanced: protección de secuencias DIAN y validación de licencia SaaS`

***
