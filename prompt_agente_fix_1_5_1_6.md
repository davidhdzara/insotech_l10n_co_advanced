# Prompt para Corrección de Hallazgos 1.5 y 1.6 (insotech_core)

Copia y pega el siguiente texto al agente de desarrollo:

***

**Actúa como un desarrollador experto de Odoo 19 especializado en calidad de código y estándares OCA.**

Tu objetivo es corregir **2 hallazgos menores** detectados en la auditoría del módulo `insotech_core` dentro del repositorio `insotech_l10n_co_advanced`. No debes modificar ningún archivo de la carpeta `insotech_core/models/` ni `insotech_core/views/`, esos ya están auditados y aprobados.

### Contexto del Proyecto
- **Repositorio:** `git@github.com:davidhdzara/insotech_l10n_co_advanced.git`
- **Versión Odoo:** 19
- **Módulos existentes:** `insotech_core` (motor de licenciamiento SaaS)
- **Módulos futuros:** `insotech_l10n_co_advanced` (facturación electrónica DIAN)
- **Licencia:** OPL-1 (Propietaria)
- **Autor:** Insotech (`www.insotech.it`)

---

### Tarea 1.5: Corregir el `README.md` raíz del repositorio

**Archivo:** `/README.md` (en la raíz del repositorio)

**Problema:** El README actual hace referencia a Odoo **18** y a un módulo llamado `l10n_co_dian_advanced` que **no existe** en el repositorio. Esto genera confusión y no refleja la arquitectura real del proyecto.

**Qué debe contener el nuevo README (reescríbelo completo):**

1. **Título:** `Insotech — Localización Colombiana Avanzada para Odoo`
2. **Descripción:** Explica que este repositorio contiene los módulos comerciales de Insotech para la localización colombiana avanzada en Odoo 19 (con port futuro a 18). Debe mencionar que resuelve las limitaciones críticas de la localización nativa (`l10n_co`), específicamente:
   - Protección de consecutivos de resolución DIAN (cero huecos por rechazos).
   - Motor de licenciamiento SaaS con período de gracia de 72h.
   - Autocompletado de RUT/NIT (futuro).
3. **Tabla de Módulos:** Una tabla markdown con los módulos del repositorio:

   | Módulo | Estado | Descripción |
   |---|---|---|
   | `insotech_core` | ✅ Disponible | Motor de licenciamiento SaaS |
   | `insotech_l10n_co_advanced` | 🚧 En desarrollo | Facturación electrónica DIAN segura |

4. **Versiones Soportadas:**

   | Versión Odoo | Estado |
   |---|---|
   | 19.0 | ✅ Desarrollo activo |
   | 18.0 | ⏳ Port planificado |

5. **Instalación:** Referencia breve a `Documentacion/insotech_core/GUIA_DESPLIEGUE.md` para instrucciones detalladas.
6. **Licencia:** OPL-1 (Odoo Proprietary License). Todos los derechos reservados por Insotech.
7. **Contacto:** `www.insotech.it`

**Estilo:** Profesional, conciso, en español. Usa markdown limpio con tablas y badges si es posible.

---

### Tarea 1.6: Crear archivo `security/ir.model.access.csv`

**Archivo a crear:** `insotech_core/security/ir.model.access.csv`

**Contexto:** El módulo `insotech_core` solo hereda modelos existentes (`res.company` y `res.config.settings`), por lo tanto **no necesita reglas de acceso propias**. Sin embargo, por buena práctica OCA y para evitar warnings en los logs de Odoo, debemos:

1. Crear la carpeta `insotech_core/security/` si no existe.
2. Crear el archivo `ir.model.access.csv` con solo la línea de encabezado:
   ```csv
   id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
   ```
   (Solo el header, sin filas de datos, ya que no hay modelos nuevos que proteger.)

3. **Registrar** este archivo en el `__manifest__.py` de `insotech_core`:
   - Añadir `'security/ir.model.access.csv'` al listado `'data'` del manifiesto, **antes** de las vistas.

**Resultado esperado del `__manifest__.py` tras la edición:**
```python
'data': [
    'security/ir.model.access.csv',
    'views/res_config_settings_views.xml',
],
```

---

### Instrucciones Finales
- **No modifiques** `models/res_company.py` ni `views/res_config_settings_views.xml`. Están auditados y aprobados.
- Verifica que el módulo siga siendo instalable tras tus cambios (que no haya errores de sintaxis en el manifest ni en el CSV).
- Haz un único commit con el mensaje: `[FIX] insotech_core: corregir README raíz y agregar security/ir.model.access.csv`

***
