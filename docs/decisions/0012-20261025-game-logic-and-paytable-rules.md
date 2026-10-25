# Game Logic: Data Structures and Paytable Rules

Date: 2026-10-25

## Status

Accepted

## Context

The game logic is a plain Python module without Flask and without a database
(`app/game.py`, see `docs/architecture.md`). It draws stop positions, evaluates
the paytable and calculates the theoretical probabilities, hit frequency and
RTP. Before implementing it, the following questions need an answer:

 * In which form does the code work with a configuration?
 * What exactly does the rule type "cherry count" mean?
 * What happens if several rules match the same result?
 * How is the random source passed into the game logic (decision 0008)?
 * How are the theoretical values calculated?
 * How can the game logic be tested without a database?

The project follows the rule to prefer the pragmatic, simpler option.

## Options Considered

Data structure:

 * Option A1: Plain dicts and lists, exactly as stored as JSON in the
   database (decision 0010). No conversion needed.
 * Option A2: Python classes (dataclasses) for configuration and rules. More
   explicit, but needs conversion from and to JSON.

Overlapping rules (e.g. three cherries match "three of a kind CHERRY" and
"cherry count 3"):

 * Option B1: Only the matching rule with the highest payout pays.
 * Option B2: The payouts of all matching rules are added up. Makes the
   analysis per rule harder, because one spin counts for several rules.

Theoretical values:

 * Option C1: Formulas per rule type. Must be written and kept consistent
   with the evaluation for every rule type.
 * Option C2: Evaluate every possible symbol combination with the same
   function that is used when playing, weighted by how often the symbols
   appear on each reel.

Testing without a database: `src/app/__init__.py` creates the tables when the
package is imported, so importing `app.game` would need a database.

 * Option D1: Move the Flask application into `app/main.py` and keep the
   package `app` free of side effects.
 * Option D2: Place the game logic outside the package `app`. Contradicts the
   architecture.
 * Option D3: Create the tables at the first request instead of at start-up.
   Database problems would no longer be visible right at start-up.

## Decision

 * A1: A configuration is a plain dict with `reel_strips` (three lists of
   symbol codes) and `paytable` (list of rules). Rules:
   `{"type": "three_of_a_kind", "symbol": "SEVEN", "payout": 100}` and
   `{"type": "cherry_count", "count": 1, "payout": 2}`.
 * "Cherry count" means exactly `count` cherries on the payline, at any
   position.
 * B1: Only the matching rule with the highest payout pays; on a tie the first
   one in the paytable.
 * The random source is a function that takes the lengths of the reel strips
   and returns one stop position per reel. Tests pass a fixed function.
 * C2: Theoretical values by evaluating all symbol combinations (at most
   6 x 6 x 6 = 216).
 * D1: The Flask application moves to `app/main.py`; Gunicorn starts
   `app.main:app`. This changes the follow-up of decision 0004.
 * The bet is fixed at 1 credit; the payout is the multiplier of the rule.

## Reasons

Plain dicts need no conversion between database, API and game logic. With B1
each spin belongs to at most one rule, so the analysis "actual vs. theoretical
frequency per rule" can count each spin once. Because C2 uses the same
evaluation function as playing, theory and practice cannot drift apart when a
rule type is added or changed. D1 is a small change and lets the game logic
tests run without a database, locally and in the CI.

## Consequences

 * Easier: Unit tests of the game logic need no database and no network.
 * Easier: The winning rule of a stored spin can always be recalculated from
   its three symbols, so the `spins` table needs no additional column.
 * Harder: Plain dicts are not checked by Python itself. A function
   `validate_config()` checks a configuration before it is saved.
 * Harder: Adding the rule type "any bar" later means changing
   `rule_matches()` and `validate_config()`; the theoretical calculation stays
   unchanged.
 * Follow-up: random.org and the fallback to Python are added to `app/rng.py`
   in step 8 with the same function signature.
