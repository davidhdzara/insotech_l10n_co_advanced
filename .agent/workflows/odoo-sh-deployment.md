---
description: Cómo desplegar módulos Odoo personalizados en Odoo.sh y consideraciones técnicas para Odoo 19
---

# Despliegue de Módulos en Odoo.sh

## Reglas Fundamentales

### 1. Addons Path en Odoo.sh
Odoo.sh configura el addons path como `/home/odoo/src/user`. Odoo escanea **hijos directos** de este path buscando `__manifest__.py`.

Si el módulo NO es hijo directo de `src/user`, **Odoo no lo descubre**.

```
✅ CORRECTO:
src/user/insotech_core/__manifest__.py     ← hijo directo, Odoo lo encuentra

❌ INCORRECTO:
src/user/davidhdzara/repo/insotech_core/__manifest__.py  ← 3 niveles, Odoo NO lo encuentra
```

### 2. Submódulos en Odoo.sh
Al agregar un submódulo desde la interfaz de Odoo.sh:

- El **path** debe ser el nombre del repositorio **SIN carpetas intermedias**.
- ✅ Path correcto: `insotech_l10n_co_advanced`
- ❌ Path incorrecto: `davidhdzara/insotech_l10n_co_advanced`
- Los módulos Odoo dentro del submódulo deben estar EN LA RAÍZ del repositorio submódulo.

Si después de agregar el submódulo el módulo no aparece al buscar en Aplicaciones:
1. Verificar que el path no tenga carpetas intermedias
2. Verificar el log de Odoo: la línea `loading N modules...` debe mostrar N+1
3. Si muestra el mismo N, el módulo NO fue descubierto

### 3. Submódulos Huérfanos
Nunca dejar referencias de submódulos (tipo `160000` en git) sin entrada correspondiente en `.gitmodules`. Verificar con:
```bash
git ls-tree HEAD | grep 160000   # muestra submódulos registrados
cat .gitmodules                   # debe tener entrada para cada uno
```
Si hay discrepancias, eliminar las referencias huérfanas:
```bash
git rm --cached nombre_huerfano
```

### 4. El KILLED en Staging
El estado KILLED en staging de Odoo.sh **no siempre es un error de código**. Significa que el proceso de tests fue terminado por el sistema. Causas posibles:
- OOM (falta de RAM) al correr tests con muchos módulos
- Timeout
- Error real en el código

Para diagnosticar: revisar los **LOGS** del build en Odoo.sh y filtrar por `ERROR`. Si no hay errores, es un problema de recursos.

---

## Vistas de Ajustes en Odoo 19

### Estructura Base
La vista `res.config.settings.view.form` en Odoo 19 (ID: `base.res_config_settings_view_form`) es un `<form>` **vacío**:
```xml
<form string="Settings" class="oe_form_configuration" js_class="base_settings">
</form>
```

Todas las secciones (General, Ventas, Contabilidad, etc.) son agregadas por otros módulos mediante herencia.

### Cómo Agregar una Sección Propia
```xml
<xpath expr="//form" position="inside">
    <app string="Mi Sección" name="mi_modulo">
        <block title="Mi Bloque" name="mi_bloque">
            <setting help="Texto de ayuda" id="mi_setting">
                <label for="mi_campo"/>
                <div class="text-muted">Descripción</div>
                <field name="mi_campo" placeholder="..."/>
            </setting>
        </block>
    </app>
</xpath>
```

> **IMPORTANTE**: El `name` del `<app>` debe coincidir con el nombre técnico del módulo.

### XPaths que NO funcionan en Odoo 19
```xml
<!-- ❌ No existe en la vista base: -->
<xpath expr="//app[@name='general_settings']" position="inside">

<!-- ❌ No existe en la vista base: -->
<xpath expr="//block[@name='main_configuration']" position="after">
```

---

## Flujo de Push a Odoo.sh

### Módulo directo en el repo principal
```bash
# 1. Editar código del módulo
# 2. Commit y push
cd /home/david/odoo-projects/insotech
git add insotech_core/
git commit -m "[ADD/UPD/FIX] insotech_core: descripcion"
git push origin staging_produccion
```

### Módulo en repo separado + submódulo
```bash
# 1. Push al repo del módulo
cd /home/david/odoo-projects/insotech_l10n_co_advanced
git add -A && git commit -m "descripcion" && git push origin master

# 2. Actualizar puntero del submódulo en el repo principal
cd /home/david/odoo-projects/insotech
git submodule update --remote insotech_l10n_co_advanced
git add insotech_l10n_co_advanced
git commit -m "Actualizar submodulo"
git push origin staging_produccion
```

> Si se usa submódulo, SIEMPRE hay que hacer el paso 2 (actualizar puntero). Solo pushear al repo del módulo NO actualiza Odoo.sh.

---

## Repositorios del Proyecto

| Repo | Contenido | Rama principal |
|---|---|---|
| `davidhdzara/insotech` | Repo principal de Odoo.sh (Guapante) | `staging_produccion` |
| `davidhdzara/insotech_l10n_co_advanced` | Módulos Insotech (producto comercial) | `master` |

## Estructura del Repo Principal (Odoo.sh)
```
insotech/ (staging_produccion)
├── insotech_core/          ← Módulo de licenciamiento (copiado directo)
├── theme_insotech/         ← Tema premium
├── Documentos/             ← Plantillas HTML
└── ...
```

## Estructura del Repo del Producto
```
insotech_l10n_co_advanced/ (master)
├── insotech_core/          ← Motor de licenciamiento
├── Documentacion/          ← Documentación técnica
│   └── insotech_core/
│       ├── README.md
│       ├── GUIA_DESPLIEGUE.md
│       └── CHANGELOG.md
└── README.md
```
