import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    """Extensión de res.company con campos de habilitación DIAN."""

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
        selection=[
            ('not_configured', 'Sin Configurar'),
            ('in_progress', 'En Proceso'),
            ('enabled', 'Habilitado'),
        ],
        string="Estado Configuración DIAN",
        default='not_configured',
    )
    insotech_dian_cert_file = fields.Binary(
        string="Certificado .p12 (DIAN)",
        attachment=True,
    )
    insotech_dian_cert_filename = fields.Char(
        string="Nombre archivo certificado",
    )
    insotech_dian_cert_password = fields.Char(
        string="Contraseña certificado (DIAN)",
    )

    def _register_hook(self):
        """Ensure product.product_category_goods XML ID exists.

        Runs on every server start. Prevents ValueError in
        l10n_co_dian's certification process on databases
        without demo data.
        """
        super()._register_hook()
        try:
            self.env['ir.model.data']._xmlid_to_res_model_res_id(
                'product.product_category_goods',
                raise_if_not_found=True,
            )
        except ValueError:
            Category = self.env['product.category']
            category = Category.search(
                [('parent_id', '=', False)],
                limit=1, order='id ASC',
            )
            if not category:
                category = Category.search(
                    [], limit=1, order='id ASC',
                )
            if category:
                self.env['ir.model.data'].create({
                    'module': 'product',
                    'name': 'product_category_goods',
                    'model': 'product.category',
                    'res_id': category.id,
                    'noupdate': True,
                })
                _logger.info(
                    "Insotech: Created product.product_category_goods "
                    "→ '%s' (id=%s)", category.name, category.id,
                )
            else:
                _logger.warning(
                    "Insotech: No product categories found. "
                    "Cannot create product.product_category_goods.",
                )
