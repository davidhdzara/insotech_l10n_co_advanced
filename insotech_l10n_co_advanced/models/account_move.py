import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Extend account.move to protect DIAN resolution consecutives.

    This module implements the PRE-INV → FE- sequence mutation pattern:
    1. On posting, Colombian EDI invoices get a temporary PRE-INV name.
    2. The DIAN resolution consecutive is NOT consumed.
    3. When DIAN accepts, the name mutates to the legal sequence (e.g. FE-845).
    4. When DIAN rejects, the PRE-INV name stays and the user can correct & retry.
    """

    _inherit = 'account.move'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    insotech_dian_status = fields.Selection(
        selection=[
            ('not_applicable', 'No Aplica'),
            ('pending', 'Pendiente DIAN'),
            ('accepted', 'Aceptada por DIAN'),
            ('rejected', 'Rechazada por DIAN'),
        ],
        string="Estado DIAN (Insotech)",
        default='not_applicable',
        copy=False,
        tracking=True,
        help="Estado de validación de la factura ante la DIAN. "
             "Gestionado por el módulo Insotech."
    )

    insotech_pre_inv_name = fields.Char(
        string="Nombre Temporal PRE-INV",
        copy=False,
        readonly=True,
        help="Nombre temporal asignado mientras la factura está pendiente "
             "de validación por la DIAN."
    )

    insotech_reserved_dian_name = fields.Char(
        string="Nombre DIAN Reservado",
        copy=False,
        readonly=True,
        help="Nombre legal de la resolución DIAN asignado por Odoo al "
             "confirmar. Se restaura cuando la DIAN acepta la factura."
    )

    insotech_is_co_edi = fields.Boolean(
        string="Es Factura EDI Colombiana",
        compute='_compute_insotech_is_co_edi',
        store=True,
        help="Indica si esta factura debe ser procesada como factura "
             "electrónica colombiana ante la DIAN."
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------

    @api.depends('move_type', 'journal_id', 'company_id')
    def _compute_insotech_is_co_edi(self):
        """Determine if a move is a Colombian EDI invoice.

        A move is considered Colombian EDI if:
        - It is a customer invoice or credit note (out_invoice / out_refund)
        - The company's country is Colombia
        - The journal is configured for DIAN electronic invoicing

        We detect DIAN-enabled journals by checking if the l10n_co_dian
        module has added EDI configuration to the journal. The exact field
        name may vary; we use a defensive approach checking multiple
        possible indicators.
        """
        for move in self:
            is_co_edi = False
            if move.move_type in ('out_invoice', 'out_refund'):
                company = move.company_id
                journal = move.journal_id
                # Check if company is Colombian
                if company and company.country_id and \
                        company.country_id.code == 'CO':
                    # Check if journal has DIAN EDI enabled
                    # Try multiple possible field names from l10n_co_dian
                    is_co_edi = self._insotech_check_journal_dian_enabled(
                        journal
                    )
            move.insotech_is_co_edi = is_co_edi

    # -------------------------------------------------------------------------
    # PRIVATE HELPERS
    # -------------------------------------------------------------------------

    def _insotech_check_journal_dian_enabled(self, journal):
        """Check if a journal is enabled for DIAN electronic invoicing.

        This method uses a defensive approach, checking multiple possible
        field indicators that the l10n_co_dian module may use. This ensures
        compatibility even if field names change between Odoo versions.

        :param journal: account.journal recordset
        :returns: True if DIAN EDI is enabled for this journal
        """
        if not journal:
            return False

        # Possible field names used by l10n_co_dian to mark a journal
        # as DIAN-enabled. We check all known possibilities.
        dian_field_candidates = [
            'l10n_co_dian_enabled',          # Direct DIAN flag
            'l10n_co_edi_is_direct_sending',  # Direct sending to DIAN
            'l10n_co_edi_dian_env',           # DIAN environment config
        ]

        for field_name in dian_field_candidates:
            if hasattr(journal, field_name):
                value = getattr(journal, field_name)
                if value:
                    _logger.debug(
                        "Insotech: Journal '%s' detected as DIAN-enabled "
                        "via field '%s'", journal.name, field_name
                    )
                    return True

        # Fallback: Check if the journal has any EDI format related to
        # Colombian DIAN configured (works with edi.format if available)
        if hasattr(journal, 'edi_format_ids'):
            for edi_format in journal.edi_format_ids:
                if 'co_dian' in (edi_format.code or '').lower() or \
                        'l10n_co' in (edi_format.code or '').lower():
                    _logger.debug(
                        "Insotech: Journal '%s' detected as DIAN-enabled "
                        "via edi_format '%s'", journal.name, edi_format.code
                    )
                    return True

        # Final fallback: if company is CO and journal type is 'sale',
        # assume it's DIAN-enabled (conservative — can be refined after
        # first deploy)
        if journal.type == 'sale' and \
                journal.company_id.country_id.code == 'CO':
            _logger.debug(
                "Insotech: Journal '%s' assumed as DIAN-enabled "
                "(CO sale journal fallback)", journal.name
            )
            return True

        return False

    def _insotech_get_pre_inv_name(self):
        """Generate a temporary PRE-INV name using ir.sequence.

        :returns: string like 'PRE-INV/2026/00001'
        """
        return self.env['ir.sequence'].next_by_code('insotech.pre.inv') \
            or 'PRE-INV/0000'

    # NOTE: _insotech_get_next_dian_name() was removed.
    # Instead, we store the original name assigned by _post() in
    # insotech_reserved_dian_name and restore it on DIAN acceptance.
    # This is more reliable than trying to recompute the sequence.

    # -------------------------------------------------------------------------
    # OVERRIDDEN METHODS — Sequence Protection
    # -------------------------------------------------------------------------

    def _post(self, soft=True):
        """Override _post to protect DIAN resolution consecutives.

        For Colombian EDI invoices (out_invoice, out_refund on DIAN-enabled
        journals), this method:
        1. Lets super()._post() run normally (assigns journal sequence name).
        2. Immediately replaces the name with a temporary PRE-INV/YYYY/NNNNN.
        3. Marks the invoice as 'pending' DIAN validation.

        For non-Colombian-EDI invoices, the flow is completely untouched.
        """
        # Call super first — this assigns the journal sequence name
        posted = super()._post(soft=soft)

        for move in posted:
            try:
                if move.insotech_is_co_edi and \
                        move.move_type in ('out_invoice', 'out_refund'):
                    # The journal sequence has been consumed by super()._post()
                    # We need to:
                    # 1. Save the assigned name (for potential future use)
                    # 2. Replace with PRE-INV temporary name
                    # 3. Mark as pending DIAN validation
                    # Store the original name assigned by _post()
                    # This is the DIAN resolution number that Odoo consumed
                    original_name = move.name
                    pre_inv_name = move._insotech_get_pre_inv_name()

                    _logger.info(
                        "Insotech: Protecting DIAN consecutive for move %s. "
                        "Original name: %s → Temporary: %s",
                        move.id, original_name, pre_inv_name
                    )

                    # Write the temporary name, store the reserved DIAN
                    # name, and set status to pending
                    move.with_context(
                        skip_account_move_synchronization=True
                    ).write({
                        'name': pre_inv_name,
                        'insotech_pre_inv_name': pre_inv_name,
                        'insotech_reserved_dian_name': original_name,
                        'insotech_dian_status': 'pending',
                    })

                    # Log in chatter
                    move.message_post(
                        body=_(
                            "🔒 <b>Protección de consecutivo DIAN activada</b>"
                            "<br/>Nombre temporal asignado: <b>%s</b>"
                            "<br/>El número definitivo de la resolución DIAN "
                            "se asignará tras la aceptación electrónica.",
                            pre_inv_name
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )

            except Exception as e:
                _logger.error(
                    "Insotech: Error protecting DIAN consecutive for "
                    "move %s: %s. The move was posted with its original "
                    "name to avoid blocking operations.",
                    move.id, str(e)
                )
                # Don't raise — let the invoice post normally rather
                # than blocking the business operation

        return posted

    # -------------------------------------------------------------------------
    # DIAN RESPONSE PROCESSING — Mutation to Legal Sequence
    # -------------------------------------------------------------------------

    def _insotech_process_dian_acceptance(self):
        """Process a DIAN acceptance: mutate PRE-INV → legal DIAN name.

        This method should be called when the DIAN ApplicationResponse
        indicates the invoice was accepted. It:
        1. Gets the next legal number from the journal's DIAN sequence.
        2. Replaces the PRE-INV name with the legal name.
        3. Increments insotech_usage_count on the company.
        4. Logs the mutation in the chatter.
        """
        for move in self:
            if move.insotech_dian_status != 'pending':
                _logger.warning(
                    "Insotech: Attempted to process DIAN acceptance for "
                    "move %s which is not in 'pending' status (current: %s)",
                    move.id, move.insotech_dian_status
                )
                continue

            try:
                # Restore the reserved DIAN name
                legal_name = move.insotech_reserved_dian_name
                if not legal_name:
                    raise UserError(_(
                        "No se encontró el nombre DIAN reservado para "
                        "la factura %s. Contacte a soporte técnico.",
                        move.name
                    ))

                old_name = move.name

                _logger.info(
                    "Insotech: DIAN accepted move %s. "
                    "Mutating name: %s → %s",
                    move.id, old_name, legal_name
                )

                # Write the legal name and update status
                move.with_context(
                    skip_account_move_synchronization=True
                ).write({
                    'name': legal_name,
                    'insotech_dian_status': 'accepted',
                })

                # Increment usage counter on the company
                company = move.company_id
                company.sudo().write({
                    'insotech_usage_count':
                        company.insotech_usage_count + 1
                })

                # Log in chatter
                move.message_post(
                    body=_(
                        "✅ <b>Factura aceptada por la DIAN</b>"
                        "<br/>Número temporal: <b>%s</b>"
                        "<br/>Número definitivo asignado: <b>%s</b>"
                        "<br/>El consecutivo de la resolución DIAN ha "
                        "sido asignado exitosamente.",
                        old_name, legal_name
                    ),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )

            except Exception as e:
                _logger.error(
                    "Insotech: Error processing DIAN acceptance for "
                    "move %s: %s",
                    move.id, str(e)
                )
                raise UserError(_(
                    "Error al procesar la aceptación DIAN para la "
                    "factura %s: %s\n\n"
                    "Por favor contacte a soporte técnico.",
                    move.name, str(e)
                ))

    def _insotech_process_dian_rejection(self, error_message=''):
        """Process a DIAN rejection: keep PRE-INV name and log error.

        This method should be called when the DIAN ApplicationResponse
        indicates the invoice was rejected. The PRE-INV name stays
        intact, and NO DIAN consecutive is lost.

        :param error_message: The error message/reason from the DIAN
        """
        for move in self:
            if move.insotech_dian_status not in ('pending', 'rejected'):
                _logger.warning(
                    "Insotech: Attempted to process DIAN rejection for "
                    "move %s which is in '%s' status",
                    move.id, move.insotech_dian_status
                )
                continue

            _logger.warning(
                "Insotech: DIAN rejected move %s (name: %s). "
                "Error: %s",
                move.id, move.name, error_message
            )

            move.write({
                'insotech_dian_status': 'rejected',
            })

            # Log details in chatter
            move.message_post(
                body=_(
                    "❌ <b>Factura rechazada por la DIAN</b>"
                    "<br/>Nombre temporal conservado: <b>%s</b>"
                    "<br/><b>Motivo del rechazo:</b> %s"
                    "<br/><br/>📝 Corrija el error y use el botón "
                    "<i>'Reintentar Envío DIAN'</i> para volver a enviar. "
                    "<b>No se ha perdido ningún consecutivo</b> de la "
                    "resolución DIAN.",
                    move.name,
                    error_message or _("No se recibió detalle del error.")
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

    # -------------------------------------------------------------------------
    # DIAN SEND INTERCEPTION — License Validation
    # -------------------------------------------------------------------------

    def _insotech_validate_license_before_dian(self):
        """Validate the Insotech SaaS license before sending to DIAN.

        This method should be called just before the HTTP call to the
        DIAN webservice is made. It validates the license using
        insotech_core's _validate_and_report_license() method.

        :raises UserError: if the license is not valid
        """
        for move in self:
            if not move.insotech_is_co_edi:
                continue

            company = move.company_id
            try:
                if not company._validate_and_report_license():
                    raise UserError(_(
                        "Su licencia Insotech no está activa o ha expirado.\n\n"
                        "El envío de la factura electrónica a la DIAN ha sido "
                        "bloqueado. Puede seguir creando y confirmando "
                        "facturas, pero no podrá transmitirlas a la DIAN "
                        "hasta renovar su licencia.\n\n"
                        "Por favor, contacte a soporte en www.insotech.it "
                        "para renovarla."
                    ))
            except UserError:
                raise
            except Exception as e:
                _logger.error(
                    "Insotech: Unexpected error validating license for "
                    "move %s: %s. Allowing operation to continue.",
                    move.id, str(e)
                )
                # In case of unexpected errors in license validation,
                # allow the operation to continue to avoid blocking
                # the client's business

    # -------------------------------------------------------------------------
    # HOOKS INTO l10n_co_dian — Intercept DIAN Send & Response
    # -------------------------------------------------------------------------
    # These methods attempt to override the l10n_co_dian module's methods
    # for sending to DIAN and processing responses. The exact method names
    # may need adjustment after the first deployment depending on the
    # actual implementation of l10n_co_dian in Odoo 19 Enterprise.
    # -------------------------------------------------------------------------

    def _l10n_co_dian_post(self, *args, **kwargs):
        """Override l10n_co_dian's posting/sending method.

        Injects license validation before the DIAN API call.
        Falls through to super() if the method exists.
        """
        self._insotech_validate_license_before_dian()
        if hasattr(super(), '_l10n_co_dian_post'):
            return super()._l10n_co_dian_post(*args, **kwargs)
        return True

    def _l10n_co_edi_send(self, *args, **kwargs):
        """Override l10n_co_edi's send method (alternative hook).

        Injects license validation before the DIAN API call.
        Falls through to super() if the method exists.
        """
        self._insotech_validate_license_before_dian()
        if hasattr(super(), '_l10n_co_edi_send'):
            return super()._l10n_co_edi_send(*args, **kwargs)
        return True

    def _hook_invoice_document_before_pdf(self, *args, **kwargs):
        """Override the Print & Send hook for DIAN document processing.

        In Odoo 19, the Print & Send wizard (account_move_send) uses
        hook methods to allow localization modules to inject logic
        before generating the final PDF. We use this hook to:
        1. Validate the Insotech license
        2. After the response, process acceptance or rejection

        Falls through to super() if the method exists.
        """
        self._insotech_validate_license_before_dian()
        if hasattr(super(), '_hook_invoice_document_before_pdf'):
            return super()._hook_invoice_document_before_pdf(
                *args, **kwargs
            )
        return True

    # -------------------------------------------------------------------------
    # USER ACTIONS
    # -------------------------------------------------------------------------

    def action_insotech_retry_dian(self):
        """Button action: retry sending a rejected invoice to DIAN.

        Resets the status to 'pending' and triggers the DIAN send
        process again. The user should have corrected the rejection
        cause before clicking this button.
        """
        for move in self:
            if move.insotech_dian_status != 'rejected':
                raise UserError(_(
                    "Solo puede reintentar el envío de facturas que "
                    "hayan sido rechazadas por la DIAN."
                ))

            # Validate license before retrying
            move._insotech_validate_license_before_dian()

            # Reset to pending
            move.write({
                'insotech_dian_status': 'pending',
            })

            move.message_post(
                body=_(
                    "🔄 <b>Reintento de envío a la DIAN</b>"
                    "<br/>El usuario ha iniciado un reintento de envío. "
                    "La factura será reenviada con el nombre temporal "
                    "<b>%s</b>.",
                    move.name
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

            _logger.info(
                "Insotech: User requested DIAN retry for move %s (%s)",
                move.id, move.name
            )

            # Trigger the DIAN send process
            # Try multiple possible methods that l10n_co_dian might use
            if hasattr(move, 'action_send_and_print'):
                return move.action_send_and_print()
            elif hasattr(move, 'action_l10n_co_dian_send'):
                return move.action_l10n_co_dian_send()
            elif hasattr(move, 'button_send_dian'):
                return move.button_send_dian()
            else:
                _logger.warning(
                    "Insotech: No known DIAN send method found for "
                    "retry on move %s. Opening Print & Send wizard.",
                    move.id
                )
                # Fallback: open the send and print wizard
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.move.send',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'active_ids': self.ids,
                        'active_model': 'account.move',
                    },
                }

    def action_insotech_force_dian_accept(self):
        """Manual action: force DIAN acceptance (admin only).

        This is a safety valve for cases where the DIAN accepted
        the invoice but our module didn't catch the response
        automatically. Should only be used by administrators.

        Requires the user to be in the Accounting / Adviser group.
        """
        self.ensure_one()
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_(
                "Solo los administradores contables pueden forzar "
                "la aceptación DIAN manualmente."
            ))

        if self.insotech_dian_status not in ('pending', 'rejected'):
            raise UserError(_(
                "Solo se puede forzar la aceptación para facturas "
                "en estado 'Pendiente' o 'Rechazada'."
            ))

        self._insotech_process_dian_acceptance()

        _logger.warning(
            "Insotech: Admin user %s forced DIAN acceptance for "
            "move %s (%s)",
            self.env.user.login, self.id, self.name
        )
