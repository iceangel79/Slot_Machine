# Symbol Codes in the Backend, Emoji Display in the Frontend

Date: 2026-10-24

## Status

Accepted

## Context

The slot machine shows classic Las Vegas symbols, including blanks. The
symbols must be stored in the database and displayed in the frontend.

## Options Considered

 * Option 1: Store and transfer the emoji themselves. Simple, but couples the
   data to one way of displaying it.
 * Option 2: Backend and database use symbol codes only (`CHERRY`, `LEMON`,
   `BELL`, `BAR`, `SEVEN`, `BLANK`); the frontend maps codes to a display.

## Decision

Option 2. The MVP frontend displays the codes as emoji; blanks are displayed
explicitly.

## Reasons

The backend stays independent of the presentation. Any frontend, from simple
emoji up to an elaborate game client (e.g. built with Godot), can use the same
API and data.

## Consequences

 * Easier: Changing the look never touches stored data.
 * Harder: The frontend needs a mapping table from code to display.
