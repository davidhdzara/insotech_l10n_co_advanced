# Prompt para Implementación de la Fase 3.5: Wizard Express DIAN + Contador de Resolución

Copia y pega el siguiente texto al agente de desarrollo:

***

**Actúa como un desarrollador senior de Odoo 19 Enterprise con experiencia en UX/UI corporativo. Eres conocido por crear interfaces que se sienten 100% nativas de Odoo — como si Odoo las hubiera construido.**

Tu objetivo es implementar dos features dentro del módulo `insotech_l10n_co_advanced`: un Wizard de configuración express DIAN y un contador visual de resolución. Ambos deben ser estéticamente impecables.

---

## PASO 0 — OBLIGATORIO: LEE ANTES DE ESCRIBIR CÓDIGO

Lee estos archivos en orden:

1. `.agent/skills/odoo-v19-buenas-practicas/SKILL.md` — Convenciones de código Odoo V19
2. `.agent/skills/desarrollo-frontend-owl-odoo-v19/SKILL.md` — OWL y frontend en Odoo V19
3. `Documentacion/aprendizajes/odoo_sh_deployment.md` — Reglas de despliegue y XPaths V19
4. `Documentacion/Información base/07_Guia_Configuracion_DIAN_Odoo19.md` — La guía que el wizard va a automatizar (Parte B, Fases 3-6)
5. `insotech_l10n_co_advanced/__manifest__.py` — Manifest actual
6. `insotech_l10n_co_advanced/models/account_move.py` — Código actual del módulo (los campos ya existentes)
7. `insotech_l10n_co_advanced/views/account_move_views.xml` — Vistas actuales

Todos los archivos están en: `/home/david/odoo-projects/insotech_l10n_co_advanced/`

---

## CONTEXTO DEL PRODUCTO

Este módulo es un producto SaaS comercial. Nuestros clientes son PYMEs colombianas y Partners contables. La UI debe transmitir **profesionalismo y confianza**. Si algo se ve "pegado encima" o "hecho por un freelancer", hemos fallado.

---

## REGLA DE ORO ESTÉTICA

> **Todo lo que construyas debe verse como si lo hubiera diseñado el equipo de UX de Odoo SA.** Usa las mismas clases CSS que Odoo usa internamente. Los mismos patrones de botones, badges, progress bars, y cards. Si no estás seguro de cómo Odoo haría algo, investiga cómo lo hacen componentes similares en otros módulos nativos (como CRM pipeline, Project progress, o Subscription health indicators).

---

## FEATURE 1: Wizard "Configuración Express DIAN"

### Qué es

Un `TransientModel` (wizard) que consolida la configuración de facturación electrónica colombiana en un solo formulario guiado. Reemplaza la necesidad de navegar a 4 secciones diferentes de Ajustes.

### Archivos a crear/modificar

```
insotech_l10n_co_advanced/
├── wizard/
│   ├── __init__.py                          [NUEVO]
│   └── dian_setup_wizard.py                 [NUEVO]
├── views/
│   ├── dian_setup_wizard_views.xml          [NUEVO]
│   └── account_move_views.xml               [MODIFICAR — agregar menú]
├── models/
│   └── res_company.py                       [NUEVO — campo state]
├── security/
│   └── ir.model.access.csv                  [MODIFICAR — agregar ACL del wizard]
└── __manifest__.py                          [MODIFICAR — agregar archivos]
```

### Modelo `insotech.dian.setup.wizard` (TransientModel)

| Campo | Tipo | Descripción |
|---|---|---|
| `company_id` | Many2one → res.company | Empresa a configurar (default: empresa actual) |
| `certificate_file` | Binary | Archivo .p12 subido por el usuario |
| `certificate_filename` | Char | Nombre del archivo (para el widget binary) |
| `certificate_password` | Char | Contraseña del certificado (widget password) |
| `software_id` | Char | Software ID del portal de habilitación DIAN |
| `software_pin` | Char | PIN de software |
| `test_set_id` | Char | Test Set ID para certificación |
| `enable_support_documents` | Boolean | ¿También emitirá Documentos Soporte? |
| `current_step` | Selection | `certificate` / `credentials` / `confirm` / `done` |

### Lógica del Wizard

