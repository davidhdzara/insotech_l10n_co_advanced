{
    'name': 'Insotech — Localización Colombiana Avanzada',
    'version': '19.0.1.2.0',
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
    """,
    'author': 'Insotech',
    'website': 'https://www.insotech.it',
    'depends': [
        'account',
        'l10n_co_edi',
        'l10n_co_dian',
        'insotech_core',
        'insotech_dian_wizard',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

