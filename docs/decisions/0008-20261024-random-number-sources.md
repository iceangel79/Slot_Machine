# Random Number Sources: random.org and Python

Date: 2026-10-24

## Status

Accepted

## Context

The required architecture contains an external web service. A slot machine
needs random numbers. random.org provides true random numbers based on
atmospheric noise, but has a daily quota. Python's `secrets` module uses the
operating system's cryptographically secure generator, which is sufficient
for a slot machine (real casinos also use certified software generators).

## Options Considered

 * Option 1: Python only. Simplest, but no external web service.
 * Option 2: random.org for all spins. Would exhaust the quota during
   autospin and mass simulation.
 * Option 3: random.org only delivers a seed per simulation run. Reproducible,
   but adds the concept of seeds.
 * Option 4: random.org for single manual spins; Python for autospin and mass
   simulation; Python as fallback if random.org is not reachable.

## Decision

Option 4. 

## Reasons

It is the simplest option that includes an external web service. It also adds
a twist to the application: when playing manually, the result is determined by
atmospheric noise. Autospin and mass simulation do not depend on the quota.

## Consequences

 * Easier: No quota problems for simulations.
 * Harder: The backend must handle failures and timeouts of random.org.
 * Follow-up: The source used is stored per spin (`rng_source`), so the
   analysis can distinguish between random.org and Python spins.
 * Testing: The random number source is passed into the game logic, so unit
   tests can use a fixed, predictable source.
