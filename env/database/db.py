import sqlite3


DB_NAME = "rent_management.db"


def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            rental_date TEXT NOT NULL,
            return_date TEXT
        )
        """
    )
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
    cursor.execute("SELECT * FROM properties")
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