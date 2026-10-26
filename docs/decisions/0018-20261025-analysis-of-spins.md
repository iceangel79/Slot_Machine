# Analysis of Spins

Date: 2026-10-25

## Status

Accepted

## Context

Step 10 adds the feature "analyse" (requirement F4): for a selected
configuration, the application shows the number of spins, total bet and total
payout, and compares the actual RTP, hit frequency and frequency per winning
rule with the theoretical values. The endpoint
`GET /api/configurations/<id>/analysis` is planned in `docs/architecture.md`.

Questions:

 * The table `spins` stores no winning rule (decision 0012). How are the hits
   per rule counted efficiently, also for a very large number of spins?
 * Should random.org and Python spins be analysed separately (decision 0008)?
 * How does the user see whether a difference between actual and theoretical
   value is still normal random fluctuation?
 * Is a chart needed?

The project follows the rule to prefer the pragmatic, simpler option.

## Options Considered

Counting the hits per rule:

 * Option A1: Load all spins into Python and evaluate each one. Simple, but
   slow and memory-hungry with millions of spins.
 * Option A2: Rebuild the rules in SQL (`CASE WHEN ...`). Fast, but the game
   logic would exist twice and could drift apart.
 * Option A3: The database groups the spins by their three symbols
   (`GROUP BY symbol_1, symbol_2, symbol_3`). Python evaluates every group
   once with `game.evaluate()`. At most 6 x 6 x 6 = 216 groups, independent of
   the number of spins.

Random source:

 * Option B1: Always analyse all spins together.
 * Option B2: Optional filter `?source=random.org` or `?source=python`.

Normal fluctuation:

 * Option C1: Show actual and theoretical values only. The user cannot tell
   whether a difference is normal.
 * Option C2: Show an expected range (95 %) per value: theoretical value
   +/- 1.96 standard errors. Values outside are marked.
 * Option C3: A chi-square test over all rules. Statistically cleaner, but
   harder to explain and needs SciPy or own distribution functions.

Chart:

 * Option D1: No chart; a table with the expected range.
 * Option D2: Bar chart actual vs. theoretical per rule. The values range from
   about 0.01 % to 25 %, so a logarithmic axis would be needed.
 * Option D3: Line chart of the actual RTP over the number of spins
   (convergence), e.g. with Chart.js via CDN.

## Decision

A3, B2, C2 and D1.

Further rules:

 * The calculation is a plain function `game.analyse(config, rows)` without
   database; `db.spins_grouped_by_symbols()` delivers the rows.
 * Total bet and total payout are the sums stored in the database
   (`SUM(bet)`, `SUM(payout)`).
 * Standard error of the hit frequency and of each rule:
   `sqrt(p * (1 - p) / n)`.
 * Standard error of the RTP: `sigma / sqrt(n)`. The standard deviation
   `sigma` of the payout per spin is calculated exactly from the theoretical
   rule probabilities: `sigma^2 = sum(p * payout^2) - RTP^2`.
 * The range is limited to 0 and, for frequencies, to 100 %.
 * Without spins, actual values and ranges are `null`.
 * New index `spins_configuration_id_idx` on `spins (configuration_id)`.

## Reasons

A3 keeps the work of Python constant and lets the database do the counting.
It follows the same principle as the theoretical calculation (decision 0012,
option C2): theory and analysis use the same evaluation function, so they
cannot drift apart. B2 is the follow-up promised in decision 0008 and costs
one condition in the query. C2 answers the question "is this still normal?"
with one number per line that is easy to explain. For the default
configuration (sigma about 3.5) the RTP range is 91 % +/- 21.7 % after 1,000
spins and +/- 0.7 % after 1,000,000 spins, which shows clearly how much the
jackpot makes the RTP fluctuate. D1: the table answers requirement F4
completely; a chart is not required.

## Consequences

 * Easier: The analysis stays fast with any number of spins (50,000 spins
   in about 20 ms locally); the calculation is unit tested without database.
 * Easier: A spin manipulated in the database or a faulty random source
   shows up as a value outside the expected range.
 * Harder: With 95 %, about 1 in 20 values lies outside the range by chance,
   even with correct random numbers. The page explains this.
 * Harder: The range uses the normal approximation. With few spins or rare
   rules (e.g. three sevens, about 1 in 8,000) it is only a rough guide.
 * Note: PostgreSQL does not create an index for a foreign key
   automatically. `CREATE INDEX IF NOT EXISTS` in `schema.sql` adds it to
   existing databases at the next start (decision 0010).
 * Option D3 (RTP convergence chart) was considered again in step 11 and
   left out: the table with the expected range shows the same effect, and the
   chart would add a JavaScript library and a new query.
