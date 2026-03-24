# -*- coding: utf-8 -*-
"""Override res.partner to auto-compute DV for Colombian NITs.

Uses @api.onchange (UI-only) to auto-fill the verification digit
when the user types a NIT.  Checks that the field exists before
setting it, since l10n_co_verification_code may not be installed.

⚠️ V18 MIGRATION NOTE:
   Verify field name and model in Odoo 18's l10n_co module.
"""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# DIAN modulo-11 prime factors for DV calculation
_DV_FACTORS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def _compute_verification_digit(nit_str):
    """Calculate DIAN verification digit for a Colombian NIT."""
    if not nit_str or not nit_str.strip().isdigit():
        return ''
    nit_str = str(nit_str).strip().zfill(15)
    total = 0
    for i, digit in enumerate(reversed(nit_str)):
        if i >= len(_DV_FACTORS):
            break
        total += int(digit) * _DV_FACTORS[i]
    remainder = total % 11
    return str(11 - remainder) if remainder >= 2 else str(remainder)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat', 'l10n_latam_identification_type_id')
    def _onchange_vat_compute_dv(self):
        """Auto-fill DV when user types a NIT in the contact form."""
        # Check which DV field exists on this model
        dv_field = None
        for fname in ('l10n_co_verification_code', 'vat_dv'):
            if fname in self._fields:
                dv_field = fname
                break

        if not dv_field:
            # No DV field available — nothing to do
            return

        for partner in self:
            try:
                id_type = partner.l10n_latam_identification_type_id
                is_nit = bool(
                    id_type
                    and getattr(id_type, 'l10n_co_document_code', None)
                    == '31'
                )
            except Exception:
                is_nit = False

            if is_nit and partner.vat:
                clean_vat = ''.join(
                    c for c in (partner.vat or '') if c.isdigit()
                )
                dv = _compute_verification_digit(clean_vat)
                if dv:
                    partner[dv_field] = dv
            elif not is_nit:
                partner[dv_field] = ''
