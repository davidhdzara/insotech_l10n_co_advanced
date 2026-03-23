import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # -----------------------------------------------------------------
    # RESOLUTION COUNTER (computed — dynamic for any journal)
    # -----------------------------------------------------------------

    insotech_resolution_used = fields.Integer(
        string='Consecutivos usados',
        compute='_compute_insotech_resolution_counter',
    )
    insotech_resolution_total = fields.Integer(
        string='Total autorizados',
        compute='_compute_insotech_resolution_counter',
    )
    insotech_resolution_available = fields.Integer(
        string='Disponibles',
        compute='_compute_insotech_resolution_counter',
    )
    insotech_resolution_percent = fields.Float(
        string='% Disponible',
        compute='_compute_insotech_resolution_counter',
    )
    insotech_resolution_display = fields.Char(
        string='Uso de resolución',
        compute='_compute_insotech_resolution_counter',
    )

    @api.depends('l10n_co_edi_min_range_number',
                 'l10n_co_edi_max_range_number')
    def _compute_insotech_resolution_counter(self):
        """Count DIAN resolution usage per journal.

        Counts posted invoices (excluding PRE-INV) in this
        journal and compares against the authorized range.
        Works with ANY journal name — reads range fields
        dynamically from l10n_co_edi fields.
        """
        for journal in self:
            journal.insotech_resolution_used = 0
            journal.insotech_resolution_total = 0
            journal.insotech_resolution_available = 0
            journal.insotech_resolution_percent = 0.0
            journal.insotech_resolution_display = ''

            if not journal._insotech_is_dian_enabled():
                continue

            min_r = getattr(
                journal, 'l10n_co_edi_min_range_number', 0
            ) or 0
            max_r = getattr(
                journal, 'l10n_co_edi_max_range_number', 0
            ) or 0
            if not max_r:
                continue

            total = max_r - min_r + 1

            used = self.env['account.move'].search_count([
                ('journal_id', '=', journal.id),
                ('state', '=', 'posted'),
                ('move_type', 'in', (
                    'out_invoice', 'out_refund',
                )),
                ('name', 'not like', 'PRE-INV%'),
            ])

            available = max(0, total - used)
            pct = (available / total * 100) if total > 0 else 0

            journal.insotech_resolution_used = used
            journal.insotech_resolution_total = total
            journal.insotech_resolution_available = available
            journal.insotech_resolution_percent = round(pct, 1)
            journal.insotech_resolution_display = (
                '%d / %d usados (%.1f%% disponible)'
                % (used, total, pct)
            )

    # -----------------------------------------------------------------
    # DIAN SEQUENCE FORMAT VALIDATION
    # -----------------------------------------------------------------

    def _insotech_get_dian_prefix(self):
        """Return the DIAN prefix for this journal.

        The prefix is read from the journal's ``code`` field
        (displayed as 'Prefijo de secuencia' in the UI).  This
        value is dynamic \u2014 each client can set any prefix
        (``FE``, ``FEI``, ``FEGU``, etc.).

        :returns: string prefix or empty string
        """
        self.ensure_one()
        return (self.code or '').strip()

    def _insotech_check_dian_sequence_format(self):
        """Warn if the journal produces DIAN-incompatible names.

        DIAN expects invoice numbers in the format:
        ``{Prefix}{Number}``  (e.g. ``FE1``, ``FEGU500``).

        Odoo 19 SequenceMixin default format is:
        ``{code}/%(year)s/{padded_number}`` \u2192 ``FE/2026/00001``

        This method checks the most recent posted move in the
        journal and warns if the name contains ``/`` or other
        characters that DIAN will reject (rule FAD05a).

        It does NOT block \u2014 it only logs and returns a message.
        """
        self.ensure_one()
        if not self._insotech_is_dian_enabled():
            return ''

        # Check last posted move in this journal
        last_move = self.env['account.move'].search([
            ('journal_id', '=', self.id),
            ('state', '=', 'posted'),
            ('move_type', 'in', (
                'out_invoice', 'out_refund',
            )),
            ('name', 'not like', 'PRE-INV%'),
        ], limit=1, order='id desc')

        if last_move and '/' in last_move.name:
            prefix = self._insotech_get_dian_prefix()
            msg = (
                "El diario '%s' genera nombres con formato "
                "'%s' que contiene '/'. La DIAN rechazará "
                "esto con error FAD05a.\n\n"
                "Formato esperado: %s1, %s2, ... %s%d\n\n"
                "Para corregir: edite la referencia de la "
                "última factura confirmada en este diario "
                "para que siga el formato '%s1' (sin barras "
                "ni año)."
            ) % (
                self.name,
                last_move.name,
                prefix, prefix, prefix,
                self.l10n_co_edi_max_range_number or 5000,
                prefix,
            )
            _logger.warning("Insotech: %s", msg)
            return msg
        return ''

    def _insotech_is_dian_enabled(self):
        """Check if this journal has DIAN configuration active."""
        if hasattr(self, 'l10n_co_dian_provider'):
            if self.l10n_co_dian_provider:
                return True
        if hasattr(self, 'l10n_co_edi_dian_authorization_number'):
            if self.l10n_co_edi_dian_authorization_number:
                return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to warn about DIAN sequence format."""
        journals = super().create(vals_list)
        for journal in journals:
            msg = journal._insotech_check_dian_sequence_format()
            if msg:
                _logger.warning(
                    "Insotech: New DIAN journal '%s' may have "
                    "incompatible sequence format.",
                    journal.name,
                )
        return journals

    def write(self, vals):
        """Override write to warn about DIAN sequence format."""
        result = super().write(vals)
        # Check if DIAN-related fields were modified
        dian_fields = {
            'l10n_co_dian_provider',
            'l10n_co_edi_dian_authorization_number',
            'code',
        }
        if dian_fields & set(vals.keys()):
            for journal in self:
                journal._insotech_check_dian_sequence_format()
        return result

    # -----------------------------------------------------------------
    # DIAN NUMBERING RANGE FETCH (existing)
    # -----------------------------------------------------------------

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
