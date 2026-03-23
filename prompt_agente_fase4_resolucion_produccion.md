# Prompt: Fase 4 — Limpieza de Código del Módulo insotech_l10n_co_advanced

Copia y pega el siguiente texto al agente:

***

## ROL

Eres un desarrollador Odoo 19 Enterprise. Trabajas en el módulo `insotech_l10n_co_advanced`.

---

## PASO 0 — LEE ANTES DE TOCAR CÓDIGO

### Skills del proyecto:
1. `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/metodologia-de-trabajo-insotech/SKILL.md`
2. `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/odoo-v19-buenas-practicas/SKILL.md`
3. `/home/david/odoo-projects/insotech_l10n_co_advanced/.agent/skills/base-de-conocimiento/SKILL.md`

### Código del módulo (leer COMPLETO):
4. Todo el directorio: `/home/david/odoo-projects/insotech_l10n_co_advanced/insotech_l10n_co_advanced/`

---

## CONTEXTO

Los errores de la DIAN (401 y 302) que motivaron la creación de código extra ya se resolvieron por **configuración**, no por código:
- Error 401 → El NIT estaba con DV incluido en `vat`. Se corrigió.
- Error 302 → Faltaba "Sincronizar a Producción" en el portal DIAN + desactivar modo "Prueba" en Odoo.

El botón nativo "Volver a cargar la configuración de la DIAN" **ya funciona correctamente**. No necesita intervención de código.

Sin embargo, un agente anterior agregó código innecesario que debe eliminarse.

---

## TAREA ÚNICA: Limpiar código innecesario

Un agente anterior agregó un wizard manual y un botón extra al diario que **NO deben existir**. La filosofía del módulo es: **no agregar campos ni botones a las vistas nativas de Odoo**.

### Archivos a ELIMINAR:

| Archivo | Qué hace | Por qué se elimina |
|---|---|---|
| `wizard/dian_manual_config_wizard.py` | Wizard para ingresar resolución manualmente | Innecesario — Odoo ya tiene campos nativos editables |
| `wizard/dian_manual_config_wizard_views.xml` | Vista del wizard | Innecesario |
| `views/account_journal_views.xml` | Agrega botón "✏️ Configurar Manualmente" al diario | Viola la filosofía del módulo |

### Archivos a REVISAR y LIMPIAR:

| Archivo | Qué revisar |
|---|---|
| `wizard/__init__.py` | Quitar import del wizard eliminado |
| `__init__.py` (raíz) | Quitar import de `wizard` si ya no hay wizards válidos |
| `__manifest__.py` | Quitar referencias a los archivos eliminados de la sección `data` |
| `security/ir.model.access.csv` | Quitar permisos del modelo `l10n_co_dian.manual.config.wizard` si existen |
| `models/account_journal.py` | **Revisar** — tiene un override de `button_l10n_co_dian_fetch_numbering_range` que captura el error 302. Como los errores se resolvieron por configuración, evalúa si este override aporta valor (mensaje amigable) o si debe eliminarse también. Pregúntame antes de decidir. |

### Después de limpiar:

1. Verificar que el módulo compila: `python -m py_compile` de cada `.py`
2. Verificar que `__manifest__.py` no referencia archivos eliminados
3. Verificar que no quedan imports rotos
4. Hacer commit y push

---

## FLUJO DE DESPLIEGUE

```bash
cd /home/david/odoo-projects/insotech_l10n_co_advanced
git checkout 19.0
git add -A
git commit -m "refactor: eliminar wizard manual y botón innecesario del diario DIAN"
git push origin 19.0
```

---

## REGLAS

1. **PEP8 y OCA** — líneas ≤79 chars
2. **NO agregues nada** — esta tarea es solo de ELIMINACIÓN y limpieza
3. **Pregunta** antes de eliminar `models/account_journal.py` — el override del error 302 podría tener valor como mensaje amigable
4. **Commit en español**, descriptivo

---

## CRITERIOS DE ACEPTACIÓN

- [ ] `wizard/dian_manual_config_wizard.py` eliminado
- [ ] `wizard/dian_manual_config_wizard_views.xml` eliminado
- [ ] `views/account_journal_views.xml` eliminado
- [ ] Referencias eliminadas de `__init__.py`, `__manifest__.py`, `security/`
- [ ] Sin imports rotos
- [ ] El módulo compila sin errores
- [ ] Decisión tomada sobre `models/account_journal.py` (mantener override o eliminar)
- [ ] Build pasa en Odoo.sh

***
