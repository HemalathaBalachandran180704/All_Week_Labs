import sqlite3
import random
import datetime
from faker import Faker

fake = Faker()

def generate_imei():
    return ''.join([str(random.randint(0, 9)) for _ in range(15)])

# ------------------ Connect ------------------
DB_NAME = "nlp_sql.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ------------------ Create Tables ------------------
def create_tables():
    tables = [
        "assignment_jobs", "technician_assignments", "job_photos", "job_notes", "jobs",
        "old_mobiles", "customers", "store_technicians", "user_stores", "users", "stores"
    ]
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")

    # Stores
    cursor.execute("""
    CREATE TABLE stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        created_at TEXT DEFAULT (DATETIME('now'))
    );
    """)

    # Users
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin','manager','staff','technician')) DEFAULT 'staff',
        full_name TEXT,
        email TEXT,
        store_id INTEGER,
        created_at TEXT DEFAULT (DATETIME('now')),
        last_login TEXT,
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL
    );
    """)

    # User Stores
    cursor.execute("""
    CREATE TABLE user_stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        store_id INTEGER NOT NULL,
        is_primary BOOLEAN DEFAULT 0,
        assigned_at TEXT DEFAULT (DATETIME('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
    );
    """)

    # Store Technicians
    cursor.execute("""
    CREATE TABLE store_technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER NOT NULL,
        technician_id INTEGER NOT NULL,
        assigned_at TEXT DEFAULT (DATETIME('now')),
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
        FOREIGN KEY (technician_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Customers
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        store_id INTEGER,
        created_at TEXT DEFAULT (DATETIME('now')),
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL
    );
    """)

    # Jobs
    cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        device_type TEXT NOT NULL,
        device_model TEXT,
        device_password_type TEXT,
        device_password TEXT,
        notification_methods TEXT,
        problem_description TEXT NOT NULL,
        deposit_cost REAL DEFAULT 0,
        raw_cost REAL DEFAULT 0,
        estimate_cost REAL DEFAULT 0,
        actual_cost REAL DEFAULT 0,
        payment_status TEXT DEFAULT 'Pending',
        payment_method TEXT,
        status TEXT DEFAULT 'New',
        store_id INTEGER,
        assigned_by INTEGER,
        created_at TEXT DEFAULT (DATETIME('now')),
        updated_at TEXT DEFAULT (DATETIME('now')),
        completed_at TEXT,
        started_at TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL,
        FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # Job Notes
    cursor.execute("""
    CREATE TABLE job_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at TEXT DEFAULT (DATETIME('now')),
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Job Photos
    cursor.execute("""
    CREATE TABLE job_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        photo BLOB NOT NULL,
        uploaded_at TEXT DEFAULT (DATETIME('now')),
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Technician Assignments
    cursor.execute("""
    CREATE TABLE technician_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technician_id INTEGER NOT NULL,
        assigned_by INTEGER,
        assigned_at TEXT DEFAULT (DATETIME('now')),
        started_at TEXT,
        completed_at TEXT,
        status TEXT DEFAULT 'active',
        notes TEXT,
        FOREIGN KEY (technician_id) REFERENCES users(id),
        FOREIGN KEY (assigned_by) REFERENCES users(id)
    );
    """)

    # Assignment Jobs
    cursor.execute("""
    CREATE TABLE assignment_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        FOREIGN KEY (assignment_id) REFERENCES technician_assignments(id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Old Mobiles
    cursor.execute("""
    CREATE TABLE old_mobiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT,
        aadhar_number TEXT,
        customer_address TEXT,
        mobile_brand TEXT NOT NULL,
        mobile_model TEXT NOT NULL,
        imei_number TEXT,
        repair_status TEXT NOT NULL,
        warranty_status TEXT NOT NULL,
        repair_description TEXT,
        estimated_value REAL DEFAULT 0,
        purchase_date DATE,
        accessories_included TEXT,
        notes TEXT,
        store_id INTEGER,
        created_at TEXT DEFAULT (DATETIME('now')),
        updated_at TEXT DEFAULT (DATETIME('now')),
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL
    );
    """)

# ------------------ Insert Sample Data ------------------
def safe_choice(lst):
    return random.choice(lst) if lst else None

def insert_stores(n=20):
    for _ in range(n):
        cursor.execute("""
            INSERT INTO stores (name, location, phone, email, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (fake.company(), fake.city(), fake.phone_number(), fake.company_email(),
              datetime.datetime.now().isoformat()))

def insert_users(n=50):
    store_ids = [row[0] for row in cursor.execute("SELECT id FROM stores").fetchall()]
    roles = ["admin", "manager", "staff", "technician"]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, email, store_id, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fake.user_name(), fake.password(), random.choice(roles), fake.name(),
              fake.email(), safe_choice(store_ids),
              datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()))

# You can similarly define insert_user_stores, insert_customers, insert_jobs, etc.
# For brevity, you can keep your existing insert functions with `safe_choice` added.

# ------------------ Run Setup ------------------
create_tables()
insert_stores(20)
insert_users(50)
# insert_user_stores(30)
# insert_customers(40)
# insert_jobs(60)
# insert_job_notes(40)
# insert_store_technicians(30)
# insert_technician_assignments(20)
# insert_assignment_jobs(20)
# insert_old_mobiles(30)

conn.commit()
conn.close()
print(f"✅ Database '{DB_NAME}' created and test data inserted successfully!")
