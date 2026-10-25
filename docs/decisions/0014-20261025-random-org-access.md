# Access to random.org: One Request per Reel

Date: 2026-10-25

## Status

Accepted

## Context

Manual spins draw their stop positions from random.org, with Python as
fallback (decision 0008). The random source is a function that takes the
lengths of the reel strips and returns one stop position per reel (decision
0012). The reels of a configuration may have different lengths.

The HTTP interface of random.org (`/integers/`) needs no API key. random.org
asks clients to send a User-Agent with a contact e-mail address. The daily
quota applies per IP address; on Render several services share outgoing IP
addresses, so the quota may be exhausted without our own fault. One request
returns any number of integers, but all within the same range `min..max`.

Questions:

 * How are stop positions for reels of different lengths requested?
 * Which HTTP client is used?
 * What happens if random.org fails?
 * How is this tested without calling random.org?

## Options Considered

Requesting the numbers:

 * Option A1: One request per reel, each with `min=0` and `max=length - 1`.
   Every number lies exactly within the range of its reel; no conversion.
   Three times the latency and three points of failure per spin.
 * Option A2: One request for three numbers between 0 and 999,999,999, then
   `number % length`. One request, but introduces a (negligible) modulo bias
   that must be explained.

HTTP client:

 * Option B1: `urllib.request` from the standard library. No additional
   dependency.
 * Option B2: The library `requests`. More readable, but an additional
   dependency.

## Decision

 * A1: One request per reel.
 * B1: `urllib.request` with a timeout of 3 seconds per request and a
   User-Agent containing a contact address.
 * If any of the three requests fails (network error, timeout, HTTP error
   such as an exhausted quota, unexpected answer), all three stop positions
   are drawn with Python. A spin never mixes sources. The failure is logged.
 * `rng.manual_stop_positions()` returns the stop positions and the source
   used (`random.org` or `python`), which is stored per spin.

## Reasons

A1 is the most direct way to use random.org: each reel gets its own number in
exactly its own range, without any conversion or bias. The additional latency
is acceptable for a single manual spin. B1 avoids a dependency for a few lines
of code. Falling back for the whole spin keeps `rng_source` unambiguous.

## Consequences

 * Easier: No API key to manage; no conversion of the random numbers.
 * Harder: A manual spin takes up to three round trips to random.org; in the
   worst case (timeouts) up to 9 seconds before the fallback is used.
 * Testing: Unit and API tests never call random.org. The parsing of the
   answer is a pure function and tested directly; the fallback is tested by
   replacing `rng.random_org_stop_positions` with `monkeypatch`.
 * Risk: The quota per IP address on Render. The fallback keeps the game
   playable; `rng_source` shows how often it was used.
