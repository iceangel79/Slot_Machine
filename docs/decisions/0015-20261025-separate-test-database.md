# Separate Test Database (Neon Branch)

Date: 2026-10-25

## Status

Accepted

## Context

The API tests need a PostgreSQL database (decision 0011). In CI they use a
fresh service container. Locally they used `DATABASE_URL` from `.env`, i.e.
the production database on Neon. Decision 0011 noted the risk that tests
writing data (spins) would then write into the production database. With
step 8 such tests are added.

## Options Considered

 * Option 1: A separate Neon branch `test` (free, created with one click). Its
   connection string is stored as `TEST_DATABASE_URL` in `.env`.
 * Option 2: A local PostgreSQL in Docker. Clean, but an additional local
   setup.
 * Option 3: The tests delete the data they created. Error-prone: an aborted
   test run leaves data in the production database.

## Decision

Option 1. The tests use only `TEST_DATABASE_URL`:

 * `tests/conftest.py` reads `TEST_DATABASE_URL` and sets `DATABASE_URL` to it
   before the application is imported.
 * If `TEST_DATABASE_URL` is not set, the API tests are not collected; pytest
   shows this in its header. The tests of the game logic run in any case.
 * In CI, `TEST_DATABASE_URL` points to the service container.

## Reasons

Production and test data are clearly separated, with no additional local
setup. The safeguard in `conftest.py` makes it impossible to run the API tests
against the production database by mistake.

## Consequences

 * Easier: Tests may write freely; production data stays clean.
 * Easier: Locally and in CI the same mechanism is used.
 * Harder: A further connection string must be kept in `.env`.
 * Rule: Tests do not rely on an empty database (spins accumulate in the test
   branch); they check the returned values, not row counts.
 * Note: A Neon branch starts as a copy of its parent branch. It can be reset
   in the Neon console if needed.
 * Resolves the risk noted in decision 0011.
