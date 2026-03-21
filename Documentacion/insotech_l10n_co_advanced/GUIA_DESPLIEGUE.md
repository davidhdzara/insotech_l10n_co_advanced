# Guía de Despliegue — insotech_l10n_co_advanced

## Requisitos Previos

- Odoo 19 **Enterprise** (no Community — requiere `l10n_co_dian`)
- Módulos nativos instalados: `l10n_co`, `l10n_co_dian`, `l10n_co_edi`
- Módulo `insotech_core` instalado y con token de licencia configurado
- Acceso de administrador al sistema

---

## Instalación en Odoo.sh

### Método recomendado: Copia directa

> **⚠️ NO usar submódulos** para repos multi-módulo. Odoo.sh solo busca `__manifest__.py` en hijos directos de `src/user/`.

```bash
# 1. Clonar el repo producto (si no existe localmente)
git clone --branch 19.0 git@github.com:davidhdzara/insotech_l10n_co_advanced.git

# 2. Clonar el repo de Odoo.sh del cliente
git clone --branch staging_produccion git@github.com:davidhdzara/insotech.git

# 3. Copiar el módulo a la raíz del repo de Odoo.sh
cp -r insotech_l10n_co_advanced/insotech_l10n_co_advanced insotech/

# 4. Verificar que __manifest__.py sea hijo directo
ls insotech/insotech_l10n_co_advanced/__manifest__.py
# ✅ Debe existir

# 5. Commit y push
cd insotech
git add insotech_l10n_co_advanced/
git commit -m "[ADD] insotech_l10n_co_advanced: localización colombiana avanzada"
git push origin staging_produccion
```

### Resultado esperado en Odoo.sh:
```
src/user/
├── insotech_core/__manifest__.py              ← hijo directo ✅
├── insotech_l10n_co_advanced/__manifest__.py  ← hijo directo ✅
└── otros_modulos/
```

### Post-push
1. Esperar a que el build de Odoo.sh termine exitosamente.
2. Ir a **Aplicaciones** → quitar filtro "Aplicaciones".
3. Buscar `insotech` → hacer clic en **Activar** en "Localización Colombiana Avanzada".

---

## Instalación On-Premise

```bash
# 1. Clonar el repo en el directorio de addons custom
cd /opt/odoo/custom-addons/
git clone --branch 19.0 git@github.com:davidhdzara/insotech_l10n_co_advanced.git

# 2. Agregar al addons_path en odoo.conf
# addons_path = ...,/opt/odoo/custom-addons/insotech_l10n_co_advanced

# 3. Reiniciar Odoo
sudo systemctl restart odoo

# 4. En Odoo: Aplicaciones → Actualizar lista → Buscar "insotech" → Instalar
```

---

## Actualización del Módulo

Cuando se despliegan cambios de código:

1. **Copiar archivos actualizados** al repo de Odoo.sh (o pull en on-premise).
2. **Commit y push** a la rama correspondiente.
3. En Odoo: **Aplicaciones** → buscar `insotech_l10n_co_advanced` → **tres puntos (⋮)** → **Actualizar**.

> **⚠️ Importante**: El simple reinicio del servidor **NO** crea columnas nuevas ni aplica cambios en vistas. Se debe ejecutar el **Actualizar** (upgrade) del módulo para que los cambios en modelos y vistas se apliquen a la base de datos.

---

## Verificación Post-Instalación

### 1. Verificar campos en la BD
En modo desarrollador: `Ajustes → Técnico → Estructura de la BD → Modelos → account.move`

Buscar:
- `insotech_dian_status` (Selection)
- `insotech_pre_inv_name` (Char)
- `insotech_reserved_dian_name` (Char)
- `insotech_is_co_edi` (Boolean)

### 2. Verificar vista
En modo desarrollador: `Ajustes → Técnico → Interfaz de Usuario → Vistas`

Buscar: `account.move.form.inherit.insotech.l10n_co_advanced`

### 3. Verificar secuencia
En modo desarrollador: `Ajustes → Técnico → Secuencias`

Buscar: `Insotech: Factura Pre-Validación DIAN` (código: `insotech.pre.inv`)

### 4. Test funcional
1. Crear una factura de cliente (empresa colombiana).
2. Confirmar → debe aparecer `PRE-INV/2026/NNNNN` y banner amarillo.
3. Hacer clic en "Forzar Aceptación DIAN" → debe restaurar `INV/2026/NNNNN`.

---

## Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| Módulo no aparece en Aplicaciones | Path de 2 niveles | Copiar módulo directo a raíz del repo |
| Error xpath al instalar | Nombres de elementos cambiaron en Odoo 19 | Usar xpaths seguros: `//header`, `//sheet` |
| Banner no aparece | Campos invisibles declarados dentro de `<sheet>` | Moverlos a `//header position="before"` |
| Nuevas facturas salen como PRE-INV (no INV) | SequenceMixin contaminado | Verificar override de `_get_last_sequence_domain()` |
| HTML crudo en chatter | Usando `_()` en vez de `Markup()` | Usar `from markupsafe import Markup` |
| Error `column does not exist` | Módulo actualizado pero no upgradeado | Aplicaciones → tres puntos → Actualizar |
| Build KILLED en Odoo.sh | OOM, timeout, o error de código | Revisar logs filtrados por `ERROR` |

---

## Desinstalación

1. Ir a `Aplicaciones → Buscar "insotech_l10n_co_advanced"`.
2. Tres puntos (⋮) → **Desinstalar**.
3. Confirmar.

> **Advertencia**: La desinstalación eliminará los campos `insotech_*` de la tabla `account_move`. Las facturas que ya tengan nombre `PRE-INV` **no serán renombradas automáticamente**. Asegúrese de que todas las facturas pendientes hayan sido aceptadas antes de desinstalar.
