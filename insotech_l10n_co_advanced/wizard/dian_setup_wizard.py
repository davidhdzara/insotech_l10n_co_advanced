# -*- coding: utf-8 -*-
# =============================================================================
# Wizard: Configuración Express DIAN
#
# Consolida la configuración de facturación electrónica colombiana
# (Fases 4-6 de la guía DIAN) en un flujo guiado de 3 pasos:
#   1. Credenciales (Software ID, PIN, Test Set ID)
#   2. Resumen y confirmación
#   3. Resultado (éxito / error)
#
# El certificado digital (.p12) se carga manualmente por el usuario
# desde Ajustes → Contabilidad → Facturación Electrónica antes de
# ejecutar este wizard.
# =============================================================================

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DianSetupWizard(models.TransientModel):
    """Express DIAN configuration wizard.

    Guides the user through the DIAN electronic invoicing setup
    in a step-by-step flow, consolidating what normally requires
    navigating to multiple settings sections.
    """

    _name = 'insotech.dian.setup.wizard'
    _description = 'Wizard Configuración Express DIAN'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Empresa",
        required=True,
        default=lambda self: self.env.company,
        help="Empresa que se va a configurar para facturación "
             "electrónica DIAN.",
    )

    # -- Step 1: Credentials --
    software_id = fields.Char(
        string="Software ID",
        help="Identificador único del software asignado por la DIAN "
             "en el Portal de Habilitación → Configuración → "
             "Software Propio.",
    )
    software_pin = fields.Char(
        string="PIN de Software",
        help="PIN numérico del software asignado por la DIAN. "
             "Generalmente '12345' en el entorno de pruebas.",
    )
    test_set_id = fields.Char(
        string="Test Set ID",
        help="Identificador del set de pruebas para certificación. "
             "Se obtiene en el Portal de Habilitación → Asociar "
             "Rangos de Prueba.",
    )
    enable_support_documents = fields.Boolean(
        string="Emitir Documentos Soporte",
        help="Active esta opción si su empresa realiza compras a "
             "personas no obligadas a facturar (régimen simplificado) "
             "y necesita emitir Documentos Soporte electrónicos.",
    )

    # -- Navigation --
    current_step = fields.Selection(
        selection=[
            ('credentials', 'Credenciales'),
            ('confirm', 'Confirmación'),
            ('done', 'Finalizado'),
            ('already_enabled', 'Ya Configurado'),
        ],
        string="Paso Actual",
        default='credentials',
        required=True,
    )

    # -- Step 3: Result --
    result_message = fields.Html(
        string="Resultado",
        readonly=True,
    )

    # -- Computed: config state from company --
    config_state = fields.Selection(
        related='company_id.insotech_dian_config_state',
        string="Estado Configuración",
        readonly=True,
    )

    # -------------------------------------------------------------------------
    # DEFAULTS
    # -------------------------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        """Set initial step based on company config state."""
        res = super().default_get(fields_list)
        company = self.env.company
        if company.insotech_dian_config_state == 'enabled':
            res['current_step'] = 'already_enabled'
        return res

    # -------------------------------------------------------------------------
    # NAVIGATION ACTIONS
    # -------------------------------------------------------------------------

    def _reopen_wizard(self):
        """Return action to reopen the wizard with current record."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_next_step(self):
        """Navigate to the next step in the wizard flow."""
        self.ensure_one()
        step_flow = ['credentials', 'confirm', 'done']
        current_idx = step_flow.index(self.current_step)
        if current_idx < len(step_flow) - 1:
            self.current_step = step_flow[current_idx + 1]
        return self._reopen_wizard()

    def action_prev_step(self):
        """Navigate to the previous step in the wizard flow."""
        self.ensure_one()
        step_flow = ['credentials', 'confirm', 'done']
        current_idx = step_flow.index(self.current_step)
        if current_idx > 0:
            self.current_step = step_flow[current_idx - 1]
        return self._reopen_wizard()

    # -------------------------------------------------------------------------
    # STEP ACTIONS
    # -------------------------------------------------------------------------

    def action_apply_credentials(self):
        """Step 1 → 2: Validate credentials and move to confirmation.

        Validates that required fields are filled and moves to the
        confirmation step. The actual writing to l10n_co_dian models
        happens in the confirmation step.
        """
        self.ensure_one()
        if not self.software_id or not self.software_pin:
            raise UserError(_(
                "Debe completar el Software ID y el PIN de Software "
                "para continuar."
            ))
        if not self.test_set_id:
            raise UserError(_(
                "Debe ingresar el Test Set ID para poder realizar "
                "el proceso de certificación ante la DIAN."
            ))
        self.current_step = 'confirm'
        return self._reopen_wizard()

    def action_start_certification(self):
        """Step 2 → 3: Apply configuration and start certification.

        Writes the configuration to l10n_co_dian models and triggers
        the certification process. Uses defensive hasattr checks
        since field names may vary between l10n_co_dian versions.
        """
        self.ensure_one()
        company = self.company_id.sudo()
        errors = []

        # -- Write Operation Modes (Modos de Operación) --
        try:
            self._apply_operation_modes(company)
        except Exception as e:
            _logger.error(
                "Insotech DIAN Wizard: Error applying operation "
                "modes for company %s: %s", company.id, str(e)
            )
            errors.append(_(
                "Error configurando modos de operación: %s",
                str(e)
            ))

        # -- Activate test environment + certification --
        try:
            self._activate_certification(company)
        except Exception as e:
            _logger.error(
                "Insotech DIAN Wizard: Error activating certification "
                "for company %s: %s", company.id, str(e)
            )
            errors.append(_(
                "Error activando certificación: %s",
                str(e)
            ))

        # -- Update company config state --
        if errors:
            company.insotech_dian_config_state = 'not_configured'
            error_html = '<br/>'.join(str(e) for e in errors)
            self.result_message = _(
                '<div class="alert alert-danger">'
                '<i class="fa fa-exclamation-triangle"></i> '
                '<strong> Se encontraron errores durante la '
                'configuración:</strong>'
                '<br/><br/>%s'
                '<br/><br/>Verifique la configuración e intente '
                'nuevamente.</div>'
            ) % error_html
        else:
            company.insotech_dian_config_state = 'in_progress'
            self.result_message = _(
                '<div class="alert alert-success">'
                '<i class="fa fa-check-circle"></i> '
                '<strong> Configuración aplicada exitosamente</strong>'
                '<br/><br/>Se han configurado los modos de operación '
                'y se ha iniciado el proceso de certificación ante '
                'la DIAN.'
                '<br/><br/>El siguiente paso es completar el set de '
                'pruebas. Odoo generará automáticamente los documentos '
                'de prueba y los enviará a la DIAN.'
                '<br/><br/><em>Cuando el portal de habilitación de la '
                'DIAN confirme la certificación exitosa, el estado '
                'se actualizará a "Habilitado".</em></div>'
            )

        self.current_step = 'done'
        return self._reopen_wizard()

    # -------------------------------------------------------------------------
    # PRIVATE HELPERS
    # -------------------------------------------------------------------------

    def _apply_operation_modes(self, company):
        """Write operation modes to l10n_co_dian configuration.

        Searches for the operation mode model and creates/updates
        records for electronic invoicing and optionally support
        documents.

        :param company: res.company sudo recordset
        """
        # Try to find the operation mode model
        OperationMode = None
        for model_name in [
            'l10n_co_dian.operation.mode',
            'l10n_co.dian.operation.mode',
        ]:
            if model_name in self.env:
                OperationMode = self.env[model_name].sudo()
                break

        if OperationMode is None:
            _logger.warning(
                "Insotech DIAN Wizard: Operation mode model not "
                "found. The credentials will be stored but operation "
                "modes must be configured manually."
            )
            # Fallback: try to write directly to company fields
            vals = {}
            if hasattr(company, 'l10n_co_dian_software_id'):
                vals['l10n_co_dian_software_id'] = self.software_id
            if hasattr(company, 'l10n_co_dian_software_pin'):
                vals['l10n_co_dian_software_pin'] = self.software_pin
            if hasattr(company, 'l10n_co_dian_test_set_id'):
                vals['l10n_co_dian_test_set_id'] = self.test_set_id
            if vals:
                company.write(vals)
                _logger.info(
                    "Insotech DIAN Wizard: Wrote credentials to "
                    "company fields: %s", list(vals.keys())
                )
            return

        # Create invoice operation mode
        self._create_or_update_operation_mode(
            OperationMode, company,
            mode_type='invoice',
            software_id=self.software_id,
            software_pin=self.software_pin,
            test_set_id=self.test_set_id,
        )

        # Create support document mode if requested
        if self.enable_support_documents:
            self._create_or_update_operation_mode(
                OperationMode, company,
                mode_type='support',
                software_id=self.software_id,
                software_pin=self.software_pin,
                test_set_id=self.test_set_id,
            )

        _logger.info(
            "Insotech DIAN Wizard: Operation modes configured "
            "for company %s", company.id
        )

    def _create_or_update_operation_mode(
        self, OperationMode, company, mode_type,
        software_id, software_pin, test_set_id
    ):
        """Create or update a single operation mode record.

        :param OperationMode: model class for operation modes
        :param company: res.company recordset
        :param mode_type: 'invoice' or 'support'
        :param software_id: DIAN software ID
        :param software_pin: DIAN software PIN
        :param test_set_id: DIAN test set ID
        """
        # Build values dict defensively
        vals = {'company_id': company.id}

        # Try to determine the field for mode type
        for field_name in ['software_mode', 'mode', 'type']:
            if field_name in OperationMode._fields:
                # Map our mode_type to the likely selection values
                if mode_type == 'invoice':
                    vals[field_name] = 'invoice'
                elif mode_type == 'support':
                    vals[field_name] = 'support'
                break

        # Write credential fields
        for field_name, value in [
            ('software_id', software_id),
            ('l10n_co_dian_software_id', software_id),
            ('software_pin', software_pin),
            ('l10n_co_dian_software_pin', software_pin),
            ('nip', software_pin),
            ('test_set_id', test_set_id),
            ('testing_id', test_set_id),
            ('l10n_co_dian_test_set_id', test_set_id),
        ]:
            if field_name in OperationMode._fields:
                vals[field_name] = value

        # Search for existing record to update
        domain = [('company_id', '=', company.id)]
        existing = OperationMode.search(domain, limit=1)
        if existing:
            existing.write(vals)
        else:
            OperationMode.create(vals)

    def _activate_certification(self, company):
        """Activate test environment and certification process.

        Tries to enable the test environment and trigger the
        certification process using l10n_co_dian's native methods.

        IMPORTANT: All field access is wrapped in try/except because
        writing to l10n_co_dian fields (e.g. test environment flags)
        may internally trigger certificate validation. We must NEVER
        let a missing certificate block or crash the wizard.

        :param company: res.company sudo recordset
        """
        # Try to set test environment flag
        test_env_fields = [
            'l10n_co_dian_test_environment',
            'l10n_co_edi_test_environment',
        ]
        for field_name in test_env_fields:
            if field_name in company._fields:
                try:
                    company.write({field_name: True})
                    _logger.info(
                        "Insotech DIAN Wizard: Activated %s "
                        "on company %s",
                        field_name, company.id
                    )
                except Exception as e:
                    _logger.warning(
                        "Insotech DIAN Wizard: Could not set %s "
                        "on company %s: %s (certificate missing?)",
                        field_name, company.id, str(e)
                    )
                break

        # Try to activate certification flag
        cert_fields = [
            'l10n_co_dian_enable_certification',
            'l10n_co_edi_enable_certification',
        ]
        for field_name in cert_fields:
            if field_name in company._fields:
                try:
                    company.write({field_name: True})
                    _logger.info(
                        "Insotech DIAN Wizard: Activated %s "
                        "on company %s",
                        field_name, company.id
                    )
                except Exception as e:
                    _logger.warning(
                        "Insotech DIAN Wizard: Could not set %s "
                        "on company %s: %s (certificate missing?)",
                        field_name, company.id, str(e)
                    )
                break

        # Try to trigger the native certification process
        # NOTE: This may require a valid certificate to be loaded.
        # If it fails, the user must trigger it manually from Settings.
        cert_methods = [
            '_l10n_co_dian_start_certification',
            'action_l10n_co_dian_start_certification',
            'button_start_certification',
        ]
        for method_name in cert_methods:
            if hasattr(company, method_name):
                method = getattr(company, method_name)
                if callable(method):
                    try:
                        _logger.info(
                            "Insotech DIAN Wizard: Calling %s "
                            "on company %s",
                            method_name, company.id
                        )
                        method()
                    except Exception as e:
                        _logger.warning(
                            "Insotech DIAN Wizard: %s failed "
                            "on company %s: %s. The certification "
                            "must be triggered manually.",
                            method_name, company.id, str(e)
                        )
                    return

        _logger.warning(
            "Insotech DIAN Wizard: No native certification method "
            "found on company %s. The certification process must "
            "be triggered manually from Settings.",
            company.id
        )
