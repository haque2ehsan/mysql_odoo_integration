{
    'name': 'MySQL to Odoo19 Integration',
    'version': '19.0.1.1.0',
    'category': 'UU-IT',
    'summary': 'Authenticate portal users against MySQL (Laravel ERP) credentials',
    'description': """
        MySQL to Odoo19 Integration
        ============================
        - Portal employees log in using their Laravel ERP (MySQL) username and password
        - MySQL username maps to employee Badge ID in Odoo
        - Passwords verified against bcrypt hashes (Laravel default)
        - MySQL connection configurable from Settings → General Settings
    """,
    'author': 'Md Ehsanul Haque',
    'license': 'OPL-1',
    'depends': [
        'base_setup',
        'hr',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
