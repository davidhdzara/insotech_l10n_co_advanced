# Prompt: Fase 3.5 — Wizard Habilitación DIAN (Scope Reducido)

Copia y pega el siguiente texto al agente:

***

**Actúa como un desarrollador senior de Odoo 19 Enterprise con experiencia en despliegues en Odoo.sh.**

Tu objetivo es crear un wizard SIMPLE y SEGURO para capturar los datos de habilitación DIAN. Este wizard **NO toca la localización nativa** de Odoo. Solo almacena 3 campos que el proceso de certificación requiere.

---

## PASO 0 — OBLIGATORIO

Lee PRIMERO estos archivos de aprendizajes antes de escribir código. Contienen errores reales que ocurrieron en este proyecto:

```
/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/base-de-conocimiento/aprendizajes/
```

Archivos CRÍTICOS a leer:
1. `odoo-v19-ir-cron-numbercall-removed.md` — Campos de ir.cron eliminados en V19
2. `odoo-v19-models-constraint-underscore-prefix.md` — models.Constraint requiere prefijo _
3. `odoo-v19-type-http-vs-jsonrpc-api-rest.md` — type='http' vs 'jsonrpc'
4. `odoo-v19-controller-jsonrpc-search-view-group.md` — Vistas y grupos V19
5. `odoo-v19-sale-subscription-l10n-co-build-fail.md` — Builds fallidos por l10n_co

También lee las skills:
- `.agent/skills/odoo-v19-buenas-practicas/SKILL.md`

---

## ENTORNO DE TRABAJO

### Repositorio y rama

```bash
# Clonar el repo (si no está clonado):
git clone --recurse-submodules --branch dev-fase3.5 git@github.com:davidhdzara/insotech.git

# Si ya está clonado:
cd /home/david/odoo-projects/insotech
git fetch origin
git checkout dev-fase3.5
git pull origin dev-fase3.5
```

**Rama:** `dev-fase3.5`
**Repo:** `davidhdzara/insotech` (privado, Odoo.sh)

---

## SCOPE — QUÉ SÍ Y QUÉ NO

### ✅ LO QUE SÍ DEBE HACER EL WIZARD

Capturar y almacenar estos 3 datos de habilitación DIAN:

| Campo | Tipo | Descripción |
|---|---|---|
| `software_id` | Char | ID del software registrado en el portal DIAN |
| `software_pin` | Char | PIN del software DIAN |
| `test_set_id` | Char | Test Set ID para el proceso de certificación |

Funcionalidad:
- Wizard `TransientModel` con los 3 campos
- Botón "Guardar Configuración" que escribe los valores en `res.company`
- Campo `insotech_dian_config_state` en `res.company` (`not_configured` / `in_progress` / `enabled`)
- Cuando está `enabled`, los campos quedan `readonly`
- Botón "Desbloquear" solo para `account.group_account_manager`

### ❌ LO QUE NO DEBE HACER

- **NO tocar el certificado .p12** — Se configura manualmente en Contabilidad → Ajustes
- **NO activar modos de operación** — Se hace manual
- **NO disparar el proceso de certificación** — Se hace manual
- **NO modificar ningún archivo de `l10n_co_dian`**
- **NO depender de campos de `l10n_co_dian`** en el modelo
- **NO heredar ni extender vistas de módulos de localización**

### ⚠️ REGLA DE ORO

> Este módulo debe poder instalarse y desinstalarse SIN AFECTAR EN ABSOLUTO la localización colombiana nativa de Odoo. Si se desinstala, todo debe quedar exactamente como antes. Cero dependencias con `l10n_co_dian` o `l10n_co`.

---

## ESTRUCTURA DEL MÓDULO

Crear dentro del repo `insotech` (NO en `insotech_l10n_co_advanced`):

```
insotech_dian_wizard/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_company.py            ← Campos de configuración DIAN
├── wizard/
│   ├── __init__.py
│   └── dian_setup_wizard.py      ← TransientModel del wizard
├── views/
│   ├── dian_setup_wizard_views.xml  ← Vista del wizard
│   └── res_config_settings_views.xml ← Campos en Ajustes
├── security/
│   └── ir.model.access.csv
└── __init__.py
```

> **NOTA:** Es un módulo SEPARADO (`insotech_dian_wizard`), NO es parte de `insotech_saas_server`. Son independientes.

---

