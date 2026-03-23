import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DianManualConfigWizard(models.TransientModel):
    _name = 'l10n_co_dian.manual.config.wizard'
    _description = 'Configuración Manual de Resolución DIAN'

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        required=True,
        readonly=True,
    )
    authorization_number = fields.Char(
        string='Resolución de Facturación',
        help='Número de resolución asignado por la DIAN (ej: 18764107498052)',
    )
    authorization_date = fields.Date(
        string='Fecha de Resolución',
        help='Fecha de inicio de la resolución',
    )
    authorization_end_date = fields.Date(
        string='Fecha de Finalización',
        help='Fecha de vencimiento de la resolución',
    )
    min_range_number = fields.Integer(
        string='Número Inicial',
        help='Primer número autorizado de la resolución',
    )
    max_range_number = fields.Integer(
        string='Número Final',
        help='Último número autorizado de la resolución',
    )
    technical_key = fields.Char(
        string='Clave de Control Técnico',
        help='Clave técnica proporcionada por la DIAN para el CUFE. '
             'Si no la tiene, puede dejarla vacía e intentar '
             '"Recargar configuración DIAN" más adelante.',
    )

    def action_save_config(self):
        """Write resolution data directly to the journal."""
        self.ensure_one()
        vals = {}
        if self.authorization_number:
            vals['l10n_co_edi_dian_authorization_number'] = (
                self.authorization_number
            )
        if self.authorization_date:
            vals['l10n_co_edi_dian_authorization_date'] = (
                self.authorization_date
            )
        if self.authorization_end_date:
            vals['l10n_co_edi_dian_authorization_end_date'] = (
                self.authorization_end_date
            )
        if self.min_range_number:
            vals['l10n_co_edi_min_range_number'] = self.min_range_number
        if self.max_range_number:
            vals['l10n_co_edi_max_range_number'] = self.max_range_number
        if self.technical_key:
            vals['l10n_co_dian_technical_key'] = self.technical_key

        if vals:
            self.journal_id.sudo().write(vals)
            _logger.info(
                'DIAN resolution configured manually for journal %s: %s',
                self.journal_id.name,
                vals,
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Resolución DIAN configurada',
                'message': (
                    'Los datos de la resolución se guardaron correctamente '
                    'en el diario %s.' % self.journal_id.name
                ),
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
