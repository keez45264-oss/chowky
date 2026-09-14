"""
Promotes a user to admin on the local SQLite database.
Usage: python scripts/make_admin.py your@email.com
"""
import os
import sqlite3
import sys

if len(sys.argv) != 2:
    print("Usage: python scripts/make_admin.py your@email.com")
    raise SystemExit(1)

email = sys.argv[1].strip().lower()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "app", "chowky.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT id FROM users WHERE email = ?", (email,))
user = cur.fetchone()

if user is None:
    print(f"No user found with email {email}")
    raise SystemExit(1)

cur.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
conn.commit()
print(f"{email} is now an admin. Log out and back in for it to take effect.")