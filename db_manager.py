"""
SQLite Database Connection and Schema Management.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from src.config import DATABASE_PATH


class DatabaseManager:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    @contextmanager
    def get_connection(self):
        """Context manager for SQLite connection with automatic closing."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def initialize_schema(self):
        """Create tables if they don't already exist and seed default settings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Company Settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    company_name TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    gstin TEXT,
                    pan TEXT,
                    state_code TEXT,
                    logo_path TEXT,
                    invoice_prefix TEXT DEFAULT 'INV-',
                    next_invoice_num INTEGER DEFAULT 1,
                    invoice_num_padding INTEGER DEFAULT 3,
                    default_cgst_rate REAL DEFAULT 9.0,
                    default_sgst_rate REAL DEFAULT 9.0,
                    default_igst_rate REAL DEFAULT 18.0,
                    bank_name TEXT,
                    bank_acc_no TEXT,
                    bank_ifsc TEXT,
                    bank_branch TEXT,
                    upi_id TEXT,
                    default_terms TEXT,
                    declaration TEXT DEFAULT 'Certified that the above particulars are true & correct'
                )
            """)

            # 2. Customers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    gstin TEXT,
                    pan TEXT,
                    state_code TEXT,
                    shipping_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Products/Services Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    hsn_code TEXT,
                    unit TEXT DEFAULT 'NOS',
                    default_rate REAL DEFAULT 0.0,
                    tax_rate REAL DEFAULT 18.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Invoices Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_no TEXT UNIQUE NOT NULL,
                    invoice_date TEXT NOT NULL,
                    due_date TEXT,
                    po_no TEXT,
                    po_date TEXT,
                    vehicle_no TEXT,
                    copy_type TEXT DEFAULT 'Original Copy',
                    customer_id INTEGER,
                    billed_to_name TEXT NOT NULL,
                    billed_to_address TEXT,
                    billed_to_phone TEXT,
                    billed_to_email TEXT,
                    billed_to_gstin TEXT,
                    billed_to_state_code TEXT,
                    shipped_to_name TEXT,
                    shipped_to_address TEXT,
                    shipped_to_phone TEXT,
                    shipped_to_email TEXT,
                    shipped_to_gstin TEXT,
                    shipped_to_state_code TEXT,
                    subtotal REAL NOT NULL,
                    cgst_rate REAL DEFAULT 0.0,
                    cgst_amount REAL DEFAULT 0.0,
                    sgst_rate REAL DEFAULT 0.0,
                    sgst_amount REAL DEFAULT 0.0,
                    igst_rate REAL DEFAULT 0.0,
                    igst_amount REAL DEFAULT 0.0,
                    total_tax REAL NOT NULL,
                    grand_total REAL NOT NULL,
                    total_in_words TEXT,
                    payment_status TEXT DEFAULT 'Unpaid',
                    payment_method TEXT,
                    notes TEXT,
                    terms TEXT,
                    pdf_path TEXT,
                    docx_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
                )
            """)

            # 5. Invoice Items Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    s_no INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    hsn_code TEXT,
                    quantity REAL NOT NULL DEFAULT 1.0,
                    unit TEXT DEFAULT 'NOS',
                    rate REAL NOT NULL DEFAULT 0.0,
                    amount REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
                )
            """)

            # Seed default company settings if empty (using Namura Engg. Works from reference invoice!)
            cursor.execute("SELECT COUNT(*) FROM company_settings WHERE id = 1")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO company_settings (
                        id, company_name, address, phone, email,
                        gstin, pan, state_code, invoice_prefix,
                        next_invoice_num, invoice_num_padding,
                        default_cgst_rate, default_sgst_rate, default_igst_rate,
                        declaration
                    ) VALUES (
                        1,
                        'NAMURA ENGG. WORKS',
                        '4/8, Balaji Nagar, Vilankurichi, Coimbatore-641035',
                        '9842811245',
                        'namuraew@gmail.com',
                        '33BKXPS7582P1ZR',
                        'BKXPS7582P',
                        '33',
                        'INV-',
                        1,
                        3,
                        9.0,
                        9.0,
                        18.0,
                        'Certified that the above particulars are true & correct'
                    )
                """)

            # Seed initial sample products and customers if empty
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO products (name, description, hsn_code, unit, default_rate, tax_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    ("Precision CNC Machining", "CNC Turned Precision Bushings (SS304)", "8483", "NOS", 450.00, 18.0),
                    ("Hydraulic Cylinder Repair", "Complete overhaul and seal replacement", "8412", "SET", 2800.00, 18.0),
                    ("Sheet Metal Fabrication", "Custom Laser Cut & Bent Enclosure", "7326", "KG", 185.00, 18.0),
                    ("Industrial Flange Adapter", "Cast Iron Flange 150mm Grade 25", "7307", "NOS", 1250.00, 18.0)
                ])

            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO customers (name, address, phone, email, gstin, pan, state_code, shipping_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    (
                        "Apex Industries Pvt Ltd",
                        "Plot No. 45, Phase II, SIDCO Industrial Estate, Coimbatore - 641021",
                        "9443210987",
                        "purchase@apexindustries.com",
                        "33AAACA1234A1Z5",
                        "AAACA1234A",
                        "33",
                        "Plot No. 45, Phase II, SIDCO Industrial Estate, Coimbatore - 641021"
                    ),
                    (
                        "TechMech Systems",
                        "12/A, Peenya Industrial Area, 3rd Phase, Bangalore - 560058",
                        "9880011223",
                        "orders@techmechsystems.in",
                        "29AABCT5678B1Z2",
                        "AABCT5678B",
                        "29",
                        "12/A, Peenya Industrial Area, 3rd Phase, Bangalore - 560058"
                    )
                ])

            conn.commit()