## MANIFEST

```python
{
    'name': 'Insotech DIAN Setup Wizard',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Wizard simplificado para configuración de habilitación DIAN',
    'author': 'Insotech',
    'website': 'https://www.insotech.it',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/dian_setup_wizard_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
```

**IMPORTANTE:**
- Dependencias: solo `base` y `account`. **NO** `l10n_co_dian`, **NO** `l10n_co`.
- `application: False` — Es un complemento, no una app.

---

## MODELO: `res.company` (extensión)

```python
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    insotech_dian_software_id = fields.Char(
        string="Software ID (DIAN)",
    )
    insotech_dian_software_pin = fields.Char(
        string="Software PIN (DIAN)",
    )
    insotech_dian_test_set_id = fields.Char(
        string="Test Set ID (DIAN)",
    )
    insotech_dian_config_state = fields.Selection(
        [
            ('not_configured', 'Sin Configurar'),
            ('in_progress', 'En Proceso'),
            ('enabled', 'Habilitado'),
        ],
        string="Estado Configuración DIAN",
        default='not_configured',
    )
```

**Prefijo `insotech_dian_`** en todos los campos para evitar colisiones con campos nativos de `l10n_co_dian`.

---

## WIZARD: `insotech.dian.setup.wizard` (TransientModel)

```python
from odoo import fields, models


class InsotechDianSetupWizard(models.TransientModel):
    _name = 'insotech.dian.setup.wizard'
    _description = 'Wizard de Configuración DIAN'

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company,
    )
    software_id = fields.Char(string="Software ID")
    software_pin = fields.Char(string="Software PIN")
    test_set_id = fields.Char(string="Test Set ID")

    def action_save_config(self):
        """Guardar configuración DIAN en la empresa."""
        self.ensure_one()
        self.company_id.write({
            'insotech_dian_software_id': self.software_id,
            'insotech_dian_software_pin': self.software_pin,
            'insotech_dian_test_set_id': self.test_set_id,
            'insotech_dian_config_state': 'in_progress',
        })
        return {'type': 'ir.actions.act_window_close'}
```

---

## VISTA DEL WIZARD

- Formulario simple con los 3 campos
- Botón "Guardar Configuración" en el footer
- Estilo nativo de Odoo (sin CSS custom)
- Si `company.insotech_dian_config_state == 'enabled'`, mostrar banner verde "✅ Configuración habilitada" y campos readonly

---

## VISTA EN AJUSTES

Agregar los campos de configuración DIAN en **Ajustes → Contabilidad** usando `res.config.settings`:

- Crear modelo `res.config.settings` heredado que exponga los campos de `res.company`
- Usar xpath seguro (buscar `//div[@name='account_settings']` o similar)
- **Si el xpath es difícil o frágil, crear un menú propio:** Contabilidad → Configuración → Habilitación DIAN

---

## REGLAS ABSOLUTAS

1. **Build de Odoo.sh DEBE pasar.** Si falla, NO hagas push. Verifica la sintaxis de todos los XML y Python antes.
2. **NO uses campos de `ir.cron` que no existen en V19** (`numbercall`, `state`, `priority`).
3. **NO uses `self.env.cr.commit()`** — Odoo maneja las transacciones.
4. **NO dependas de `l10n_co_dian`** ni de ningún módulo de localización.
5. **Prefijo `insotech_dian_`** en todos los campos custom.
6. **PEP8, docstrings, calidad OCA.**
7. **Verifica el __manifest__.py** con `python -c "import ast; ast.literal_eval(open('insotech_dian_wizard/__manifest__.py').read())"` antes de pushear.

---

## COMMIT Y PUSH

```bash
cd /home/david/odoo-projects/insotech
git add insotech_dian_wizard/
git commit -m "[ADD] insotech_dian_wizard: wizard simplificado para habilitación DIAN"
git push origin dev-fase3.5
```

---

## VERIFICACIÓN

1. El módulo aparece en la lista de Apps en Odoo.
2. Se instala sin errores.
3. Abrir Contabilidad → Configuración → Habilitación DIAN (o donde quede el menú).
4. Completar los 3 campos y guardar.
5. Verificar que los campos se guardaron en la empresa.
6. Verificar que tras marcar como "Habilitado", los campos quedan readonly.
7. **Desinstalar el módulo** y verificar que la contabilidad sigue funcionando normalmente.

***
