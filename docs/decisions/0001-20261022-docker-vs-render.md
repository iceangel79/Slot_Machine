# Docker and Render.com for Hosting

Date: 2026-10-22

## Status

Accepted

## Context

The application must be reachable under a public URL until the end of the
exam session and must be deployed automatically. The decision is whether to
use Docker, a hosting platform such as Render.com, or both. The course
template already contains a `Dockerfile`.

## Options Considered

 * Option 1: Docker together with a hosting platform (Render.com). The same
   image runs locally and in production.
 * Option 2: Render.com without Docker (native Python runtime). One tool less,
   but local and production environments may differ.
 * Option 3: Docker only, hosted on an own machine. No public URL without
   additional effort.

## Decision

Option 1: Render.com builds and runs the `Dockerfile` from the repository and
deploys automatically on every push.

## Reasons

Docker runs the same version of the application in every environment and can
be tested locally with Docker Desktop. Render.com is a Platform as a Service
(PaaS) that simplifies deployment, connects directly to the GitHub repository
and offers a free tier that is sufficient for this project.

## Consequences

 * Easier: Automatic deployment on every push; the application is already
   containerised and could be moved to another platform.
 * Harder: The `Dockerfile` of the template had to be adapted to the
   application (start command, later `app.main:app`, decision 0012).
 * Risk: The free tier sleeps without traffic; the first request then takes
   about a minute.
