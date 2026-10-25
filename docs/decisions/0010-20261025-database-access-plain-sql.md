# Database Access: Plain SQL with psycopg

Date: 2026-10-25

## Status

Accepted

## Context

The backend stores configurations and spins in PostgreSQL on Neon (decision
0006). The data model consists of two tables, `configurations` and `spins`
(see `docs/architecture.md`). Reel strips and paytable are stored as JSON and
always read and written as a whole. Configurations are immutable (decision
0007), so rows are inserted and read, but rarely updated.

Two questions need an answer before the walking skeleton is built:

 * How does the Python code talk to the database?
 * How is the database schema created and kept up to date?

The project follows the rule to prefer the pragmatic, simpler option.

## Options Considered

 * Option 1: Plain SQL with the PostgreSQL driver `psycopg`. SQL statements
   are written by hand in a small module `app/db.py`. The schema is defined in
   `schema.sql` with `CREATE TABLE IF NOT EXISTS` and executed when the
   application starts. Few concepts, SQL is visible and easy to follow.
   Schema changes after the first version must be done by hand.
 * Option 2: SQLAlchemy (ORM) with Alembic migrations. Tables are defined as
   Python classes, schema changes are versioned as migration scripts. Clean
   and widely used, but introduces two additional tools and their concepts
   (sessions, models, migration workflow).
 * Option 3: SQLAlchemy Core without ORM. Generates SQL from Python
   expressions without object mapping. Sits between options 1 and 2, but
   still adds a library to learn without a clear benefit for two tables.

## Decision

Option 1, plain SQL with `psycopg`, and a `schema.sql` executed at startup.


## Reasons

With two tables and JSON columns, an ORM saves almost no code. Plain SQL keeps
the database access transparent: what is written in the code is exactly what
runs on Neon. This fits the learning focus of the module and the rule to
choose the simpler option. Because `CREATE TABLE IF NOT EXISTS` is idempotent,
running the schema at every start is harmless and removes a manual setup step
on Render.

## Consequences

 * Easier: No ORM or migration tool to learn; SQL statements can be copied
   into the Neon SQL editor for debugging.
 * Easier: A new, empty database (e.g. for local testing) is set up
   automatically on the first start.
 * Harder: Changes to existing tables are not applied by `schema.sql`. They
   must be done by hand (`ALTER TABLE`, e.g. in the Neon SQL editor) and
   noted in the diary.
 * Harder: SQL statements and the mapping of rows to Python dictionaries are
   written by hand.
 * Rule: Values are always passed to queries as parameters (`%s`), never
   inserted into the SQL string, to prevent SQL injection.
 * Follow-up: Add `psycopg[binary]` as dependency; create `src/app/db.py` and
   `src/app/schema.sql`.
