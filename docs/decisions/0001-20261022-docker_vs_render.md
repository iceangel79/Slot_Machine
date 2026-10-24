# Decision Docker vs Render.com

Date: 2026-10-22

## Status

Accepted

## Context

Decision needs to be made, wheter to use docker and/or render.com to host the application.

## Options Considered

 * Option 1: Docker and Render.com or any other service for that matter.
 * Option 2: Only render.com or any other service for that matter.
 * Option 3: Only docker (locally hosted).

## Decision

Use docker together with render.com, since the dockerfile is already provided with the template and can be used without modifications.

## Reasons

The advantage of Docker to run the same version of the application on different environments is useful in case you want to use Docker Desktop locally to test the application. Render.com is a Platform as a Service (PaaS) which simplifies the deployment process. It also provides a free tier which is sufficient for our needs. Furthermore, Render.com is a modern platform which is easy to use and provides a good developer experience.

## Consequences

In case the software would be further developed it is already containerized and can be deployed on other services too.
However, the dockerfile provided with the template needs to be adapted to the needs of the application.