```
Paso 1 (certificate):
  → El usuario sube el .p12 y escribe la contraseña.
  → Al hacer clic en "Siguiente", el wizard escribe el certificado
    en los campos de l10n_co_dian de la empresa.

Paso 2 (credentials):
  → El usuario ingresa Software ID, PIN, Test Set ID.
  → Al hacer clic en "Siguiente", el wizard configura los
    Modos de Operación (Factura Electrónica + Documento Soporte
    si fue seleccionado) usando los modelos nativos de l10n_co_dian.

Paso 3 (confirm):
  → Resumen de lo configurado con checkmarks verdes.
  → Botón "Iniciar Certificación" que:
    1. Activa el entorno de prueba
    2. Activa el flag de certificación
    3. Dispara el proceso nativo de l10n_co_dian
    4. Actualiza company.insotech_dian_config_state = 'in_progress'

Paso 4 (done):
  → Mensaje de éxito o error según la respuesta de la DIAN.
  → Si éxito: company.insotech_dian_config_state = 'enabled'
```

### Vista del Wizard — Diseño

El wizard debe verse como los wizards nativos de Odoo (ej. `account.setup.bill.wizard`, `base.setup.installer`):

- **Encabezado con pasos:** Usa el patrón de stepper/breadcrumb que Odoo usa en sus wizards de configuración. Investiga `o_wizard_step` o clases similares.
- **Campos con labels descriptivos** y textos de ayuda (`help`).
- **Botones "Anterior" y "Siguiente"** en el footer.
- **Iconos**: `fa-lock` para certificado, `fa-cog` para credenciales, `fa-check-circle` para confirmación.
- **NO uses tabs/pestañas.** Es un flujo lineal paso a paso. Usa `invisible` dinámico por `current_step`.

### Campo `insotech_dian_config_state` en `res.company`

```python
insotech_dian_config_state = fields.Selection([
    ('not_configured', 'Sin Configurar'),
    ('in_progress', 'En Proceso de Certificación'),
    ('enabled', 'Habilitado'),
], default='not_configured', string="Estado Configuración DIAN")
```

### Bloqueo post-habilitación

Cuando `insotech_dian_config_state == 'enabled'`:
- El wizard muestra un mensaje: "✅ Su facturación electrónica está habilitada y configurada. No se requieren cambios."
- Los campos de configuración DIAN en Ajustes de Contabilidad deben mostrarse como `readonly` (inyectar vía xpath).
- Un botón **"🔓 Desbloquear Configuración"** (visible solo para `account.group_account_manager`) con `confirm="¿Está seguro? Desbloquear la configuración podría afectar su facturación electrónica."` que resetea el state a `not_configured`.

### Menú de acceso

Agregar una entrada de menú:
- **Contabilidad → Configuración → Configuración Express DIAN**
- Solo visible si `company.country_id.code == 'CO'`
- Abre el wizard directamente

---

## FEATURE 2: Contador Visual de Resolución DIAN

### Qué es

Un indicador visual en la vista de facturas y en el diario que muestra cuántos números de la resolución DIAN se han consumido y cuántos quedan. Debe ser **elegante, sutil, e integrado** — NO un campo numérico suelto.

### Diseño — INSPIRACIÓN OBLIGATORIA

Antes de implementar, **investiga** cómo Odoo implementa estos indicadores nativos y replica su estética:

1. **Subscriptions → Health indicator** (barra de progreso con colores graduales)
2. **Project → Task progress** (porcentaje con barra circular o lineal)
3. **CRM → Pipeline probability** (badge con porcentaje)
4. **Sales → Subscription renewal count** (badge informativo)

### Ubicación 1: Vista formulario de la factura

Agregar vía xpath en `account_move_views.xml`, **solo visible cuando `insotech_is_co_edi == True`**:

Un **widget de statusbar-style o badge** en la zona del header (después de los banners existentes) que muestre:

```
Resolución DIAN: FE 843 / 5,000  ━━━━━━━━━━━░░░  83% disponible
```

**Reglas de color:**
- **Verde** (>50% disponible): Todo bien
- **Amarillo** (20-50%): Atención, solicitar nueva resolución pronto
- **Rojo** (<20%): Urgente, resolución casi agotada

### Ubicación 2: Vista formulario del diario

**Solo si hay forma no invasiva de hacerlo.** Si el xpath es complejo o frágil, omitir. Mejor una ubicación segura que una bonita que se rompa.

### Implementación técnica

**Campos computados en `account.move`:**

