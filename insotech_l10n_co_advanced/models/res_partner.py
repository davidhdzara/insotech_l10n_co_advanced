# -*- coding: utf-8 -*-
"""Override res.partner to auto-compute DV for Colombian NITs.

Uses @api.onchange (UI-only) instead of a computed field to avoid
crashing existing databases during module upgrade. The field
l10n_co_verification_code stays as a regular Char — no schema change.

⚠️ V18 MIGRATION NOTE:
   Verify l10n_co_verification_code and l10n_latam_identification_type_id
   still exist in Odoo 18's l10n_co module.
"""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# DIAN modulo-11 prime factors for DV calculation
_DV_FACTORS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def _compute_verification_digit(nit_str):
    """Calculate DIAN verification digit for a Colombian NIT.

    Algorithm:
        1. Pad NIT to 15 digits with leading zeros
        2. Multiply each digit (right to left) by prime factors
        3. Sum products, take modulo 11
        4. If remainder >= 2 → DV = 11 - remainder, else DV = remainder
    """
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
        """Auto-fill DV when user types a NIT in the contact form.

        Only triggers in the UI (not during batch operations or imports).
        Does not modify the field definition — safe for upgrades.
        """
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
                    partner.l10n_co_verification_code = dv
            elif is_nit and not partner.vat:
                pass  # Keep existing DV
            else:
                # Not NIT → clear DV
                partner.l10n_co_verification_code = ''
