# Configuration Editor

Date: 2026-10-25

## Status

Accepted

## Context

Step 9 adds the feature "configure" (requirement F3): a configuration consists
of three reel strips and a paytable, the theoretical probabilities, hit
frequency and RTP are shown while editing, and saved configurations are
immutable (decision 0007). Validation and theoretical values already exist in
the game logic (`validate_config()`, `theoretical_stats()`, decision 0012).

Questions:

 * How does the user edit the reel strips?
 * How is a new configuration created?
 * How are the theoretical values calculated while editing?
 * How are the pages of the frontend organised?

The project follows the rule to prefer the pragmatic, simpler option.

## Options Considered

Editing the reel strips:

 * Option A1: The number of positions per symbol and reel, entered in a grid
   (6 symbols x 3 reels). The frontend builds the strips from the numbers.
 * Option A2: An ordered list per reel (add, remove, move symbols). Realistic,
   but much more frontend code and tedious to use.
 * Option A3: One text field per reel with comma-separated codes. Easy to
   build, but error-prone to use.

Creating a configuration:

 * Option B1: The editor always starts as a copy of an existing configuration
   and saves the result as a new configuration.
 * Option B2: Additionally an empty editor. Not needed, because there is
   always at least the default configuration (decision 0013).

Theoretical values while editing:

 * Option C1: After every change, and a short pause of 300 ms (debounce), the
   frontend calls `POST /api/configurations/evaluate`.
 * Option C2: A button "Calculate". Simpler, but does not fully meet "shown
   while editing".
 * Option C3: Calculation in JavaScript. Duplicates the game logic and
   contradicts decision 0012 (theory and play use the same function).

Pages:

 * Option D1: One HTML page per feature (`index.html` play,
   `configure.html`, later `analyse.html`) with a small navigation. The emoji
   table moves to `static/common.js`, the styles to `static/style.css`.
 * Option D2: One page with tabs (`v-if`). One file, but it quickly becomes
   hard to read.

## Decision

A1, B1, C1 and D1.

Further rules:

 * A reel has 1 to 30 positions (decision 0017).
 * A name is required (1 to 100 characters, leading and trailing spaces are
   removed).
 * A configuration with an RTP above 100 % can be saved; the editor shows a
   warning.
 * The rules stay in the order they were entered; on equal payout the first
   rule wins (decision 0012). Rules cannot be moved.
 * Configurations cannot be deleted, because spins refer to them.

## Reasons

With one payline and equally likely stop positions, the order of the symbols
on a reel does not change any probability; only the number of positions per
symbol counts. The order would only matter for the symbols visible above and
below the payline, which are not shown. A1 therefore loses nothing and is the
easiest to build and to use. B1 fits immutable configurations naturally. C1
keeps all calculations in the backend, so theory and play cannot drift apart.
D1 keeps every page small and understandable on its own.

## Consequences

 * Easier: The editor needs no drag and drop; the backend and the database
   stay unchanged (strips are still stored as lists).
 * Easier: The live calculation reuses `validate_config()` and
   `theoretical_stats()`; error messages of the validation are shown directly
   in the editor.
 * Harder: Strips saved by the editor are grouped by symbol (e.g. all
   cherries first). This has no effect on the game, but looks less like a real
   reel.
 * Harder: Every change in the editor triggers a request to the backend.
 * Follow-up: `POST /api/configurations` and
   `POST /api/configurations/evaluate`; `static/common.js` and
   `static/style.css` shared by all pages.
