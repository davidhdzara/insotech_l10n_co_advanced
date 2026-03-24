# -*- coding: utf-8 -*-
import re
# =============================================================================
# INVESTIGACIÓN — Odoo 19 Enterprise + l10n_co_dian (2026-03-21)
#
# SequenceMixin (account/models/sequence_mixin.py):
#   - Odoo 19 NO usa ir.sequence para account.move. El name se computa
#     internamente via _compute_name() + _get_last_sequence().
#   - _get_last_sequence_domain() determina qué movimientos se consideran
#     para derivar el patrón de secuencia del diario.
#   - Nuestro override añade AND name NOT LIKE 'PRE-INV%' para evitar
#     contaminación del patrón.
#
# _post() en Odoo 19:
#   - El método se llama _post(soft=True), no action_post().
#   - Asigna el name al confirmar via SequenceMixin._compute_name().
#   - Nuestro approach: dejar que _post() asigne normalmente, guardar
#     el nombre original en insotech_reserved_dian_name, luego renombrar
#     a PRE-INV. Al aceptar DIAN, restaurar desde reserved.
#
# l10n_co_dian — Campos en account.move (verificados en staging):
#   l10n_co_edi_cufe_cude_ref        Char      CUFE/CUDE/CUDS
#   l10n_co_edi_type                 Selection Tipo de Documento
#   l10n_co_edi_operation_type       Selection Tipo de operación
#   l10n_co_edi_transaction          Char      ID de transacción (CO)
#   l10n_co_edi_attachment_url       Char      URL para Anexos
#   l10n_co_edi_is_support_document  Boolean   Documento de apoyo
#   l10n_co_edi_debit_note           Boolean   Nota de Débito
#   l10n_co_edi_payment_option_id    Many2one  Método de pago
#
# l10n_co_dian — Respuesta DIAN via account.edi.document:
#   state           Selection  Estado (to_send → sent = aceptada)
#   error           HTML       Mensaje de error DIAN (si rechaza)
#   move_id         Many2one   Factura vinculada
#   edi_format_id   Many2one   Formato EDI (DIAN)
#   edi_format_name Char       Nombre del formato
#   blocking_level  Selection  Nivel de bloqueo
#
# Hook automático: account_edi_document.py hereda account.edi.document
# y sobreescribe write() para detectar cambios de state/error.
# =============================================================================

import logging

