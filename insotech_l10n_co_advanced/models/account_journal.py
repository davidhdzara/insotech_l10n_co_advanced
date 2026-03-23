import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def button_l10n_co_dian_fetch_numbering_range(self):
        """Override: try native call, on error 302 give helpful message."""
        try:
            return super().button_l10n_co_dian_fetch_numbering_range()
        except UserError as e:
            error_msg = str(e)
            if '302' in error_msg or 'prefijos' in error_msg.lower():
                raise UserError(
                    "⚠️ La DIAN devolvió error 302: El software no tiene "
                    "prefijos asociados según la API.\n\n"
                    "Esto puede ocurrir si:\n"
                    "• La asociación en el portal DIAN tiene menos de 24 horas\n"
                    "• Hay inconsistencia temporal entre el portal y la API\n\n"
                    "SOLUCIÓN: Use el botón 'Configurar Resolución Manualmente' "
                    "que aparece debajo para ingresar los datos directamente.\n\n"
                    "Datos que necesita del portal DIAN:\n"
                    "• Número de resolución\n"
                    "• Fechas de inicio y fin\n"
                    "• Rango de numeración (inicio y fin)\n"
                    "• Clave de control técnico (si disponible)"
                )
            raise

    def button_l10n_co_dian_open_manual_config(self):
        """Open wizard for manual DIAN resolution configuration."""
        self.ensure_one()
        return {
            'name': 'Configurar Resolución DIAN Manualmente',
            'type': 'ir.actions.act_window',
            'res_model': 'l10n_co_dian.manual.config.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_journal_id': self.id,
                'default_authorization_number':
                    self.l10n_co_edi_dian_authorization_number or '',
                'default_authorization_date':
                    self.l10n_co_edi_dian_authorization_date,
                'default_authorization_end_date':
                    self.l10n_co_edi_dian_authorization_end_date,
                'default_min_range_number':
                    self.l10n_co_edi_min_range_number or 0,
                'default_max_range_number':
                    self.l10n_co_edi_max_range_number or 0,
                'default_technical_key':
                    self.l10n_co_dian_technical_key or '',
            },
        }
