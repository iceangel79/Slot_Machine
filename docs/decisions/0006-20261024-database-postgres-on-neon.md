# Database: PostgreSQL hosted on Neon

Date: 2026-10-24

## Status

Accepted

## Context

All spins and configurations must be stored persistently. The application must
stay available until the end of the exam session (December 2026). The backend
runs on the Render free tier, whose file system is lost on every deploy or
restart. Free PostgreSQL databases on Render expire after 30 days.

## Options Considered

 * Option 1: SQLite file inside the application. Simplest, but data is lost on
   Render with every deploy or restart.
 * Option 2: PostgreSQL on Render (free). Close to the app, but expires after
   30 days, i.e. before the end of the exam session.
 * Option 3: PostgreSQL on Neon (free tier). Managed PostgreSQL that does not
   expire; connected via a connection string.
 * Option 4: Azure SQL. Recommended in the course, but requires a separate
   Azure setup.

## Decision

Option 3, PostgreSQL hosted on Neon. 

## Reasons

PostgreSQL is one of the databases recommended in the course. Neon removes the
expiry problem without adding an extra platform for the backend. The Python
backend connects to the database directly; Render only provides the connection
string as an environment variable.

## Consequences

 * Easier: Persistent data independent of Render deploys.
 * Harder: A second external provider must be managed.
 * Security: The connection string contains a password. It is stored as
   `DATABASE_URL` in a local `.env` file (not versioned) and as an environment
   variable on Render, never in the code.
 * Risk: A free database may pause when idle, so the first request after a
   pause can be slower.
