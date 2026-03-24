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
        deposit REAL,

        
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