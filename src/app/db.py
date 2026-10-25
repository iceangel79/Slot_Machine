"""Database access with plain SQL (decision 0010)."""

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

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


def ensure_default_configuration(name, config):
    """Store the default configuration if no configuration exists yet."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO configurations (name, reel_strips, paytable)
            SELECT %s, %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM configurations)
            """,
            (name, Jsonb(config["reel_strips"]), Jsonb(config["paytable"])),
        )


def list_configurations():
    """Return all configurations (without reel strips and paytable), newest first."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, created_at FROM configurations ORDER BY id DESC"
        ).fetchall()


def get_configuration(configuration_id):
    """Return one configuration as dict, or None if it does not exist."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, created_at, reel_strips, paytable
            FROM configurations
            WHERE id = %s
            """,
            (configuration_id,),
        ).fetchone()


def insert_configuration(name, config):
    """Store a new configuration and return its id.

    Configurations are never changed afterwards (decision 0007).
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO configurations (name, reel_strips, paytable)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (name, Jsonb(config["reel_strips"]), Jsonb(config["paytable"])),
        ).fetchone()
    return row["id"]


def insert_spins(configuration_id, results, rng_source):
    """Store spins (results of game.spin) in one transaction.

    executemany sends all rows in one go, which keeps mass simulations fast
    even though the database is reached over the network.
    """
    rows = [
        (
            configuration_id,
            *result["symbols"],
            result["bet"],
            result["payout"],
            rng_source,
        )
        for result in results
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO spins (configuration_id, symbol_1, symbol_2, symbol_3,
                                   bet, payout, rng_source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
