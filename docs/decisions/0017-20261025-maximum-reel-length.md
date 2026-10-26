# Maximum Reel Length: 30 Positions

Date: 2026-10-25

## Status

Accepted

## Context

The configuration editor lets the user choose how many positions each reel has
(decision 0016). `validate_config()` only required at least one position per
reel; there was no upper limit. The application simulates a classic
three-reel Las Vegas slot machine with physical reels; virtual reel mapping is
out of scope (`docs/requirements.md`).

The length of a reel does not make the configuration or the calculation
slower: the editor asks for the number of positions per symbol, and the
theoretical values evaluate at most 6 x 6 x 6 = 216 symbol combinations,
independent of the reel length. The limit is therefore about realism and
protection against nonsensical input, not about performance.

## Options Considered

 * Option 1: No upper limit. Allows unrealistic configurations and very large
   requests.
 * Option 2: 22 positions, exactly like the classic mechanical machines.
   Historically accurate, but leaves no room for experiments.
 * Option 3: 30 positions. Covers the classic machines with some room for
   experiments.
 * Option 4: 100 or more positions, similar to modern virtual reels. Not a
   classic machine any more.

## Decision

Option 3. A reel has 1 to 30 positions (`game.MAX_STRIP_LENGTH`).

## Reasons

Mechanical slot machines were limited by the size of their physical reels.
The first machines around 1900 (e.g. the "Liberty Bell") had about 10 symbols
per reel. Later, reels with 20 stops became common, and many machines from the
1960s onwards used 22 stops per reel (22 x 22 x 22 = 10,648 combinations).
Larger reels did not fit into the cabinet. Only virtual reels, introduced in
the 1980s, allowed modern machines to use 64, 256 or more virtual positions,
which is out of scope for this project.

30 positions cover the classic 20 to 22 stops and leave room for experiments:
a longer reel allows finer probabilities, e.g. one seven out of 30 positions
makes the jackpot rarer than one out of 20.

## Consequences

 * Easier: Configurations stay within the range of real classic machines.
 * Easier: The limit is enforced in one place (`validate_config()`); the
   editor shows the validation message and the number of positions per reel.
 * Harder: The limit is also written in the frontend (`configure.html`) to
   show "x / 30"; both values must be changed together.
 * Note: The default configuration (decision 0013) uses 20 positions per reel.
