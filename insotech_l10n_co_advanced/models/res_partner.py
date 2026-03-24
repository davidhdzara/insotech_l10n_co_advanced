# -*- coding: utf-8 -*-
"""Override res.partner to auto-compute DV for Colombian NITs.

The verification digit (Dígito de Verificación) is calculated using
the DIAN's modulo-11 algorithm whenever the partner's identification
type is NIT (document type code '31').

⚠️ V18 MIGRATION NOTE:
   This file overrides l10n_co_verification_code as a stored computed
   field.  When porting to V18, verify that:
   - l10n_co_verification_code still exists in Odoo's l10n_co module
   - l10n_latam_identification_type_id API hasn't changed
   - The field is still Char (not Integer)
"""
import logging

from odoo import api, fields, models

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

    Args:
        nit_str: NIT as string (digits only, no DV, no dashes)

    Returns:
        str: single digit '0'-'9' or empty string if invalid
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

    l10n_co_verification_code = fields.Char(
        compute='_compute_l10n_co_verification_code',
        store=True,
        readonly=False,
        string="Verification Code (DV)",
    )

    @api.depends('vat', 'l10n_latam_identification_type_id')
    def _compute_l10n_co_verification_code(self):
        """Auto-compute DV only when identification type is NIT.

        Note: This runs on ALL partners during module upgrade.
        Must handle gracefully: no id_type, no vat, missing fields.
        """
        for partner in self:
            try:
                id_type = partner.l10n_latam_identification_type_id
                is_nit = bool(
                    id_type
                    and getattr(id_type, 'l10n_co_document_code', '')
                    == '31'
                )
            except Exception:
                # Field might not exist yet during install
                is_nit = False

            if is_nit and partner.vat:
                clean_vat = ''.join(
                    c for c in (partner.vat or '') if c.isdigit()
                )
                dv = _compute_verification_digit(clean_vat)
                partner.l10n_co_verification_code = dv or ''
            elif is_nit and not partner.vat:
                # NIT type selected but no VAT yet — keep existing
                partner.l10n_co_verification_code = (
                    partner.l10n_co_verification_code or ''
                )
            else:
                # Not NIT or no id_type — don't overwrite manually
                # entered values for non-Colombian partners
                if not partner.l10n_co_verification_code:
                    partner.l10n_co_verification_code = ''
