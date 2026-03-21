{
    'name': 'Insotech L10n CO Advanced (DIAN)',
    'version': '19.0.1.0.0',
    'summary': 'Zero-gap electronic invoicing for Colombia — Decoupled sequence, smart retries, contingency mode.',
    'description': """
Extends Odoo 18 native l10n_co_dian module to enforce the following:
- Decoupled DIAN sequence: legal invoice number (FE-XXXX) is only consumed AFTER DIAN
  validates the XML — preventing gaps on rejection.
- Smart HTTP timeout (8s) to avoid freezing POS terminals when MUISCA is slow.
- Contingency Mode switch on journals for issuing paper-range invoices during outages.
- Async retry cron: re-sends technically-failed invoices every N hours, skips business
  logic rejections (invalid NIT, etc.) that require human intervention.
    """,
    'author': 'InSoTech / Guapante',
    'website': 'https://github.com/davidhdzara',
    'category': 'Accounting/Localizations/EDI',
    'license': 'OPL-1',
    'depends': [
        'account',
        'l10n_co',
        'l10n_co_dian',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
