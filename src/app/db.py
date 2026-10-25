"""Database access with plain SQL (decision 0010)."""

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def get_connection():
    """Open a new connection to the database given in DATABASE_URL.

    Rows are returned as dictionaries, e.g. {"id": 1, "name": "Classic"}.
    Use it in a with block: the transaction is committed at the end of the
    block and rolled back if an exception occurs.
    """
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)


def init_schema():
    """Create the tables if they do not exist yet."""
    with get_connection() as conn:
        conn.execute(SCHEMA_FILE.read_text(encoding="utf-8"))


def check_connection():
    """Run a trivial query. Raises an exception if the database is unreachable."""
    with get_connection() as conn:
        conn.execute("SELECT 1")
