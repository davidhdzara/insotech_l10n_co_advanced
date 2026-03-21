import logging
import requests
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    insotech_license_token = fields.Char(string="Token de Licencia Insotech")

    def _validate_insotech_license(self):
        self.ensure_one()

        token = self.insotech_license_token
        vat = self.vat
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if not token:
            return False

        payload = {
            'token': token,
            'vat': vat,
            'url': url
        }

        try:
            response = requests.post(
                'https://www.insotech.it/insotech/api/v1/verify',
                json=payload,
                timeout=3
            )
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'active':
                        return True
                except ValueError:
                    _logger.warning("Respuesta no válida de la API de Insotech (JSON inválido).")
        except requests.exceptions.Timeout:
            _logger.warning("Timeout al validar la licencia de Insotech.")
        except requests.exceptions.RequestException as e:
            _logger.warning("Error de red al validar la licencia de Insotech: %s", e)
        except Exception as e:
            _logger.warning("Error inesperado al validar la licencia de Insotech: %s", e)

        return False

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    insotech_license_token = fields.Char(
        related='company_id.insotech_license_token',
        readonly=False,
        string="Token de Licencia Insotech"
    )
