# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    """Extend res.company with DIAN configuration state tracking.

    Tracks whether the company has completed the DIAN electronic
    invoicing setup process through the express wizard.
    """

    _inherit = 'res.company'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    insotech_dian_config_state = fields.Selection(
        selection=[
            ('not_configured', 'Sin Configurar'),
            ('in_progress', 'En Proceso de Certificación'),
            ('enabled', 'Habilitado'),
        ],
        default='not_configured',
        string="Estado Configuración DIAN",
        help="Estado del proceso de configuración de facturación "
             "electrónica DIAN gestionado por el wizard express.",
    )

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_insotech_unlock_dian_config(self):
        """Reset DIAN configuration state to allow reconfiguration.

        This action is protected by a confirmation dialog and restricted
        to accounting managers via the view's groups attribute.
        """
        self.ensure_one()
        if not self.env.user.has_group(
            'account.group_account_manager'
        ):
            raise UserError(_(
                "Solo los administradores contables pueden "
                "desbloquear la configuración DIAN."
            ))
        self.insotech_dian_config_state = 'not_configured'