```python
insotech_resolution_used = fields.Integer(
    compute='_compute_insotech_resolution_info',
    string="Números Usados",
)
insotech_resolution_max = fields.Integer(
    compute='_compute_insotech_resolution_info',
    string="Números Autorizados",
)
insotech_resolution_percent = fields.Float(
    compute='_compute_insotech_resolution_info',
    string="% Disponible",
)
```

**Lógica de cómputo:**
- Lee `journal_id.l10n_co_edi_min_range_number` y `journal_id.l10n_co_edi_max_range_number` del diario.
- Calcula cuántos se han consumido contando facturas confirmadas (no PRE-INV) con ese diario.
- Si los campos no existen (diario no DIAN), retorna 0.

**Vista XML:**
Usa las clases CSS nativas de Odoo. Ejemplo de patrón para barra de progreso:

```xml
<div class="d-flex align-items-center gap-2"
     invisible="not insotech_is_co_edi">
    <span class="text-muted small">Resolución DIAN:</span>
    <div class="progress flex-grow-1" style="height: 6px; max-width: 150px;">
        <div class="progress-bar"
             t-att-class="'bg-success' if insotech_resolution_percent > 50
                          else 'bg-warning' if insotech_resolution_percent > 20
                          else 'bg-danger'"
             t-att-style="'width: ' + str(100 - insotech_resolution_percent) + '%'"
             role="progressbar"/>
    </div>
    <span class="badge rounded-pill"
          t-att-class="'text-bg-success' if insotech_resolution_percent > 50
                       else 'text-bg-warning' if insotech_resolution_percent > 20
                       else 'text-bg-danger'">
        <field name="insotech_resolution_used"/> / <field name="insotech_resolution_max"/>
    </span>
</div>
```

> **IMPORTANTE:** Este es un ejemplo de referencia. Investiga los patrones actuales de Odoo 19 antes de copiar esto. Los atributos `t-att-class` y `t-att-style` pueden tener sintaxis diferente en vistas XML de backend. Si no funcionan, usa campos computados auxiliares para el color y el ancho.

### Lo que NO debe ser

- ❌ Un campo numérico aislado ("Usados: 843")
- ❌ Una barra de progreso gigante que ocupe espacio visual
- ❌ Un widget que solo funcione con JavaScript custom complejo
- ❌ Algo que se vea diferente al estilo visual de Odoo

---

## REGLAS ABSOLUTAS

1. **Investiga antes de asumir.** Si no sabes qué clases CSS usa Odoo para progress bars, búscalas en el código fuente de Odoo (`addons/web/static/src/`) o en las vistas XML de módulos nativos (`sale_subscription`, `project`).
2. **XPaths seguros.** Solo `//header`, `//sheet`, `//group`. Nunca xpaths con `@name` que puedan no existir en Odoo 19. (Ver aprendizajes de despliegue).
3. **No toques código existente** de `account_move.py` sin entenderlo completamente. Extiéndelo, no lo reescribas.
4. **PEP8, docstrings, calidad OCA.** Sin excepciones.
5. **TransientModel** para el wizard, no un modelo persistente.
6. **`self.env.cr.commit()` PROHIBIDO** (ver skill de buenas prácticas Odoo V19).
7. **Prueba el xpath** en modo desarrollador antes de dar por terminado.

---

## CONVENCIONES

- **Versión:** Actualizar a `19.0.1.1.0` (minor bump por nueva feature)
- **Commit:** `[ADD] insotech_l10n_co_advanced: wizard express DIAN + contador resolución`
- **IDs XML:** Prefijo `insotech_l10n_co_advanced_`
- **Wizard XML ID:** `insotech_l10n_co_advanced_dian_setup_wizard_form`
- **Menú XML ID:** `insotech_l10n_co_advanced_menu_dian_setup`

---

## VERIFICACIÓN

Antes de terminar:

1. Instalar el módulo en la instancia y verificar que no haya errores de xpath.
2. Abrir el wizard desde **Contabilidad → Configuración → Configuración Express DIAN**.
3. Completar los 3 pasos del wizard con datos dummy.
4. Verificar que tras "habilitación", los campos queden bloqueados.
5. Verificar que el botón "Desbloquear" solo aparezca para admin contable.
6. Crear una factura de venta → verificar que aparece el contador de resolución con la barra correcta.
7. Verificar que el contador **NO** aparece en facturas de diarios sin DIAN.
8. Verificar colores: verde >50%, amarillo 20-50%, rojo <20%.

***
