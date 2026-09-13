"""
Database connection helper.

- If DATABASE_URL is set (Render Postgres in production), use psycopg2.
- Otherwise, fall back to a local SQLite file for development.

Route code should use `get_db()` and always use parameterized queries
(never string-format values into SQL — this is how Virumart avoided
SQL injection, and the same rule applies here).
"""
import os
import sqlite3

from flask import current_app, g

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "chowky.db")


def get_db():
    if "db" not in g:
        database_url = current_app.config["DATABASE_URL"]
        if database_url:
            import psycopg2
            import psycopg2.extras

            g.db = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
            g.db_is_postgres = True
        else:
            g.db = sqlite3.connect(SQLITE_PATH)
            g.db.row_factory = sqlite3.Row
            g.db_is_postgres = False
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def placeholder():
    """Returns the correct SQL placeholder for the active DB engine."""
    return "%s" if g.get("db_is_postgres") else "?"
