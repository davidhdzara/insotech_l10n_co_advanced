# -*- coding: utf-8 -*-
from odoo import api, models, _
import logging

_logger = logging.getLogger(__name__)

def _compute_dv_local(nit_str):
    """Calcula dígito de verificación DIAN (Módulo 11) para un NIT."""
    if not nit_str or not str(nit_str).isdigit():
        return '0'
    factors = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    nit_str = str(nit_str).zfill(15)
    total = sum(int(digit) * factors[i] for i, digit in enumerate(reversed(nit_str)))
    remainder = total % 11
    return str(11 - remainder) if remainder >= 2 else str(remainder)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('l10n_co_document_type', 'vat')
    def _l10n_co_dian_onchange_identification_type(self):
        """Sobrescribe el onchange nativo peligroso de Odoo 19.
        
        El core de Odoo intenta consumir el servicio SOAP de la DIAN para 
        consultar el RUT en cada pulsación del teclado o cambio de documento.
        Esto causa severos bloqueos de UI (RPC_ERROR) y arroja TypeError si 
        la llave PEM no está encriptada con contraseña en el módulo certificate.
        
        InSoTech desactiva esta arriesgada consulta en vivo y pre-calcula
        el Dígito de Verificación matemáticamente en modo Offline.
        """
        for partner in self:
            # Prevent calling super() because that's where the DIAN request happens.
            
            # If it's a NIT (usually 31), let's pre-calculate the DV locally.
            if partner.l10n_co_document_type == '31' and partner.vat:
                try:
                    # In Odoo 19 l10n_co, the verification code field varies, 
                    # but typically it's l10n_co_verification_code
                    if hasattr(partner, 'l10n_co_verification_code'):
                        partner.l10n_co_verification_code = _compute_dv_local(partner.vat)
                except Exception as e:
                    _logger.debug("Insotech Partner Onchange: Error calculando DV autómata: %s", e)
