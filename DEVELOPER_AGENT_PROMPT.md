# Prompt de Agente Desarrollador
## Tarea: Construir el módulo `l10n_co_dian_advanced` para Odoo 18

---

## TU ROL
Eres un experto desarrollador de Odoo especializado en localizaciones latinoamericanas. Tu tarea es construir el módulo `l10n_co_dian_advanced` para Colombia, que resuelve el problema crítico de **pérdida de consecutivos DIAN** en la implementación nativa de Odoo 18.

**ANTES DE ESCRIBIR UNA SOLA LÍNEA DE CÓDIGO**, debes leer la siguiente Skill obligatoria del proyecto:
`/home/david/odoo-projects/guapante/.agent/skills/odoo-facturacion-electronica-co/SKILL.md`

---

## CONTEXTO COMPLETO (Lee primero)

Toda la investigación, diseño arquitectónico y decisiones de negocio están documentadas aquí. **Debes leerlos en orden:**

1. `/home/david/odoo-projects/guapante/Plan de trabajo contable/10_Propuesta_Simplicidad_Facturacion.md` — El diseño base "Desacople de Secuencia".
2. `/home/david/odoo-projects/guapante/Plan de trabajo contable/11_Guia_Implementacion_Factura_Simple.md` — El Blueprint técnico paso a paso con los Edge Cases.
3. `/home/david/odoo-projects/guapante/Plan de trabajo contable/12_Roadmap_Fases_Facturacion.md` — El Roadmap de Fases 1 y 2.

---

## ENTREGABLES ESPERADOS (Fase 1 únicamente)

El módulo vive en: `/home/david/odoo-projects/l10n_co_dian_advanced/`
El esqueleto de carpetas y el `__manifest__.py` ya están creados. Debes completar los siguientes archivos:

### 1. `models/account_move.py`
Sobreescribir el método `_post()` con la lógica de Desacople de Secuencia:

```python
class AccountMoveExtended(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        # Para facturas de venta colombianas en diarios EDI habilitados:
        # 1. Verificar si el diario es tipo CO EDI y no está en modo contingencia.
        # 2. Usar el motor nativo de l10n_co_dian para generar el XML en memoria.
        # 3. Hacer POST al webservice DIAN con timeout=8s.
        # 4. Si TimeoutException o ConnectionError → raise UserError (→ Postgres Rollback, 
        #    factura vuelve a Borrador, NINGÚN consecutivo se toca).
        # 5. Si la DIAN rechaza (ApplicationResponse con rejection) → raise UserError con el
        #    motivo específico del rechazo para que el usuario lo corrija.
        # 6. Si la DIAN aprueba → LLAMAR AL super()._post() para que Odoo consuma el ir.sequence
        #    y asigne el nombre legal definitivo (FE-XXX). Estampar el CUFE devuelto.
        #
        # Para facturas en modo contingencia → LLAMAR AL super()._post() directamente
        # usando la secuencia del diario de contingencia (PC-XXX).
        pass
```

### 2. `models/account_journal.py`
Añadir el campo `is_dian_contingency` (Boolean) al diario contable:
```python
class AccountJournalExtended(models.Model):
    _inherit = 'account.journal'
    
    is_dian_contingency = fields.Boolean(
        string='Modo Contingencia DIAN',
        help='Activa para emitir bajo prefijo de contingencia (PC-XXXX) '
             'cuando la plataforma MUISCA esté caída. Las facturas contingentes '
             'serán enviadas a la DIAN automáticamente cuando se desactive.'
    )
    dian_retry_count = fields.Integer(
        string='Intentos Máximos DIAN',
        default=5,
        help='Número máximo de reintentos automáticos del Cron antes de escalar a revisión manual.'
    )
    dian_retry_interval_hours = fields.Integer(
        string='Intervalo de Reintento (horas)',
        default=3,
        help='Cada cuántas horas el Robot Nocturno intentará reenviar las facturas fallidas.'
    )
```

### 3. `data/ir_cron_data.xml`
Crear la Acción Programada del Robot Nocturno:
```xml
<!-- Cron Job que re-envía a la DIAN las facturas con falla TÉCNICA (TimeoutException, 
     saturación de red). NO reintenta rechazos por errores de datos (NIT malo, etc.) -->
<record id="cron_retry_dian_invoices" model="ir.cron">
    <field name="name">Reintento Automático Facturas DIAN (Falla Técnica)</field>
    <field name="model_id" ref="account.model_account_move"/>
    <field name="state">code</field>
    <field name="code">model.cron_retry_dian_failed_invoices()</field>
    <field name="interval_number">3</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```
