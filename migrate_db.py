"""
Database migration script to add authentication and notification features.
Run this script to update the existing database schema.
"""

import sqlite3
import os

db_path = "fixit_tech.db"

if not os.path.exists(db_path):
    print("Database not found. It will be created automatically on server startup.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add new columns to customers table
    print("Adding authentication columns to customers table...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(customers)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'hashed_password' not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN hashed_password VARCHAR(255)")
        print("  ✓ Added hashed_password column")
    
    if 'is_active' not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN is_active INTEGER DEFAULT 1 NOT NULL")
        print("  ✓ Added is_active column")
    
    if 'last_login' not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN last_login DATETIME")
        print("  ✓ Added last_login column")
    
    # Create customer_notifications table
    print("\nCreating customer_notifications table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            ticket_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
        )
    """)
    print("  ✓ Created customer_notifications table")
    
    # Create admins table
    print("\nCreating admins table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            is_active INTEGER DEFAULT 1 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            last_login DATETIME
        )
    """)
    print("  ✓ Created admins table")
    
    # Create indexes
    print("\nCreating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_notifications_customer_id ON customer_notifications(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer_notifications_created_at ON customer_notifications(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email)")
    print("  ✓ Created indexes")
    
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    conn.rollback()
    
finally:
    conn.close()
