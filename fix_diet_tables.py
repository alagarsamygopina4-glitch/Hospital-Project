import sqlite3
import os

# Identify the database path
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
print("Database path:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 1: Detect and Drop all tables starting with 'diet_' to clean up any schema mismatch
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'diet_%'")
diet_tables = [row[0] for row in cursor.fetchall()]

print(f"Found existing tables to drop: {diet_tables}")

# Disable Foreign Key checks for clean drop
cursor.execute("PRAGMA foreign_keys = OFF")

for table in diet_tables:
    cursor.execute(f"DROP TABLE IF EXISTS [{table}]")
    print(f"Dropped: {table}")

# Step 2: Clear diet migration records so Django will re-create them correctly
cursor.execute("DELETE FROM django_migrations WHERE app='diet'")
print("Cleared diet migration history from django_migrations table.")

# Step 3: Re-enable Foreign Key checks
cursor.execute("PRAGMA foreign_keys = ON")

conn.commit()

# Final Verification
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'diet_%'")
remaining = [r[0] for r in cursor.fetchall()]
print(f"Remaining diet tables: {remaining}")

conn.close()
print("\nDatabase is now clean! Running 'python manage.py migrate diet' will recreate fresh tables.")
