"""
Run this once to create app/chowky.db from schema_sqlite.sql.
Usage: python scripts/init_db.py
"""
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "app", "chowky.db")
SCHEMA_PATH = os.path.join(ROOT, "schema_sqlite.sql")

if os.path.exists(DB_PATH):
    confirm = input(f"{DB_PATH} already exists. Delete and recreate? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        raise SystemExit(0)
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
with open(SCHEMA_PATH, "r") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()

print(f"Created {DB_PATH} from schema_sqlite.sql")
