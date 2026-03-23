from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expone campos de habilitación DIAN en Ajustes."""

    _inherit = 'res.config.settings'

    insotech_dian_software_id = fields.Char(
        related='company_id.insotech_dian_software_id',
        readonly=False,
        string="Software ID (DIAN)",
    )
    insotech_dian_software_pin = fields.Char(
        related='company_id.insotech_dian_software_pin',
        readonly=False,
        string="Software PIN (DIAN)",
    )
    insotech_dian_test_set_id = fields.Char(
        related='company_id.insotech_dian_test_set_id',
        readonly=False,
        string="Test Set ID (DIAN)",
    )
    insotech_dian_config_state = fields.Selection(
        related='company_id.insotech_dian_config_state',
        readonly=True,
        string="Estado Configuración DIAN",
    )
