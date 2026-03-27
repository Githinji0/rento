import sqlite3


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
            notes TEXT
        )
    """)
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