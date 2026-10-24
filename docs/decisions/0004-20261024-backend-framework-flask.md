# Backend Framework: Flask

Date: 2026-10-24

## Status

Accepted

## Context

The backend must be written in Python with Flask, Django or FastAPI. It serves
the static frontend files, provides a JSON API for the three views (play,
configure, analyse) and talks to the database and to random.org. The project
follows the rule to prefer the pragmatic, simpler option. Decision 0002 is
detailed by this record.

## Options Considered

 * Option 1: Flask. Minimal, easy to understand, already prepared in the
   project template and in the course material.
 * Option 2: FastAPI. Strong for pure JSON APIs (automatic validation and API
   documentation), but introduces additional concepts (async, Pydantic models).
 * Option 3: Django. Full-stack framework with ORM and admin, far more than the
   scope of this project needs.

## Decision

Option 1, Flask, served by Gunicorn. Decided by Adrian.

## Reasons

Flask covers everything the application needs with the fewest concepts. The
template and the lecturers' material support it directly, which reduces setup
problems and leaves more time for the actual slot machine logic.

## Consequences

 * Easier: Small codebase, quick start, many examples available.
 * Harder: Input validation and API documentation must be done by hand.
 * Follow-up: `src/app/__init__.py` exposes a Flask object named `app`; the
   `Dockerfile` start command is changed from `app.hello:app` to `app:app`.
