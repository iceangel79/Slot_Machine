# Requirements

Date: 2026-10-24

This document describes the scope of the Slot Machine Simulator (MVP). It was
worked out in a requirements session supported by an AI assistant (Claude,
Anthropic); see `docs/diary.md` (2026-10-24).

## Goal

A web application that simulates a classic three-reel Las Vegas slot machine.
The machine is freely configurable, every spin is stored in a database, and an
analysis view compares the configured (theoretical) probabilities and payout
ratio with the results actually achieved.

## Domain concepts

 * **Symbol:** A reel symbol identified by a code, e.g. `CHERRY`, `LEMON`,
   `BELL`, `BAR`, `SEVEN`, `BLANK`. Blanks are real symbols on the strip.
 * **Reel strip:** The fixed, ordered sequence of symbols on one reel. The
   number of occurrences of a symbol determines its probability.
 * **Spin:** For each of the three reels a random stop position is drawn. The
   three symbols on the payline form the result.
 * **Payline:** One payline (the middle row).
 * **Paytable:** Rules that define which results pay and how much (as a
   multiple of the bet).
 * **RTP (Return to Player):** Expected payout per unit bet, calculated as the
   sum of probability times payout over all winning results.
 * **Hit frequency:** Share of spins that pay anything.

## Functional requirements

### F1 Play (spin)

 * The user starts a single spin; the three resulting symbols are shown.
 * The result is evaluated against the paytable and the payout is shown.
 * Each spin is stored in the database.
 * Single manual spins draw their random numbers from the external web
   service random.org. If random.org is not reachable, the backend falls back
   to Python's random number generator. The source used is stored per spin.

### F2 Autospin and mass simulation

 * **Autospin:** A number of spins executed one after another with a visible
   delay, so the user can watch.
 * **Mass simulation:** A large number of spins executed at once in the
   backend, without animation.
 * Both use Python's random number generator (no random.org quota issues).

### F3 Configure

 * A configuration consists of three reel strips and a paytable.
 * Supported paytable rule types (MVP):
    * (a) three of a kind, e.g. `SEVEN SEVEN SEVEN` pays 100x
    * (c) cherry count, e.g. one cherry anywhere pays 2x, two cherries 5x
 * The theoretical probabilities, hit frequency and RTP are calculated and
   shown while editing, before saving.
 * Saved configurations are immutable. Changing a configuration creates a new
   configuration (new version). This guarantees that every spin can be
   analysed against the configuration it was played with.

### F4 Analyse

 * The user selects a configuration and sees, for its stored spins:
    * number of spins, total bet, total payout
    * actual vs. theoretical RTP
    * actual vs. theoretical hit frequency
    * actual vs. theoretical frequency per winning rule

## Data (first draft)

 * `configurations`: id, name, created_at, reel strips, paytable
 * `spins`: id, configuration_id, created_at, symbols (3 codes), bet, payout,
   rng_source (`random.org` or `python`)

## Out of scope (MVP)

 * Player accounts, login, credit balance
 * More than three reels or more than one payline
 * Paytable rule type "any bar" and other mixed combinations
 * Virtual reel mapping (weighted stop tables) as used in modern machines

## Non-functional requirements

 * Simplicity first: the pragmatic, simpler option is preferred throughout.
 * The backend stores and returns symbol codes only. The frontend decides how
   they are displayed (MVP: emoji; blanks are shown explicitly). Any other
   frontend could be connected to the same backend.
 * The application is publicly reachable until the end of the exam session
   and deployed automatically.
 * The game logic is a plain Python module, independent of the web framework,
   and covered by unit tests.
