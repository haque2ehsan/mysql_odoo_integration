import logging

from odoo import api, models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)

try:
    import pymysql
except ImportError:
    pymysql = None
    _logger.warning("pymysql not installed. MySQL authentication will not work.")

try:
    import bcrypt
except ImportError:
    bcrypt = None
    _logger.warning("bcrypt not installed. MySQL password verification will not work.")


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_login_domain(self, login):
        """Extend login lookup to also match by employee Badge ID."""
        from odoo.orm.domains import Domain as OrmDomain
        domain = super()._get_login_domain(login)

        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('mysql_odoo_integration.auth_enabled') == 'True':
            employee = self.env['hr.employee'].sudo().search(
                [('barcode', '=', login), ('user_id', '!=', False)], limit=1
            )
            if employee and employee.user_id:
                return domain | OrmDomain('id', '=', employee.user_id.id)

        return domain

    def _check_credentials(self, credential, env):
        """MySQL-first auth for employees (portal users with Badge ID).
        Internal Odoo users authenticate normally via Odoo (email + password).
        """
        if credential.get('type') != 'password' or not credential.get('password'):
            return super()._check_credentials(credential, env)

        # Check if MySQL auth is enabled
        ICP = self.env['ir.config_parameter'].sudo()
        mysql_enabled = ICP.get_param('mysql_odoo_integration.auth_enabled') == 'True'

        # Determine if user is an employee with a Badge ID
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.user.id)], limit=1
        ) if mysql_enabled else None
        is_mysql_user = employee and employee.barcode

        if is_mysql_user:
            # Strategy: MySQL first, fall back to Odoo
            auth_info = self._mysql_authenticate(credential['password'], employee)
            if auth_info:
                return auth_info
            # MySQL failed — fall back to Odoo local password
            return super()._check_credentials(credential, env)
        else:
            # Internal user without Badge ID — Odoo auth only
            return super()._check_credentials(credential, env)

    def _mysql_authenticate(self, password, employee):
        """Authenticate against MySQL using the employee's Badge ID."""
        if not pymysql or not bcrypt:
            _logger.error("pymysql or bcrypt not available for MySQL authentication.")
            return False

        badge_id = employee.barcode

        # Get MySQL connection parameters
        ICP = self.env['ir.config_parameter'].sudo()
        config = {
            'host': ICP.get_param('mysql_odoo_integration.host', 'localhost'),
            'port': int(ICP.get_param('mysql_odoo_integration.port', '3306')),
            'database': ICP.get_param('mysql_odoo_integration.database', ''),
            'user': ICP.get_param('mysql_odoo_integration.user', ''),
            'password': ICP.get_param('mysql_odoo_integration.password', ''),
            'table': ICP.get_param('mysql_odoo_integration.table', 'users'),
            'username_col': ICP.get_param('mysql_odoo_integration.username_column', 'username'),
            'password_col': ICP.get_param('mysql_odoo_integration.password_column', 'password'),
        }

        if not config['database'] or not config['user']:
            _logger.warning("MySQL connection not configured.")
            return False

        conn = None
        try:
            conn = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                connect_timeout=5,
                read_timeout=5,
            )
            with conn.cursor() as cursor:
                # Use parameterized query — table/column names are from admin config, not user input
                query = "SELECT `{}` FROM `{}` WHERE `{}` = %s LIMIT 1".format(
                    config['password_col'],
                    config['table'],
                    config['username_col'],
                )
                cursor.execute(query, (badge_id,))
                row = cursor.fetchone()

            if not row or not row[0]:
                _logger.info("MySQL auth: no user found for badge_id=%s", badge_id)
                return False

            mysql_hashed = row[0]

            # Laravel stores bcrypt hashes (prefix $2y$), Python bcrypt uses $2b$
            if mysql_hashed.startswith('$2y$'):
                mysql_hashed = '$2b$' + mysql_hashed[4:]

            if bcrypt.checkpw(password.encode('utf-8'), mysql_hashed.encode('utf-8')):
                _logger.info("MySQL auth successful for badge_id=%s (user %s)",
                             badge_id, self.env.user.login)
                return {
                    'uid': self.env.user.id,
                    'auth_method': 'mysql',
                    'mfa': 'default',
                }

            _logger.info("MySQL auth: password mismatch for badge_id=%s", badge_id)
            return False

        except pymysql.Error as e:
            _logger.error("MySQL connection error: %s", e)
            return False
        except Exception as e:
            _logger.error("MySQL auth unexpected error: %s", e)
            return False
        finally:
            if conn:
                conn.close()
