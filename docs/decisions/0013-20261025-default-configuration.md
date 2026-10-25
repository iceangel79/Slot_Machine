# Default Configuration Stored at Startup

Date: 2026-10-25

## Status

Accepted

## Context

Every spin references a configuration (decision 0007). Step 8 (feature "play")
is implemented before step 9 (configuration GUI and endpoints), so there is no
way yet to create a configuration through the application. A configuration is
nevertheless needed to play, and new, empty databases (CI service container,
Neon test branch, decision 0015) must work without manual setup.

## Options Considered

 * Option 1: Insert a configuration by hand in the Neon SQL editor. Fast, but
   not versioned in the repository; the CI and test databases stay empty.
 * Option 2: `INSERT ... WHERE NOT EXISTS` in `schema.sql`. Idempotent, but
   the JSON of reel strips and paytable is hard to read inside SQL and is not
   checked by `validate_config()`.
 * Option 3: A default configuration as Python dict `DEFAULT_CONFIG` in
   `app/game.py`. At startup it is inserted if the table `configurations` is
   empty. Readable, versioned and covered by unit tests.
 * Option 4: Build `POST /api/configurations` already in step 8 and fill the
   database with curl. Anticipates step 9.

## Decision

Option 3. The default configuration "Classic (default)" has three identical
reels with 20 positions each (2 cherries, 3 lemons, 4 bells, 2 bars, 1 seven,
8 blanks) and pays: three sevens 200, three bars 50, three bells 20, three
cherries 20, three lemons 10, two cherries 5, one cherry 2. Theoretical RTP
91.0 %, hit frequency 28.4 %.

## Reasons

Every database, including the test and CI databases, has a valid configuration
right after the first start. The configuration lives in the code, so it is
reviewed, versioned and tested like any other code. The values are realistic
for a classic slot machine (the house keeps about 9 %). Because the default
configuration is only inserted into an empty table, it also serves as a
fallback: the application can always be played.

## Consequences

 * Easier: No manual setup step on Render, in CI or for the test database.
 * Easier: A unit test checks that the default configuration is valid and
   that its theoretical RTP stays at the expected value.
 * Harder: Changing `DEFAULT_CONFIG` later has no effect on a database that
   already contains configurations. Changes are made through the
   configuration GUI (step 9), which creates a new configuration (decision
   0007).
 * Follow-up: `GET /api/configurations` and `GET /api/configurations/<id>`
   are added in step 8, so the game GUI can choose a configuration.
