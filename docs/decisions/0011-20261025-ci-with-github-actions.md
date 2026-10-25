# Continuous Integration with GitHub Actions

Date: 2026-10-25

## Status

Accepted

## Context

The assignment requires that the software is checked automatically with every
commit, for example with tests and linters. Deployment to Render already
happens automatically on every push (decision 0001), but nothing checks the
code before or alongside it.

The project uses `ruff` as linter and `pytest` for tests (both already defined
in `pyproject.toml`). The first test checks the endpoint `/api/health`. When
the application is imported, it creates the database tables
(`db.init_schema()`, decision 0010), so tests of the HTTP endpoints need a
reachable PostgreSQL database.

## Options Considered

 * Option 1: GitHub Actions with a PostgreSQL service container. GitHub starts
   a fresh, empty PostgreSQL database for every pipeline run. No code changes
   needed; the tests check the real database access including schema
   creation.
 * Option 2: GitHub Actions without a database; the database functions are
   replaced by stand-ins in the tests (mocking). Requires moving
   `init_schema()` out of the module import and introduces mocking as an
   additional concept. The tests check less of the real behaviour.
 * Option 3: Another CI service (e.g. GitLab CI, CircleCI). Would add a
   further platform, although the code is already hosted on GitHub.

## Decision

Option 1, GitHub Actions with a PostgreSQL service container. The pipeline runs
on every push and pull request and executes two checks: `ruff check src tests`
and `pytest`.

## Reasons

GitHub Actions is built into the platform that already hosts the repository
and is the tool covered in the module. The service container keeps the
application code unchanged and lets the tests run against a real PostgreSQL,
the same database system as in production. Tests of the game logic (pure
Python, no database) run in the same pipeline without any extra setup.

## Consequences

 * Easier: Every push shows a green check or a red cross on GitHub; problems
   are noticed before they are discussed in a review or presentation.
 * Easier: Tests run against the same database system as production.
 * Harder: Running the endpoint tests locally needs a database. Locally they
   use `DATABASE_URL` from `.env`, i.e. the Neon database. This is harmless
   for the health check, which only reads.
 * Risk: Later tests that write data (e.g. spins) would write into the Neon
   database when run locally. This must be addressed before such tests are
   added, e.g. with a separate Neon branch or a local test database.
 * Note: Render deploys independently of the pipeline result. A failing
   pipeline does not stop a deployment.
 * Follow-up: Workflow in `.github/workflows/ci.yml`, first tests in
   `tests/test_api.py`.
