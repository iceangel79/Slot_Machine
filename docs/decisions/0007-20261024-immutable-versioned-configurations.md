# Immutable, Versioned Configurations

Date: 2026-10-24

## Status

Accepted

## Context

Spins must be analysed against the configuration (reel strips and paytable)
they were played with. Configurations can be changed by the user, and mass
simulations can produce a very large number of spins.

## Options Considered

 * Option 1: Store the complete configuration in every spin row. Simple to
   query, but the identical configuration is stored for every spin
   (e.g. 100,000 times per mass simulation).
 * Option 2: Separate `configurations` table; each spin references its
   configuration via `configuration_id`. Saved configurations are never
   modified; a change creates a new configuration.
 * Option 3: Separate table with editable configurations. Small, but old spins
   would then be analysed against a configuration they were not played with.

## Decision

Option 2, a normalised `configurations` table with immutable entries.

## Reasons

Each spin stays unambiguously linked to the configuration it was played with,
without storing redundant data. The analysis per configuration becomes a
simple query.

## Consequences

 * Easier: Correct analysis per configuration; small spin rows.
 * Harder: The configuration view must "save as new" instead of editing.
 * Follow-up: Data model with the tables `configurations` and `spins`.
