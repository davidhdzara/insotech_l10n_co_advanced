# -*- coding: utf-8 -*-
"""RADIAN Event tracking model.

Tracks DIAN RADIAN events (030-035) per invoice. This is a standalone
model (does NOT add fields to account.move) to comply with the rule
of not modifying native Odoo models.

Legal basis:
- Resolución 000165 de 2023 (mandatory events)
- Resolución 000008 de 2024 (Anexo 1.9)
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RadianEvent(models.Model):
    """Track RADIAN events for Colombian electronic invoices."""

    _name = 'insotech.radian.event'
    _description = 'Evento RADIAN'
    _order = 'event_date desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Referencia",
        compute='_compute_name',
        store=True,
        help="Referencia auto-generada del evento.",
    )
    move_id = fields.Many2one(
        'account.move',
        string="Factura",
        required=True,
        ondelete='cascade',
        index=True,
        help="Factura electrónica asociada al evento.",
    )
    company_id = fields.Many2one(
        'res.company',
        string="Empresa",
        required=True,
        default=lambda self: self.env.company,
    )
    event_code = fields.Selection(
        selection=[
            ('030', '030 — Acuse de Recibo'),
            ('031', '031 — Rechazo de la FE'),
            ('032', '032 — Recibo de Bienes y Servicios'),
            ('033', '033 — Aceptación Expresa'),
            ('034', '034 — Reclamo de la FE'),
            ('035', '035 — Aceptación Tácita'),
        ],
        string="Código Evento",
        required=True,
        tracking=True,
        help="Código del evento RADIAN según catálogo DIAN.",
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Generado'),
            ('sent', 'Enviado a DIAN'),
            ('accepted', 'Aceptado por DIAN'),
            ('error', 'Error'),
        ],
        string="Estado",
        default='draft',
        required=True,
        tracking=True,
        help="Estado del evento RADIAN.",
    )
    event_date = fields.Datetime(
        string="Fecha del Evento",
        default=fields.Datetime.now,
        required=True,
        help="Fecha y hora en que se generó el evento.",
    )
    xml_content = fields.Text(
        string="XML Generado (Dry Run)",
        help="Contenido del ApplicationResponse XML generado. "
             "En modo dry run, no se envía a la DIAN.",
    )
    notes = fields.Text(
        string="Notas",
        help="Notas adicionales o motivo del evento "
             "(ej: código de reclamo para evento 031).",
    )
    source = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('cron', 'Automático (CRON)'),
            ('portal', 'Portal Receptor'),
        ],
        string="Origen",
        default='manual',
        required=True,
        help="Cómo se generó este evento.",
    )
    claim_code = fields.Selection(
        selection=[
            ('01', '01 — Documento con inconsistencias'),
            ('02', '02 — Mercancía no entregada totalmente'),
            ('03', '03 — Mercancía no entregada parcialmente'),
            ('04', '04 — Servicio no prestado'),
        ],
        string="Concepto de Reclamo",
        help="Motivo del reclamo (solo para evento 034 — Reclamo).",
    )

    @api.depends('event_code', 'move_id')
    def _compute_name(self):
        """Generate a readable reference for the event."""
        for event in self:
            move_name = event.move_id.name or '???'
            code = event.event_code or '???'
            event.name = f"RAD-{code}/{move_name}"

    def _get_custom_holidays(self, company):
        """Get manual holidays for the given company as a set of dates.

        :param company: res.company record
        :returns: set of date objects
        """
        custom = self.env['insotech.custom.holiday'].search([
            ('company_id', '=', company.id),
        ])
        return {rec.date for rec in custom}

    @api.model
    def _cron_tacit_acceptance(self):
        """CRON: Generate tacit acceptance (035) events.

        Logic:
        1. Find all event 032 (Recibo del Bien/Servicio) records
        2. Check if 3 business days have passed since the 032
        3. Verify no event 033 (Aceptación Expresa),
           031 (Rechazo), or 034 (Reclamo) exists
        4. Create event 035 (Aceptación Tácita) in dry run

        IMPORTANT: The 3-day clock starts at event 032
        (Recibo del bien), NOT at 030 (Acuse de recibo).

        Legal basis: Resolución 000165/2023, art. 25
        Business days: Art. 62, Ley 4/1913
        """
        from ..services.colombian_calendar import add_business_days

        # Find all 032 events (Recibo del bien) — this is when
        # the 3-day clock starts per DIAN timeline
        recibo_events = self.search([
            ('event_code', '=', '032'),
            ('state', 'in', ('done', 'sent', 'accepted')),
        ])

        if not recibo_events:
            _logger.info(
                "Insotech RADIAN: No recibo events (032) found "
                "for tacit acceptance check."
            )
            return

        today = fields.Date.context_today(self)
        created_count = 0

        for recibo in recibo_events:
            move = recibo.move_id
            company = recibo.company_id

            # Check if this invoice already has a resolution event:
            # 033 (Aceptación Expresa), 035 (Aceptación Tácita),
            # 031 (Rechazo), or 034 (Reclamo)
            existing = self.search_count([
                ('move_id', '=', move.id),
                ('event_code', 'in', ('033', '035', '031', '034')),
                ('state', '!=', 'error'),
            ])
            if existing:
                continue

            # Calculate the deadline: 032 date + 3 business days
            recibo_date = recibo.event_date.date()
            custom_holidays = self._get_custom_holidays(company)
            deadline = add_business_days(
                recibo_date, 3, custom_holidays,
            )

            if today <= deadline:
                # Not yet expired
                continue

            # 3 business days have passed — generate 035
            _logger.info(
                "Insotech RADIAN: Generating tacit acceptance "
                "(035) for invoice %s (recibo date: %s, "
                "deadline: %s, today: %s)",
                move.name, recibo_date, deadline, today,
            )

            self.create({
                'move_id': move.id,
                'company_id': company.id,
                'event_code': '035',
                'state': 'done',
                'source': 'cron',
                'notes': (
                    f"Aceptación tácita generada automáticamente. "
                    f"Recibo del bien (032) del {recibo_date}. "
                    f"Plazo venció el {deadline}. "
                    f"Modo: dry run (XML no enviado a DIAN)."
                ),
            })

            # Post notification on the invoice chatter
            try:
                move.message_post(
                    body=(
                        f"⏱️ <b>Aceptación Tácita (035)</b> generada "
                        f"automáticamente.<br/>"
                        f"Recibo del bien (032): {recibo_date}<br/>"
                        f"Plazo de 3 días hábiles venció: {deadline}<br/>"
                        f"Sin respuesta del receptor → aceptación tácita."
                    ),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )
            except Exception as e:
                _logger.debug(
                    "Insotech: Could not post tacit acceptance "
                    "notification for move %s: %s",
                    move.id, e,
                )

            created_count += 1

        _logger.info(
            "Insotech RADIAN: Tacit acceptance CRON complete. "
            "Created %d event(s) 035.", created_count,
        )