El método `cron_retry_dian_failed_invoices()` busca `account.move` con un campo nuevo `dian_edi_state = 'technical_retry'` y los reintenta.

### 4. `views/account_journal_views.xml`
Inyectar el panel de "Modo Contingencia DIAN" en la vista formulario del Diario Contable con colores de advertencia (usar `widget="boolean_toggle"` y un `groups_string` para solo mostrarlo en diarios con l10n colombiana EDI activa).

### 5. `tests/test_dian_rejection.py`
Prueba unitaria **crítica e imprescindible**:
```python
def test_dian_rejection_does_not_consume_sequence(self):
    """
    CRÍTICO: Cuando la DIAN rechaza, el ir.sequence del diario NO debe avanzar.
    Simular (Mock) la llamada HTTP a la DIAN como que devuelve error HTTP 500.
    Verificar que:
    (1) Se levanta un UserError apropiado.
    (2) La secuencia 'next_by_id' del diario no fue llamada.
    (3) La factura sigue en estado 'draft'.
    """
```

---

## REGLAS ABSOLUTAS DE DESARROLLO (NO NEGOCIABLES)

1. **NUNCA quemes el ir.sequence antes de recibir OK de la DIAN.** La secuencia solo se toma dentro del fragmento de código posterior al éxito.
2. **SIEMPRE usa `timeout=8` en todas las peticiones requests a los webservices DIAN.**
3. **Implementa manejo diferenciado** entre errores TÉCNICOS (retry automático) y errores de DATOS del usuario (aviso en el Chatter de la factura + sin retry automático).
4. **NUNCA modifiques el código de `l10n_co_dian`** (módulo nativo de Odoo). Siempre usa `_inherit`.
5. **El módulo debe instalar sin errores con el comando:** `odoo-bin --addons-path=/home/david/odoo-projects/l10n_co_dian_advanced -i l10n_co_dian_advanced -d <db>`

---

## CONVENCIONES DE CÓDIGO

- Python: PEP8. Docstrings en inglés técnico.
- XML: Usar IDs con prefijo `l10n_co_dian_advanced_`.
- Versión del módulo: `18.0.1.0.0`
- Licencia: `OPL-1`

---

## DOCUMENTACIÓN REQUERIDA (Para escalabilidad a Odoo 19)

Al finalizar cada archivo de código, debes agregar un comentario de cabecera como este:

```python
# ============================================================
# Módulo  : l10n_co_dian_advanced
# Archivo  : models/account_move.py
# Versión  : 18.0.1.0.0
# Propósito: Override de _post() para desacoplar la secuencia DIAN.
# Notas    : Al migrar a Odoo 19, verificar si el flujo de action_post/
#             _post() en account.move cambió de firma. Si la DIAN actualizó
#             su API UBL, el motor de l10n_co_dian lo maneja; este override
#             solo necesita ajustar el punto de llamada al super().
# ============================================================
```

---

## GIT Y ENTREGA

El repositorio vive en:
`/home/david/odoo-projects/l10n_co_dian_advanced/`

Al finalizar cada archivo, haz commit con mensajes descriptivos:
- `feat: add sequence decoupling logic to account_move._post()`
- `feat: add contingency mode field to account_journal`
- `feat: add DIAN retry cron job`
- `test: add critical test for sequence integrity on DIAN rejection`

La rama de trabajo es `18.0` (o `feature/fase-1-mvp` si prefieres feature branching).

---

## DEFINICIÓN DE TERMINADO (Definition of Done)

El trabajo de la Fase 1 está completo cuando:
- [ ] `test_dian_rejection_does_not_consume_sequence` pasa en verde.
- [ ] En un entorno de Staging de Odoo.sh, se puede confirmar una factura y el número `FE-XXX` aparece en el documento **solo si** la DIAN lo aceptó.
- [ ] Si se simula una caída de la DIAN (apagando la red en el servidor de prueba durante 9 segundos), la factura NO queda congelada; vuelve a estado Borrador con un mensaje de error claro en 9 segundos.
- [ ] El Cron nocturno está activo y re-procesa correctamente las facturas marcadas como `technical_retry`.
