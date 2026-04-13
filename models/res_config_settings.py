from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mysql_auth_enabled = fields.Boolean(
        string='Enable MySQL Authentication',
        config_parameter='mysql_odoo_integration.auth_enabled',
    )
    mysql_host = fields.Char(
        string='MySQL Host',
        config_parameter='mysql_odoo_integration.host',
        default='localhost',
    )
    mysql_port = fields.Char(
        string='MySQL Port',
        config_parameter='mysql_odoo_integration.port',
        default='3306',
    )
    mysql_database = fields.Char(
        string='MySQL Database',
        config_parameter='mysql_odoo_integration.database',
    )
    mysql_user = fields.Char(
        string='MySQL User',
        config_parameter='mysql_odoo_integration.user',
    )
    mysql_password = fields.Char(
        string='MySQL Password',
        config_parameter='mysql_odoo_integration.password',
    )
    mysql_table = fields.Char(
        string='MySQL Table',
        config_parameter='mysql_odoo_integration.table',
        default='users',
    )
    mysql_username_column = fields.Char(
        string='Username Column',
        config_parameter='mysql_odoo_integration.username_column',
        default='username',
    )
    mysql_password_column = fields.Char(
        string='Password Column',
        config_parameter='mysql_odoo_integration.password_column',
        default='password',
    )
