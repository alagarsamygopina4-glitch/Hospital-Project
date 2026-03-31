import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all diet tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'diet_%'")
tables = [row[0] for row in cursor.fetchall()]

# Check columns for each table
for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [(row[1], row[2]) for row in cursor.fetchall()]
    print(f"Columns in {table}: {cols}")

conn.close()
