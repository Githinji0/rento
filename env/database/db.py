import sqlite3
from datetime import date


DB_NAME = "rent_management.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def _get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def _migrate_properties_schema(cursor):
    columns = set(_get_table_columns(cursor, "properties"))

    # Older databases may not have the columns used by the current UI.
    if "name" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN name TEXT")
    if "address" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN address TEXT")
    if "description" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN description TEXT")

    columns = set(_get_table_columns(cursor, "properties"))

    if "item_name" in columns:
        cursor.execute(
            """
            UPDATE properties
            SET name = COALESCE(NULLIF(name, ''), item_name)
            WHERE name IS NULL OR name = ''
            """
        )
    elif "customer_name" in columns:
        cursor.execute(
            """
            UPDATE properties
            SET name = COALESCE(NULLIF(name, ''), customer_name)
            WHERE name IS NULL OR name = ''
            """
        )

    cursor.execute("UPDATE properties SET address = '' WHERE address IS NULL")
    cursor.execute("UPDATE properties SET description = '' WHERE description IS NULL")


def _migrate_payments_schema(cursor):
    columns = set(_get_table_columns(cursor, "payments"))

    # Older databases may not have the current field used by the payments UI.
    if "month_covered" not in columns:
        cursor.execute("ALTER TABLE payments ADD COLUMN month_covered TEXT")

    columns = set(_get_table_columns(cursor, "payments"))
    if "payment_date" not in columns:
        cursor.execute("ALTER TABLE payments ADD COLUMN payment_date TEXT")

    cursor.execute(
        "UPDATE payments SET month_covered = '' WHERE month_covered IS NULL"
    )

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            description TEXT
        )
        """
    )
    _migrate_properties_schema(cursor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER,
        unit_number TEXT,
        rent_amount REAL,
        status TEXT
    )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        unit_id INTEGER,
        move_in DATE,
        deposit REAL

        
    )

    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER,
            amount REAL,
            payment_date TEXT,
            month_covered TEXT,
            notes TEXT
        )
    """)
    _migrate_payments_schema(cursor)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS dashboard_monthly_snapshots (
            month_key TEXT PRIMARY KEY,
            properties INTEGER NOT NULL,
            units INTEGER NOT NULL,
            occupied INTEGER NOT NULL,
            vacant INTEGER NOT NULL,
            arrears REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            role TEXT,
            bio TEXT,
            is_active INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    cursor.execute("SELECT COUNT(*) FROM user_profiles")
    profile_count = cursor.fetchone()[0]
    if profile_count == 0:
        cursor.execute(
            """
            INSERT INTO user_profiles
                (full_name, email, phone, role, bio, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                "Administrator",
                "admin@rento.local",
                "",
                "System Admin",
                "Default system profile",
            ),
        )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'manager',
            is_enabled INTEGER NOT NULL DEFAULT 1,
            last_login TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_at TEXT NOT NULL DEFAULT (datetime('now')),
            logout_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES auth_users(id)
        )
        """
    )
    conn.commit()
    conn.close()



# ===== PROPERTY OPERATIONS =====

def get_properties():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, description FROM properties")
    data = cursor.fetchall()
    conn.close()
    return data


def add_property(name, address, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO properties (name, address, description) VALUES (?, ?, ?)",
        (name, address, description),
    )
    conn.commit()
    conn.close()


def update_property(prop_id, name, address, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE properties
           SET name=?, address=?, description=?
           WHERE id=?""",
        (name, address, description, prop_id),
    )
    conn.commit()
    conn.close()


def delete_property(prop_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id=?", (prop_id,))
    conn.commit()
    conn.close()



# ===== UNIT OPERATIONS =====

def get_units():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT units.id, properties.name, unit_number,
               rent_amount, status
        FROM units
        LEFT JOIN properties
        ON units.property_id = properties.id
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def add_unit(property_id, unit_number, rent_amount, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO units
           (property_id, unit_number, rent_amount, status)
           VALUES (?, ?, ?, ?)""",
        (property_id, unit_number, rent_amount, status),
    )

    conn.commit()
    conn.close()


def update_unit(unit_id, property_id, unit_number, rent_amount, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE units
           SET property_id=?, unit_number=?,
               rent_amount=?, status=?
           WHERE id=?""",
        (property_id, unit_number, rent_amount, status, unit_id),
    )

    conn.commit()
    conn.close()


def delete_unit(unit_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM units WHERE id=?", (unit_id,))
    conn.commit()
    conn.close()


def get_property_list():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM properties")
    data = cursor.fetchall()

    conn.close()
    return data



# ===== TENANT OPERATIONS =====

def get_tenants():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tenants.id, tenants.name,
               tenants.phone, tenants.email,
               units.unit_number,
               tenants.move_in,
               tenants.deposit
        FROM tenants
        LEFT JOIN units
        ON tenants.unit_id = units.id
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def add_tenant(name, phone, email, unit_id, move_in, deposit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO tenants
           (name, phone, email, unit_id, move_in, deposit)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, phone, email, unit_id, move_in, deposit),
    )

    conn.commit()
    conn.close()


def update_tenant(tenant_id, name, phone, email, unit_id, move_in, deposit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE tenants
           SET name=?, phone=?, email=?,
               unit_id=?, move_in=?, deposit=?
           WHERE id=?""",
        (name, phone, email, unit_id, move_in, deposit, tenant_id),
    )

    conn.commit()
    conn.close()


def delete_tenant(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tenants WHERE id=?", (tenant_id,))
    conn.commit()
    conn.close()


def get_unit_list():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT units.id, units.unit_number
        FROM units
    """)

    data = cursor.fetchall()
    conn.close()
    return data



# ===== PAYMENT OPERATIONS =====

def get_payments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT payments.id,
               tenants.name,
               payments.amount,
               payments.payment_date,
               payments.month_covered
        FROM payments
        LEFT JOIN tenants
        ON payments.tenant_id = tenants.id
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def add_payment(tenant_id, amount, payment_date, month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO payments
           (tenant_id, amount, payment_date, month_covered)
           VALUES (?, ?, ?, ?)""",
        (tenant_id, amount, payment_date, month),
    )

    conn.commit()
    conn.close()


def delete_payment(payment_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM payments WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()


def get_tenant_list():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM tenants")
    data = cursor.fetchall()

    conn.close()
    return data


# ===== ARREARS CALCULATION =====

def get_tenant_rent(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT units.rent_amount
        FROM tenants
        JOIN units ON tenants.unit_id = units.id
        WHERE tenants.id=?
    """, (tenant_id,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def get_total_paid(tenant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM payments
        WHERE tenant_id=?
    """, (tenant_id,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0



# ===== DASHBOARD STATS =====

def count_properties():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM properties")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_units():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM units")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_occupied_units():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM units WHERE status='Occupied'")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_vacant_units():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM units WHERE status='Vacant'")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def count_tenants():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tenants")
    result = cursor.fetchone()[0]
    conn.close()
    return result


def total_income():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM payments")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0


def total_arrears():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tenants.id
        FROM tenants
    """)
    tenants = cursor.fetchall()

    total = 0

    for (tenant_id,) in tenants:
        cursor.execute("""
            SELECT units.rent_amount
            FROM tenants
            JOIN units ON tenants.unit_id = units.id
            WHERE tenants.id=?
        """, (tenant_id,))
        rent = cursor.fetchone()

        cursor.execute("""
            SELECT SUM(amount)
            FROM payments
            WHERE tenant_id=?
        """, (tenant_id,))
        paid = cursor.fetchone()

        rent_val = rent[0] if rent else 0
        paid_val = paid[0] if paid[0] else 0

        total += (rent_val - paid_val)

    conn.close()
    return total


def get_monthly_income(month_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE month_covered = ?
           OR substr(payment_date, 1, 7) = ?
        """,
        (month_key, month_key),
    )
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total


def upsert_dashboard_monthly_snapshot(
    month_key,
    properties,
    units,
    occupied,
    vacant,
    arrears,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO dashboard_monthly_snapshots
            (month_key, properties, units, occupied, vacant, arrears)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(month_key) DO UPDATE SET
            properties = excluded.properties,
            units = excluded.units,
            occupied = excluded.occupied,
            vacant = excluded.vacant,
            arrears = excluded.arrears
        """,
        (month_key, properties, units, occupied, vacant, arrears),
    )
    conn.commit()
    conn.close()


def get_dashboard_monthly_snapshot(month_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT properties, units, occupied, vacant, arrears
        FROM dashboard_monthly_snapshots
        WHERE month_key = ?
        """,
        (month_key,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "properties": row[0],
        "units": row[1],
        "occupied": row[2],
        "vacant": row[3],
        "arrears": row[4],
    }


def get_current_month_key():
    return date.today().strftime("%Y-%m")


# ===== USER PROFILE OPERATIONS =====

def get_user_profiles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, email, phone, role, bio, is_active
        FROM user_profiles
        ORDER BY full_name ASC
        """
    )
    data = cursor.fetchall()
    conn.close()
    return data


def add_user_profile(full_name, email, phone, role, bio, is_active=False):
    conn = get_connection()
    cursor = conn.cursor()

    if is_active:
        cursor.execute("UPDATE user_profiles SET is_active = 0")

    cursor.execute(
        """
        INSERT INTO user_profiles
            (full_name, email, phone, role, bio, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (full_name, email, phone, role, bio, 1 if is_active else 0),
    )
    conn.commit()
    conn.close()


def update_user_profile(profile_id, full_name, email, phone, role, bio, is_active=False):
    conn = get_connection()
    cursor = conn.cursor()

    if is_active:
        cursor.execute("UPDATE user_profiles SET is_active = 0")

    cursor.execute(
        """
        UPDATE user_profiles
        SET full_name=?, email=?, phone=?, role=?, bio=?, is_active=?
        WHERE id=?
        """,
        (full_name, email, phone, role, bio, 1 if is_active else 0, profile_id),
    )
    conn.commit()
    conn.close()


def delete_user_profile(profile_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_active FROM user_profiles WHERE id=?", (profile_id,))
    row = cursor.fetchone()
    was_active = bool(row and row[0])

    cursor.execute("DELETE FROM user_profiles WHERE id=?", (profile_id,))

    if was_active:
        cursor.execute(
            """
            UPDATE user_profiles
            SET is_active = 1
            WHERE id = (
                SELECT id FROM user_profiles
                ORDER BY created_at ASC
                LIMIT 1
            )
            """
        )

    conn.commit()
    conn.close()


def set_active_user_profile(profile_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_profiles SET is_active = 0")
    cursor.execute("UPDATE user_profiles SET is_active = 1 WHERE id=?", (profile_id,))
    conn.commit()
    conn.close()


def get_active_user_profile():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, email, phone, role, bio
        FROM user_profiles
        WHERE is_active = 1
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_monthly_income_report(limit=6):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT month_key, total
        FROM (
            SELECT
                COALESCE(NULLIF(month_covered, ''), substr(payment_date, 1, 7)) AS month_key,
                COALESCE(SUM(amount), 0) AS total
            FROM payments
            GROUP BY month_key
        )
        WHERE month_key IS NOT NULL
          AND month_key != ''
        ORDER BY month_key DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return rows


def get_property_occupancy_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            properties.name,
            COALESCE(SUM(CASE WHEN units.status = 'Occupied' THEN 1 ELSE 0 END), 0) AS occupied,
            COALESCE(SUM(CASE WHEN units.status = 'Vacant' THEN 1 ELSE 0 END), 0) AS vacant,
            COUNT(units.id) AS total_units
        FROM properties
        LEFT JOIN units ON units.property_id = properties.id
        GROUP BY properties.id, properties.name
        ORDER BY properties.name
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_tenant_arrears_report(limit=12):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            tenants.name,
            COALESCE(units.unit_number, '-') AS unit_number,
            COALESCE(units.rent_amount, 0) AS rent_amount,
            COALESCE(SUM(payments.amount), 0) AS paid_amount,
            COALESCE(units.rent_amount, 0) - COALESCE(SUM(payments.amount), 0) AS arrears
        FROM tenants
        LEFT JOIN units ON tenants.unit_id = units.id
        LEFT JOIN payments ON payments.tenant_id = tenants.id
        GROUP BY tenants.id, tenants.name, units.unit_number, units.rent_amount
        ORDER BY arrears DESC, tenants.name ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ===== AUTHENTICATION OPERATIONS =====

def create_auth_user(full_name, username, email, password_hash, password_salt, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO auth_users
            (full_name, username, email, password_hash, password_salt, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (full_name, username, email, password_hash, password_salt, role),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_auth_user_by_identifier(identifier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, username, email, password_hash, password_salt, role, is_enabled
        FROM auth_users
        WHERE lower(username) = lower(?) OR lower(email) = lower(?)
        LIMIT 1
        """,
        (identifier, identifier),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_auth_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, full_name, username, email, role, is_enabled
        FROM auth_users
        WHERE id = ?
        LIMIT 1
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_auth_user_self(user_id, full_name, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE auth_users
        SET full_name = ?, email = ?
        WHERE id = ?
        """,
        (full_name, email, user_id),
    )
    conn.commit()
    conn.close()


def update_auth_last_login(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE auth_users SET last_login = datetime('now') WHERE id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def create_auth_session(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO auth_sessions (user_id) VALUES (?)",
        (user_id,),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def close_auth_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE auth_sessions
        SET logout_at = datetime('now'), is_active = 0
        WHERE id = ?
        """,
        (session_id,),
    )
    conn.commit()
    conn.close()