from markupsafe import Markup
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

    # -- Resolution counter fields (Feature 2) --

    insotech_resolution_used = fields.Integer(
        string="Números Usados",
        compute='_compute_insotech_resolution_info',
        help="Cantidad de números de resolución DIAN consumidos "
             "en el diario actual.",
    )
    insotech_resolution_max = fields.Integer(
        string="Números Autorizados",
        compute='_compute_insotech_resolution_info',
        help="Rango total de números autorizados por la resolución "
             "DIAN del diario.",
    )
    insotech_resolution_percent = fields.Float(
        string="% Disponible",
        compute='_compute_insotech_resolution_info',
        help="Porcentaje de números de resolución DIAN disponibles.",
    )
    insotech_resolution_color = fields.Char(
        string="Color Resolución",
        compute='_compute_insotech_resolution_info',
        help="Clase CSS de color para el indicador de resolución.",
    )
    insotech_resolution_progress_width = fields.Integer(
        string="Ancho Barra Resolución",
        compute='_compute_insotech_resolution_info',
        help="Porcentaje de consumo para la barra de progreso.",
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

    @api.depends('journal_id', 'company_id')
    def _compute_insotech_resolution_info(self):
        """Compute DIAN resolution usage statistics.

        Reads the resolution range from the journal's l10n_co_edi
        configuration and counts how many invoices have been posted
        (excluding PRE-INV temporaries) to determine the consumption
        percentage of the DIAN resolution.

        Color thresholds:
        - Green (success): >50% available
        - Yellow (warning): 20-50% available
        - Red (danger): <20% available
        """
        for move in self:
            move.insotech_resolution_used = 0
            move.insotech_resolution_max = 0
            move.insotech_resolution_percent = 0.0
            move.insotech_resolution_color = ''
            move.insotech_resolution_progress_width = 0

            try:
                if not move.insotech_is_co_edi or not move.journal_id:
                    continue

                journal = move.journal_id

                # Read range fields from l10n_co_dian on the journal
                min_range = 0
                max_range = 0
                if 'l10n_co_edi_min_range_number' in journal._fields:
                    min_range = journal.l10n_co_edi_min_range_number or 0
                if 'l10n_co_edi_max_range_number' in journal._fields:
                    max_range = journal.l10n_co_edi_max_range_number or 0

                if not max_range:
                    continue

                total_authorized = max_range - min_range + 1

                # Count posted invoices in this journal
                # Exclude PRE-INV temporary names
                used_count = self.search_count([
                    ('journal_id', '=', journal.id),
                    ('state', '=', 'posted'),
                    ('move_type', 'in', (
                        'out_invoice', 'out_refund',
                    )),
                    ('name', 'not like', 'PRE-INV%'),
                ])

                percent_available = 0.0
                if total_authorized > 0:
                    percent_available = (
                        (total_authorized - used_count)
                        / total_authorized
                    ) * 100.0
                    # Clamp to 0-100
                    percent_available = max(
                        0.0, min(100.0, percent_available)
                    )

                # Determine color class
                if percent_available > 50:
                    color = 'success'
                elif percent_available > 20:
                    color = 'warning'
                else:
                    color = 'danger'

                move.insotech_resolution_used = used_count
                move.insotech_resolution_max = total_authorized
                move.insotech_resolution_percent = percent_available
                move.insotech_resolution_color = color
                move.insotech_resolution_progress_width = min(
                    100, int(100 - percent_available)
                )
            except Exception:
                _logger.debug(
                    "Insotech: Could not compute resolution info "
                    "for move %s, skipping.", move.id,
                    exc_info=True,
                )

    # -------------------------------------------------------------------------
    # RADIAN IRREVOCABILITY — Block NC/ND on accepted invoices
    # -------------------------------------------------------------------------

    def _insotech_check_radian_irrevocability(self):
        """Block NC/ND on invoices accepted as título valor (RADIAN).

        When a credit note (out_refund) references an invoice that has
        event 033 (Aceptación Expresa) or 035 (Aceptación Tácita),
        the invoice is considered irrevocable and NC/ND should be
        blocked.

        Users with the `group_radian_override` security group can
        bypass this check, but an alert is ALWAYS posted in the
        chatter.

        Legal basis: Resolución 000165/2023 (título valor)
        """
        RadianEvent = self.env.get('insotech.radian.event')
        if RadianEvent is None:
            return

        for move in self:
            if move.move_type != 'out_refund':
                continue

            # Find the original invoice this NC reverses
            original = move.reversed_entry_id
            if not original:
                continue

            # Check if the original has acceptance events (033/035)
            acceptance_count = RadianEvent.search_count([
                ('move_id', '=', original.id),
                ('event_code', 'in', ('033', '035')),
                ('state', '!=', 'error'),
            ])
            if not acceptance_count:
                continue

            # This invoice has been accepted → irrevocable
            has_override = self.env.user.has_group(
                'insotech_l10n_co_advanced.group_radian_override'
            )

            if has_override:
                # User has override permission → allow but log alert
                _logger.warning(
                    "Insotech RADIAN: User %s (override group) "
                    "creating NC on accepted invoice %s",
                    self.env.user.login, original.name,
                )
                try:
                    move.message_post(
                        body=Markup(
                            '⚠️ <b>ALERTA RADIAN:</b> Esta Nota '
                            'Crédito se emite sobre la factura '
                            '<b>%s</b> que ya fue aceptada como '
                            'título valor.<br/>'
                            'Acción realizada por: <b>%s</b> '
                            '(permiso de override RADIAN).'
                        ) % (
                            original.name,
                            self.env.user.name,
                        ),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                except Exception:
                    pass
            else:
                # No override → BLOCK
                raise UserError(_(
                    "⛔ No se puede emitir una Nota Crédito sobre "
                    "la factura %s.\n\n"
                    "Esta factura ya fue aceptada como título valor "
                    "(evento RADIAN 033/035) y es irrevocable.\n\n"
                    "Si necesita emitir esta NC, contacte al "
                    "administrador para que le asigne el permiso:\n"
                    "\"RADIAN: Permitir NC/ND sobre facturas "
                    "aceptadas\"",
                    original.name,
                ))

    # -------------------------------------------------------------------------
    # PRIVATE HELPERS
    # -------------------------------------------------------------------------

    def _insotech_check_journal_dian_enabled(self, journal):
        """Check if a journal is enabled for DIAN electronic invoicing.

        Verified in Odoo 19 Enterprise staging (2026-03-21):
        The key field is l10n_co_dian_provider (Selection) on account.journal.
        When this field has a value, the journal is configured for DIAN EDI.

        Additionally, l10n_co_edi_dian_authorization_number contains the
        resolution number — if present, the journal has a valid DIAN
        resolution configured.

        Fields on account.journal (l10n_co_dian):
          l10n_co_dian_provider                  Selection  Proveedor DIAN
          l10n_co_dian_technical_key              Char       Clave técnica
          l10n_co_edi_dian_authorization_number   Char       Resolución
          l10n_co_edi_dian_authorization_date     Date       Fecha resolución
          l10n_co_edi_dian_authorization_end_date Date       Fecha fin
          l10n_co_edi_min_range_number            Integer    Número inicial
          l10n_co_edi_max_range_number            Integer    Número final

        :param journal: account.journal recordset
        :returns: True if DIAN EDI is enabled for this journal
        """
        if not journal:
            return False

        # Primary check: l10n_co_dian_provider is the field Odoo 19 uses
        # to mark a journal as DIAN-enabled (Selection field)
        if hasattr(journal, 'l10n_co_dian_provider'):
            if journal.l10n_co_dian_provider:
                _logger.debug(
                    "Insotech: Journal '%s' is DIAN-enabled "
                    "(l10n_co_dian_provider = '%s')",
                    journal.name, journal.l10n_co_dian_provider
                )
                return True

        # Secondary check: journal has a DIAN resolution number configured
        if hasattr(journal, 'l10n_co_edi_dian_authorization_number'):
            if journal.l10n_co_edi_dian_authorization_number:
                _logger.debug(
                    "Insotech: Journal '%s' has DIAN resolution '%s'",
                    journal.name,
                    journal.l10n_co_edi_dian_authorization_number
                )
                return True

        # No DIAN configuration found — do NOT intervene
        _logger.debug(
            "Insotech: Journal '%s' has NO DIAN configuration. "
            "Skipping PRE-INV protection.",
            journal.name
        )
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
    # SEQUENCEMIXIN PROTECTION — Prevent PRE-INV from corrupting sequences
    # -------------------------------------------------------------------------

    def _get_last_sequence_domain(self, relaxed=False):
        """Override to exclude PRE-INV temporary names from sequence search.

        Odoo 19's SequenceMixin uses _get_last_sequence_domain() to find
        the last posted name in the journal and derive the sequence pattern.
        If PRE-INV names are included, the SequenceMixin thinks the journal
        pattern is 'PRE-INV/YYYY/NNNNN' and generates more PRE-INV names
        instead of the real journal sequence (e.g. INV/2026/XXXX).

        This override adds a filter to exclude PRE-INV names from the
        sequence domain, ensuring the SequenceMixin always uses the
        real journal sequence pattern.
        """
        where_string, param = super()._get_last_sequence_domain(relaxed)
        # Exclude PRE-INV temporary names from the sequence search
        where_string += " AND name NOT LIKE 'PRE-INV%%'"
        return where_string, param

    # -------------------------------------------------------------------------
    # OVERRIDDEN METHODS — Sequence Protection
    # -------------------------------------------------------------------------

    def _post(self, soft=True):
        """Override _post to protect DIAN resolution consecutives.

        For Colombian EDI invoices (out_invoice, out_refund on DIAN-enabled
        journals), this method:
        1. Checks RADIAN irrevocability (blocks NC on accepted invoices).
        2. Lets super()._post() run normally (assigns journal sequence name).
        3. Immediately replaces the name with a temporary PRE-INV/YYYY/NNNNN.
        4. Marks the invoice as 'pending' DIAN validation.

        For non-Colombian-EDI invoices, the flow is completely untouched.
        """
        # --- RADIAN Irrevocability Check ---
        # Block NC/ND on invoices that have been accepted as título valor
        self._insotech_check_radian_irrevocability()

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
                        body=Markup(
                            '🔒 <b>Protección de consecutivo DIAN activada</b>'
                            '<br/>Nombre temporal: <b>%s</b>'
                            '<br/>El número definitivo se asignará tras '
                            'la aceptación electrónica.'
                        ) % pre_inv_name,
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
                # Compute the DIAN-compliant name
                # (e.g. FE/2026/00001 → FE1)
                dian_name = move._insotech_compute_dian_compliant_name()
                if not dian_name:
                    # Fallback: use whatever name the move has
                    # (may already be swapped to DIAN format)
                    dian_name = (
                        move.insotech_reserved_dian_name
                        or move.name
                    )
                    _logger.warning(
                        "Insotech: Could not compute DIAN name "
                        "for acceptance of move %s, using: %s",
                        move.id, dian_name,
                    )

                old_name = move.name

                _logger.info(
                    "Insotech: DIAN accepted move %s. "
                    "Final name: %s → %s",
                    move.id, old_name, dian_name
                )

                # Write the DIAN-compliant name and update status
                move.with_context(
                    skip_account_move_synchronization=True
                ).write({
                    'name': dian_name,
                    'insotech_dian_status': 'accepted',
                })

                # Increment usage counter on the company
                company = move.company_id
                company.sudo().write({
                    'insotech_usage_count':
                        company.insotech_usage_count + 1
                })

                # ── Capa 1: Persist last consecutive ──
                # Only persist if the invoice has a CUFE
                # (proof of real DIAN acceptance, not force-accept)
                cufe = getattr(
                    move, 'l10n_co_edi_cufe_cude_ref', None
                )
                if not cufe:
                    _logger.info(
                        "Insotech: Skipping Capa 1 persist for "
                        "move %s — no CUFE (force-accepted?)",
                        move.id,
                    )
                else:
                    num_match = re.search(
                        r'(\d+)\s*$', dian_name
                    )
                    if num_match:
                        dian_num = int(num_match.group(1))
                        param_key = (
                            'insotech.dian.last_consecutive.%d'
                            % move.journal_id.id
                        )
                        current = int(
                            self.env[
                                'ir.config_parameter'
                            ].sudo().get_param(param_key, '0')
                        )
                        if dian_num > current:
                            self.env[
                                'ir.config_parameter'
                            ].sudo().set_param(
                                param_key, str(dian_num)
                            )
                            _logger.info(
                                "Insotech: Persisted last DIAN "
                                "consecutive for journal %d: %d",
                                move.journal_id.id, dian_num,
                            )

                # Log in chatter
                move.message_post(
                    body=Markup(
                        '✅ <b>Factura aceptada por la DIAN</b>'
                        '<br/>Nombre temporal: %s'
                        '<br/>Número definitivo: <b>%s</b>'
                    ) % (old_name, dian_name),
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
        """Process a DIAN rejection: restore PRE-INV and log error.

        This method is called when the DIAN ApplicationResponse
        indicates the invoice was rejected. Since the name was
        swapped to the real DIAN name for sending, we must restore
        the PRE-INV name so no consecutive is lost.

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

            # Restore PRE-INV name so the consecutive is not lost
            pre_inv = move.insotech_pre_inv_name
            vals = {'insotech_dian_status': 'rejected'}
            if pre_inv and move.name != pre_inv:
                vals['name'] = pre_inv
                _logger.info(
                    "Insotech: Restoring PRE-INV name for rejected "
                    "move %s: %s → %s",
                    move.id, move.name, pre_inv,
                )
            move.with_context(
                skip_account_move_synchronization=True,
            ).write(vals)

            # Log in chatter
            move.message_post(
                body=Markup(
                    '❌ <b>Factura rechazada por la DIAN</b>'
                    '<br/>Nombre temporal conservado: <b>%s</b>'
                    '<br/><b>Motivo:</b> %s'
                    '<br/>Corrija el error y use '
                    '<i>"Reintentar Envío DIAN"</i>.'
                ) % (pre_inv or move.name,
                     error_message or 'Sin detalle'),
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

    def _insotech_check_duplicate_consecutive(self):
        """Capa 2: Pre-send check to avoid sending duplicates.

        Before sending to DIAN, compute the DIAN number that
        WOULD be sent and compare it against the last accepted
        consecutive stored in ir.config_parameter.

        If the number was already sent, raise UserError with
        the next available consecutive.

        This protects against:
        - DB restores where Odoo's sequence resets
        - Re-sends of previously accepted invoices
        """
        for move in self:
            if not move.insotech_is_co_edi:
                continue

            journal = move.journal_id
            param_key = (
                'insotech.dian.last_consecutive.%d'
                % journal.id
            )
            last_dian = int(
                self.env[
                    'ir.config_parameter'
                ].sudo().get_param(param_key, '0')
            )
            if not last_dian:
                continue

            # Compute what the DIAN number would be
            dian_name = move._insotech_compute_dian_compliant_name()
            if not dian_name:
                continue

            num_match = re.search(r'(\d+)\s*$', dian_name)
            if not num_match:
                continue

            dian_num = int(num_match.group(1))
            prefix = (journal.code or '').strip()

            if dian_num <= last_dian:
                # Verify the blocking consecutive has CUFE
                # (was actually sent to DIAN, not force-accepted)
                blocking_moves = self.env['account.move'].search([
                    ('journal_id', '=', journal.id),
                    ('state', '=', 'posted'),
                    ('insotech_dian_status', '=', 'accepted'),
                    ('name', '=like', '%s%%' % prefix),
                ], limit=100)
                has_cufe = any(
                    getattr(m, 'l10n_co_edi_cufe_cude_ref', None)
                    for m in blocking_moves
                    if re.search(r'(\d+)\s*$', m.name or '')
                    and int(
                        re.search(r'(\d+)\s*$', m.name).group(1)
                    ) >= dian_num
                )
                if not has_cufe:
                    _logger.info(
                        "Insotech: Capa 2 skip — consecutive %d "
                        "has no CUFE-backed invoice, allowing.",
                        dian_num,
                    )
                    continue

                next_available = last_dian + 1
                raise UserError(_(
                    "⚠️ El consecutivo %s%d ya fue enviado a la "
                    "DIAN previamente.\n\n"
                    "El último consecutivo registrado para este "
                    "diario es: %s%d\n\n"
                    "El siguiente disponible es: %s%d\n\n"
                    "Para corregir:\n"
                    "1. Vaya a la lista de facturas\n"
                    "2. Seleccione esta factura\n"
                    "3. Use 'Resecuenciar' para cambiar a %s%d",
                    prefix, dian_num,
                    prefix, last_dian,
                    prefix, next_available,
                    prefix, next_available,
                ))

    # -------------------------------------------------------------------------
    # NAME SWAP HELPERS — Swap between PRE-INV and real DIAN name
    # -------------------------------------------------------------------------

    def _insotech_compute_dian_compliant_name(self):
        """Compute a DIAN-compliant invoice name.

        DIAN expects format: ``{Prefix}{Number}``
        Examples: ``FE1``, ``FEI23``, ``FEGU5001``

        The prefix is read dynamically from ``journal.code``
        (can be any value: FE, FEI, FEGU, NC, ND, DS, etc.).

        The number is extracted from
        ``insotech_reserved_dian_name`` (the name Odoo assigned
        during ``_post()``, e.g. ``FE/2026/00001`` → 1).

        If the DIAN resolution range starts at a number > 1
        (e.g. min_range=5001) but Odoo's SequenceMixin starts
        at 1, the method auto-offsets the number so the first
        invoice gets ``FE5001`` instead of ``FE1``.

        Validates that the final number falls within the
        authorized range [min_range, max_range].

        :returns: DIAN-compliant name or None if not computable
        :raises UserError: if the number exceeds max_range
        """
        self.ensure_one()
        reserved = self.insotech_reserved_dian_name
        if not reserved:
            return None

        # Extract trailing number from reserved name
        # Handles: FE/2026/00001, FE/00001, FE1, etc.
        match = re.search(r'(\d+)\s*$', reserved)
        if not match:
            _logger.warning(
                "Insotech: Cannot extract number from "
                "reserved name '%s' for move %s",
                reserved, self.id,
            )
            return None

        # Strip leading zeros to get actual number
        raw_number = int(match.group(1))

        # Read prefix from journal code (dynamic per client)
        journal = self.journal_id
        prefix = (journal.code or '').strip()
        if not prefix:
            _logger.warning(
                "Insotech: Journal %s has no code/prefix "
                "for move %s",
                journal.id, self.id,
            )
            return None

        # ----------------------------------------------------------
        # DIAN RANGE VALIDATION & OFFSET
        # ----------------------------------------------------------
        # Read the authorized range from the journal
        min_range = getattr(
            journal, 'l10n_co_edi_min_range_number', 0
        ) or 0
        max_range = getattr(
            journal, 'l10n_co_edi_max_range_number', 0
        ) or 0

        if min_range and max_range:
            # Auto-offset: if Odoo's SequenceMixin starts at 1
            # but DIAN range starts at min_range, offset it.
            # Example: raw_number=1, min_range=5001
            #          → dian_number = 5001 + (1-1) = 5001
            # Example: raw_number=3, min_range=5001
            #          → dian_number = 5001 + (3-1) = 5003
            # Example: raw_number=1, min_range=1
            #          → dian_number = 1 + (1-1) = 1 (no change)
            if raw_number < min_range:
                dian_number = min_range + (raw_number - 1)
                _logger.info(
                    "Insotech: Offsetting number for move %s: "
                    "raw=%d, min_range=%d → dian=%d",
                    self.id, raw_number, min_range, dian_number,
                )
            else:
                # Number is already in range (l10n_co_dian
                # may have configured the SequenceMixin)
                dian_number = raw_number

            # Validate against max_range
            if dian_number > max_range:
                raise UserError(_(
                    "La resolución DIAN del diario '%s' se ha "
                    "agotado.\n\n"
                    "Número calculado: %s%d\n"
                    "Rango autorizado: %s%d – %s%d\n\n"
                    "Debe solicitar una nueva resolución de "
                    "facturación a la DIAN y configurarla en "
                    "el diario."
                ) % (
                    journal.name,
                    prefix, dian_number,
                    prefix, min_range,
                    prefix, max_range,
                ))
        else:
            # No range configured — use raw number
            dian_number = raw_number
            _logger.debug(
                "Insotech: No DIAN range configured on "
                "journal %s, using raw number %d",
                journal.id, raw_number,
            )

        dian_name = '%s%d' % (prefix, dian_number)
        return dian_name

    def _insotech_swap_to_dian_name(self):
        """Swap to DIAN-compliant name for XML generation.

        Before l10n_co_dian generates the UBL XML, ``move.name``
        must be in DIAN format (e.g. ``FE1``) instead of
        ``PRE-INV/2026/00001``.

        The reserved name (``FE/2026/00001``) is transformed
        to DIAN format (``FE1``) using the journal prefix +
        extracted sequence number.  No value is hardcoded.

        This swap is TEMPORARY — if DIAN rejects, the rejection
        handler restores the PRE-INV name. If DIAN accepts, the
        acceptance handler keeps the real name.
        """
        for move in self:
            if move.insotech_dian_status != 'pending':
                continue
            if not move.insotech_reserved_dian_name:
                continue

            dian_name = move._insotech_compute_dian_compliant_name()
            if not dian_name:
                _logger.warning(
                    "Insotech: Could not compute DIAN name "
                    "for move %s, using reserved name as-is: %s",
                    move.id, move.insotech_reserved_dian_name,
                )
                dian_name = move.insotech_reserved_dian_name

            if move.name != dian_name:
                _logger.info(
                    "Insotech: Swapping to DIAN name for "
                    "move %s: %s → %s (for XML generation)",
                    move.id, move.name, dian_name,
                )
                move.with_context(
                    skip_account_move_synchronization=True,
                ).write({'name': dian_name})

    def _insotech_swap_to_pre_inv_name(self):
        """Restore the PRE-INV name after a failed send attempt.

        Called when an exception occurs during the DIAN send so
        that the move keeps its protective PRE-INV name.
        """
        for move in self:
            pre_inv = move.insotech_pre_inv_name
            if pre_inv and move.name != pre_inv:
                _logger.info(
                    "Insotech: Restoring PRE-INV name for move %s: "
                    "%s → %s",
                    move.id, move.name, pre_inv,
                )
                move.with_context(
                    skip_account_move_synchronization=True,
                ).write({'name': pre_inv})

    # -------------------------------------------------------------------------
    # HOOKS INTO l10n_co_dian — Intercept DIAN Send & Response
    # -------------------------------------------------------------------------
    # These methods override l10n_co_dian's methods for sending to
    # DIAN. Before calling super(), we swap PRE-INV → real DIAN name
    # so the generated XML contains the correct invoice number.
    # If the send fails with an exception, we restore PRE-INV.
    # -------------------------------------------------------------------------

    def _l10n_co_dian_post(self, *args, **kwargs):
        """Override l10n_co_dian's posting/sending method.

        Swaps to real DIAN name before XML generation and
        validates the Insotech license.
        """
        self._insotech_validate_license_before_dian()
        self._insotech_swap_to_dian_name()
        try:
            if hasattr(super(), '_l10n_co_dian_post'):
                return super()._l10n_co_dian_post(
                    *args, **kwargs
                )
        except Exception:
            self._insotech_swap_to_pre_inv_name()
            raise
        return True

    def _l10n_co_edi_send(self, *args, **kwargs):
        """Override l10n_co_edi's send method (alternative hook).

        Swaps to real DIAN name before XML generation and
        validates the Insotech license.
        """
        self._insotech_validate_license_before_dian()
        self._insotech_swap_to_dian_name()
        try:
            if hasattr(super(), '_l10n_co_edi_send'):
                return super()._l10n_co_edi_send(
                    *args, **kwargs
                )
        except Exception:
            self._insotech_swap_to_pre_inv_name()
            raise
        return True

    def _hook_invoice_document_before_pdf(self, *args, **kwargs):
        """Override the Print & Send hook for DIAN processing.

        In Odoo 19, the Print & Send wizard (account_move_send)
        uses hook methods to allow localization modules to inject
        logic before generating the final PDF.  We swap to the
        real DIAN name so the XML contains the correct number.
        """
        self._insotech_validate_license_before_dian()
        self._insotech_swap_to_dian_name()
        try:
            if hasattr(
                super(), '_hook_invoice_document_before_pdf'
            ):
                return super()._hook_invoice_document_before_pdf(
                    *args, **kwargs
                )
        except Exception:
            self._insotech_swap_to_pre_inv_name()
            raise
        return True

    # -------------------------------------------------------------------------
    # MAIN INTERCEPTION — action_send_and_print (Odoo 19)
    # -------------------------------------------------------------------------
    # In Odoo 19, the user clicks "Enviar" → calls action_send_and_print()
    # on account.move → opens the account.move.send wizard.
    # l10n_co_dian hooks into this wizard to generate the XML.
    # We MUST swap the name BEFORE this flow starts.
    # -------------------------------------------------------------------------

    def action_send_and_print(self, **kwargs):
        """Override the Send & Print action to swap name first.

        This is the ENTRY POINT for the DIAN send flow.
        When the user clicks "Enviar", Odoo calls this method.
        We swap PRE-INV → DIAN name BEFORE the wizard opens,
        so l10n_co_dian generates the XML with the correct name.

        After super() returns, we check if DIAN accepted (CUFE
        was populated) and auto-process the acceptance.

        If the send fails with exception, restore PRE-INV.
        """
        self._insotech_validate_license_before_dian()

        # ── Capa 2: Pre-send duplicate check ──
        self._insotech_check_duplicate_consecutive()

        self._insotech_swap_to_dian_name()
        try:
            result = super().action_send_and_print(**kwargs)
        except Exception:
            self._insotech_swap_to_pre_inv_name()
            raise

        # -------------------------------------------------------
        # POST-SEND: Check if DIAN accepted during this call
        # -------------------------------------------------------
        # After the wizard completes, check if DIAN accepted.
        # We detect acceptance by checking if l10n_co_edi_cufe
        # was populated (CUFE = proof of DIAN acceptance).
        # This is MORE RELIABLE than the account.edi.document
        # write hook which may not fire correctly.
        # -------------------------------------------------------
        for move in self:
            if move.insotech_dian_status != 'pending':
                continue
            try:
                # Refresh from DB to get latest values
                move.invalidate_recordset(
                    ['l10n_co_edi_cufe_cude_ref']
                )
                cufe = getattr(
                    move, 'l10n_co_edi_cufe_cude_ref', None
                )
                if cufe:
                    _logger.info(
                        "Insotech: Post-send DIAN acceptance "
                        "detected for move %s (CUFE: %s...)",
                        move.id, str(cufe)[:20],
                    )
                    move._insotech_process_dian_acceptance()
            except Exception as e:
                _logger.warning(
                    "Insotech: Post-send acceptance check "
                    "failed for move %s: %s (non-blocking)",
                    move.id, str(e),
                )

        return result

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
                body=Markup(
                    '🔄 <b>Reintento de envío a la DIAN</b>'
                    '<br/>La factura será reenviada con nombre '
                    'temporal <b>%s</b>.'
                ) % move.name,
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

    def action_insotech_verify_cufe(self):
        """Open the DIAN portal to verify invoice CUFE.

        Opens the official DIAN catalog in a new browser tab
        using the invoice's CUFE/CUDE as the search key.

        Works with ANY journal prefix — reads the field
        l10n_co_edi_cufe_cude_ref dynamically.
        """
        self.ensure_one()
        cufe = getattr(self, 'l10n_co_edi_cufe_cude_ref', None)
        if not cufe:
            raise UserError(_(
                "Esta factura no tiene un CUFE/CUDE asignado. "
                "Solo puede verificar facturas que hayan sido "
                "enviadas y aceptadas por la DIAN."
            ))
        url = (
            'https://catalogo-vpfe.dian.gov.co/User/'
            'SearchDocument?DocumentKey=%s' % cufe
        )
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
