# Decision Docker vs Render.com

Date: 22.10.2026

## Status

Accepted

## Context

Decision needs to be made, wheter to use docker and/or render.com to host the application.

## Options Considered

 * Option 1: Docker and Render.com or any other service for that matter.
 * Option 2: Only render.com or any other service for that matter.
 * Option 3: Only docker (locally hosted).

## Decision

Use Render.com as per proposal from face2face lesson. Since we are not planing on deploying to various services, docker would only increase complexity.

## Reasons

The advantage of Docker to run the same version of the application on different environments is not relevant for us. Render.com is a Platform as a Service (PaaS) which simplifies the deployment process. It also provides a free tier which is sufficient for our needs. Furthermore, Render.com is a modern platform which is easy to use and provides a good developer experience.

## Consequences

Complexity reduced.
In case the software would be further developed it could be containerized at that time. So it could be deployed on other services too. 