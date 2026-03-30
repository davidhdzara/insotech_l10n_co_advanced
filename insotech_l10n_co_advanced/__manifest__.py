{
    'name': 'Insotech — Localización Colombiana Avanzada',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Protección de consecutivos DIAN y facturación electrónica segura para Colombia',
    'description': """
        Extiende la localización nativa colombiana para proteger los consecutivos
        de resolución DIAN contra rechazos técnicos y errores de datos.

        Características principales:
        - Secuencia temporal PRE-INV al confirmar facturas electrónicas
        - Mutación a secuencia legal (FE-) tras aceptación DIAN
        - Protección total contra pérdida de consecutivos
        - Validación de licencia SaaS antes del envío a la DIAN
        - Banners informativos de estado DIAN en la factura
        - Contador visual de resolución DIAN
        - Contingencia Tipo 04: retry automático + retransmisión
    """,
    'author': 'Insotech',
    'website': 'https://www.insotech.it',
    'depends': [
        'account',
        'l10n_co_edi',
        'l10n_co_dian',
        'mail',
        'insotech_core',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/cron_contingency.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/report_invoice_document_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
