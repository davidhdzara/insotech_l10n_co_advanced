import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def button_l10n_co_dian_fetch_numbering_range(self):
        """Override: sanitize NIT and improve DIAN error messages.

        Fixes two known issues with GetNumberingRange:

        1) Error 401 — Odoo sends company.vat which may contain
           NIT+DV concatenated (e.g. '9017972495'). The DIAN SOAP
           service expects only the NIT without DV ('901797249').
           We temporarily strip the DV before calling super().

        2) Error 302 — The DIAN API may not have synced the
           prefix associations yet if they were recently set up
           in the web portal. We catch this and show a helpful
           message with actionable steps.
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        original_vat = company.vat or ''
        dv = company.l10n_co_verification_code or ''
        sanitized = False

        # --- Fix 401: strip DV from vat if concatenated ---
        if original_vat and dv:
            # NIT 901797249 + DV 5 → vat = '9017972495'
            # We need to send only '901797249'
            if original_vat.endswith(str(dv)):
                clean_nit = original_vat[:-len(str(dv))]
                if clean_nit:
                    _logger.info(
                        "Insotech: Sanitizing company vat for "
                        "GetNumberingRange: '%s' → '%s' "
                        "(removed DV '%s')",
                        original_vat, clean_nit, dv,
                    )
                    company.sudo().write({'vat': clean_nit})
                    sanitized = True

        try:
            result = super().button_l10n_co_dian_fetch_numbering_range()
        except UserError as e:
            error_msg = str(e)
            # --- Fix 302: helpful error for missing prefixes ---
            if '302' in error_msg or 'prefijos' in error_msg.lower():
                raise UserError(
                    "⚠️ La DIAN devolvió error 302: no se "
                    "encontraron prefijos asociados al "
                    "software.\n\n"
                    "Esto puede ocurrir por:\n"
                    "1. La asociación en el portal DIAN "
                    "tiene menos de 24 horas (la API tarda "
                    "en sincronizar)\n"
                    "2. No se ha presionado 'Sincronizar a "
                    "Producción' en el portal DIAN\n"
                    "3. El modo de operación en Odoo no es "
                    "'Producción'\n\n"
                    "SOLUCIÓN INMEDIATA:\n"
                    "Puede llenar los campos del diario "
                    "manualmente (ya existen en la pestaña "
                    "'Configuración DIAN'):\n"
                    "• Resolución de facturación\n"
                    "• Fechas de resolución\n"
                    "• Rango de numeración\n"
                    "• Clave de control técnico\n\n"
                    "Estos datos los encuentra en el portal "
                    "DIAN (catalogo-vpfe.dian.gov.co) en la "
                    "sección 'Facturando Electrónicamente'."
                ) from e
            # --- Fix 401: helpful error for NIT issues ---
            if '401' in error_msg or 'no autorizado' in error_msg.lower():
                raise UserError(
                    "⚠️ La DIAN devolvió error 401: NIT no "
                    "autorizado.\n\n"
                    "Verifique que el campo NIT de la "
                    "empresa (Ajustes → Empresas) contenga "
                    "SOLO el NIT sin dígito de "
                    "verificación.\n\n"
                    "Ejemplo:\n"
                    "  ✅ Correcto: 901797249\n"
                    "  ❌ Incorrecto: 9017972495\n\n"
                    "El dígito de verificación (DV) debe "
                    "estar en el campo separado "
                    "'Código de Verificación'.\n\n"
                    "Error original: %s" % error_msg
                ) from e
            raise
        finally:
            # Always restore the original vat value
            if sanitized:
                _logger.info(
                    "Insotech: Restoring company vat "
                    "to original value: '%s'",
                    original_vat,
                )
                company.sudo().write({'vat': original_vat})

        return result
