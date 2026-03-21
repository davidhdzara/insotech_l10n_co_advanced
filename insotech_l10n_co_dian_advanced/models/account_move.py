# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_co_dian_sequence_pending = fields.Boolean(
        string='Secuencia DIAN Pendiente',
        copy=False,
        default=False,
        help="Indica si esta factura está esperando que se le asigne la secuencia oficial de la DIAN justo antes de enviarse."
    )

    def _post(self, soft=True):
        # Override to prevent consuming the DIAN sequence prematurely.
        # We can mark the invoice as pending DIAN sequence if it's a Colombian invoice.
        res = super(AccountMove, self)._post(soft=soft)
        for move in self:
            if move.country_code == 'CO' and move.move_type in ('out_invoice', 'out_refund'):
                # Here we could set logic so it gets a temporary internal sequence
                # For now we will tag it.
                move.l10n_co_dian_sequence_pending = True
        return res

    def action_l10n_co_dian_assign_sequence(self):
        """
        Método que se llamará antes de generar el XML para asignarle el consecutivo real.
        De esta forma, si se postea la factura, solo gasta secuencia interna.
        """
        for move in self:
            if move.l10n_co_dian_sequence_pending and move.state == 'posted':
                # Logic to assign the real FE-XXXX sequence
                move.l10n_co_dian_sequence_pending = False
                # Trigger sequence generation based on journal's DIAN resolution
                # move.name = next_sequence...
