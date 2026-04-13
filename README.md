# MySQL to Odoo 19 Integration

Authenticate Odoo portal users against a MySQL database (e.g., Laravel ERP) using their existing credentials. Employees log in with their **Badge ID** and **MySQL password** — no need to manage separate Odoo passwords.

## Features

- **MySQL-first authentication** for employees with a Badge ID
- **Fallback to Odoo** local password if MySQL auth fails
- **Internal users** (without Badge ID) authenticate normally via Odoo
- **Badge ID as login** — employees can use their Badge ID instead of email to log in
- **bcrypt password verification** — compatible with Laravel's default hashing (`$2y$`)
- **Configurable from Settings** — MySQL connection details managed in General Settings

## Requirements

| Package | Purpose |
|---------|---------|
| `pymysql` | MySQL database connector |
| `bcrypt` | Password hash verification |

Install in your Odoo virtual environment:

```bash
pip install pymysql bcrypt
```

## Installation

1. Place the module in your Odoo addons path
2. Update the app list: **Settings → Apps → Update Apps List**
3. Search for "MySQL to Odoo19 Integration" and install

## Configuration

### 1. MySQL Server Setup

On your Laravel/MySQL server, create a **read-only** database user for Odoo:

```sql
-- Run this on your MySQL server
CREATE USER 'odoo_reader'@'<odoo_server_ip>' IDENTIFIED BY 'strong_password_here';
GRANT SELECT ON your_database.users TO 'odoo_reader'@'<odoo_server_ip>';
FLUSH PRIVILEGES;
```

> **Security note:** Only grant `SELECT` permission on the users table. Odoo never writes to MySQL.

### 2. Odoo Settings

Go to **Settings → General Settings**, scroll to the **MySQL Authentication** section:

| Field | Description | Default |
|-------|-------------|---------|
| Enable MySQL Authentication | Toggle to activate/deactivate | Off |
| Host | MySQL server IP or hostname | `localhost` |
| Port | MySQL server port | `3306` |
| Database | MySQL database name | — |
| User | MySQL read-only user | — |
| Password | MySQL user password | — |
| Table | Table containing user credentials | `users` |
| Username Column | Column that stores the Badge ID | `username` |
| Password Column | Column with bcrypt password hash | `password` |

### 3. Employee Setup

Each Odoo employee that should use MySQL authentication needs:

- A **Badge ID** matching their `username` in the MySQL table
- A linked **Portal User** (res.users record)

## How It Works

```
User enters Badge ID + password on Odoo login page
        │
        ▼
┌─ Is MySQL auth enabled? ──── No ──→ Standard Odoo auth
│       │
│      Yes
│       │
│       ▼
│  Find employee by Badge ID
│       │
│   Found with Badge ID?
│       │           │
│      Yes          No ──→ Standard Odoo auth (email login)
│       │
│       ▼
│  Query MySQL for Badge ID
│       │
│  Verify bcrypt password
│       │
│   Match? ─── Yes ──→ ✅ Login successful
│       │
│      No
│       │
│       ▼
│  Fall back to Odoo local password
│       │
│   Match? ─── Yes ──→ ✅ Login successful
│       │
│      No ──→ ❌ Access Denied
```

## Login Options

| User Type | Login Field | Password Source |
|-----------|------------|-----------------|
| Employee with Badge ID | Badge ID (e.g., `240320`) | MySQL first, then Odoo |
| Employee with Badge ID | Email (e.g., `user@company.com`) | Odoo only |
| Internal user (no Badge ID) | Email | Odoo only |

## Compatibility

- **Odoo**: 19.0 Enterprise / Community
- **Python**: 3.10+
- **MySQL**: 5.7+ / MariaDB 10.3+
- **Password hashing**: bcrypt (`$2y$` Laravel / `$2b$` Python)

## License

MIT License — see [LICENSE](LICENSE)

## Author

**Md Ehsanul Haque**
