# Guía de Despliegue e Instalación — insotech_core

## Requisitos Previos

- Odoo 19 Community o Enterprise
- Acceso de administrador al sistema
- Token de licencia Insotech (provisto al adquirir la licencia)

---

## Instalación según Entorno

### Odoo.sh

**Opción A: Módulo directo en el repositorio del cliente**
1. Copiar la carpeta `insotech_core/` en la raíz del repositorio del cliente en GitHub.
2. Hacer commit y push a la rama correspondiente.
3. Odoo.sh detectará el nuevo módulo automáticamente.
4. Ir a `Aplicaciones → Actualizar lista de aplicaciones → Buscar "insotech"` → Instalar.

**Opción B: Submódulo Git**
1. En Odoo.sh, ir a la rama deseada → botón **Submodule**.
2. **Repository URL**: `git@github.com:davidhdzara/insotech_l10n_co_advanced.git`
3. **Branch**: `master`
4. **Path**: `insotech_l10n_co_advanced` (SIN prefijos adicionales)
5. Hacer clic en **Add Submodule**.
6. Esperar a que el build termine.
7. Ir a `Aplicaciones → Actualizar lista de aplicaciones → Buscar "insotech"` → Instalar.

> **IMPORTANTE**: El path del submódulo debe ser el nombre del repositorio directamente, sin carpetas intermedias. Si se agrega con un path anidado (ej: `usuario/repo`), Odoo no descubrirá los módulos dentro.

### On-Premise (Servidor Propio)

```bash
# 1. Clonar el repositorio en el directorio de addons
cd /opt/odoo/custom-addons/
git clone git@github.com:davidhdzara/insotech_l10n_co_advanced.git

# 2. Verificar que insotech_core existe
ls insotech_l10n_co_advanced/insotech_core/
# Debe mostrar: __init__.py  __manifest__.py  models  views

# 3. Agregar la ruta al addons_path en odoo.conf
# Editar /etc/odoo/odoo.conf y agregar:
# addons_path = ...,/opt/odoo/custom-addons/insotech_l10n_co_advanced

# 4. Reiniciar Odoo
sudo systemctl restart odoo

# 5. En Odoo: Aplicaciones → Actualizar lista → Buscar "insotech" → Instalar
```

### Docker

```yaml
# docker-compose.yml
services:
  odoo:
    volumes:
      - ./insotech_l10n_co_advanced:/mnt/extra-addons/insotech_l10n_co_advanced
    environment:
      - EXTRA_ADDONS=/mnt/extra-addons/insotech_l10n_co_advanced
```

---

## Configuración Post-Instalación

1. Ir a **Ajustes → Insotech**.
2. En el campo **"Token de Licencia Insotech"**, ingresar el token provisto.
3. Hacer clic en **Guardar**.

---

## Verificación de la Instalación

### Comprobar campos en la base de datos
En modo desarrollador: `Ajustes → Técnico → Estructura de la Base de Datos → Modelos → res.company`

Buscar los campos:
- `insotech_license_token` (Char)
- `insotech_usage_count` (Integer)
- `insotech_last_successful_ping` (Datetime)

### Comprobar la vista de Ajustes
En modo desarrollador: `Ajustes → Técnico → Interfaz de Usuario → Vistas`

Buscar: `res.config.settings.view.form.inherit.insotech.core`

---

## Desinstalación

1. Ir a `Aplicaciones → Buscar "insotech_core"`.
2. Hacer clic en los tres puntos (⋮) → **Desinstalar**.
3. Confirmar.

> **Nota**: Si hay otros módulos que dependen de `insotech_core`, Odoo pedirá desinstalarlos primero.

---

## Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| Módulo no aparece en Aplicaciones | No está en el addons_path | Verificar la ruta en `odoo.conf` o la estructura del submódulo |
| Build KILLED en Odoo.sh | Path del submódulo incorrecto o submódulos huérfanos | Usar path directo sin carpetas intermedias |
| "Token de Licencia" no aparece en Ajustes | Módulo no instalado | Instalar desde Aplicaciones |
| Error al guardar token | Permisos insuficientes | El usuario debe ser administrador |
