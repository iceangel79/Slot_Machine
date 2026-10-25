"""Game logic of the slot machine (decision 0012).

Plain Python, no Flask and no database. A configuration is a plain dict, in
exactly the form in which it is stored as JSON in the database:

    {
        "reel_strips": [
            ["CHERRY", "BLANK", "BAR", ...],   # reel 1
            [...],                             # reel 2
            [...],                             # reel 3
        ],
        "paytable": [
            {"type": "three_of_a_kind", "symbol": "SEVEN", "payout": 100},
            {"type": "cherry_count", "count": 2, "payout": 5},
            {"type": "cherry_count", "count": 1, "payout": 2},
        ],
    }

Rules of the game:

 * The bet is 1 credit per spin; the payout is the multiplier of the rule.
 * "three_of_a_kind" pays if all three symbols on the payline are `symbol`.
 * "cherry_count" pays if exactly `count` cherries are on the payline, at any
   position.
 * If several rules match, only the one with the highest payout pays (on a
   tie, the first one in the paytable).
"""

from collections import Counter
from itertools import product

SYMBOLS = ("CHERRY", "LEMON", "BELL", "BAR", "SEVEN", "BLANK")
REEL_COUNT = 3
BET = 1


def validate_config(config):
    """Check a configuration. Raises ValueError with a readable message."""
    if not isinstance(config, dict):
        raise ValueError("configuration must be an object")

    strips = config.get("reel_strips")
    if not isinstance(strips, list) or len(strips) != REEL_COUNT:
        raise ValueError(f"reel_strips must be a list of {REEL_COUNT} reels")
    for number, strip in enumerate(strips, start=1):
        if not isinstance(strip, list) or not strip:
            raise ValueError(f"reel {number} must be a non-empty list of symbols")
        for symbol in strip:
            if symbol not in SYMBOLS:
                raise ValueError(f"reel {number}: unknown symbol {symbol!r}")

    paytable = config.get("paytable")
    if not isinstance(paytable, list):
        raise ValueError("paytable must be a list of rules")
    for number, rule in enumerate(paytable, start=1):
        _validate_rule(number, rule)


def _validate_rule(number, rule):
    if not isinstance(rule, dict):
        raise ValueError(f"rule {number} must be an object")

    payout = rule.get("payout")
    # bool is a subclass of int in Python, so True would pass as 1.
    if not isinstance(payout, int) or isinstance(payout, bool) or payout < 1:
        raise ValueError(f"rule {number}: payout must be a positive integer")

    rule_type = rule.get("type")
    if rule_type == "three_of_a_kind":
        if rule.get("symbol") not in SYMBOLS:
            raise ValueError(f"rule {number}: unknown symbol {rule.get('symbol')!r}")
    elif rule_type == "cherry_count":
        if rule.get("count") not in (1, 2, 3):
            raise ValueError(f"rule {number}: count must be 1, 2 or 3")
    else:
        raise ValueError(f"rule {number}: unknown rule type {rule_type!r}")


def rule_matches(rule, symbols):
    """Return True if one rule matches the three symbols on the payline."""
    if rule["type"] == "three_of_a_kind":
        return all(symbol == rule["symbol"] for symbol in symbols)
    if rule["type"] == "cherry_count":
        return symbols.count("CHERRY") == rule["count"]
    raise ValueError(f"unknown rule type {rule['type']!r}")


def evaluate(symbols, paytable):
    """Evaluate the three symbols on the payline against the paytable.

    Returns (rule_index, payout). rule_index is the position of the winning
    rule in the paytable, or None if nothing pays (payout 0).
    """
    winner = None
    for index, rule in enumerate(paytable):
        if rule_matches(rule, symbols):
            if winner is None or rule["payout"] > paytable[winner]["payout"]:
                winner = index
    if winner is None:
        return None, 0
    return winner, paytable[winner]["payout"] * BET


def spin(config, stop_positions):
    """Execute one spin.

    stop_positions is the random source (decision 0008): a function that takes
    the lengths of the reel strips and returns one stop position per reel,
    e.g. rng.python_stop_positions. Tests pass a fixed function instead.
    """
    strips = config["reel_strips"]
    stops = stop_positions([len(strip) for strip in strips])
    if len(stops) != len(strips):
        raise ValueError("random source must return one stop position per reel")
    for stop, strip in zip(stops, strips, strict=True):
        if not 0 <= stop < len(strip):
            raise ValueError(f"stop position {stop} is outside the reel strip")

    symbols = [strip[stop] for stop, strip in zip(stops, strips, strict=True)]
    rule_index, payout = evaluate(symbols, config["paytable"])
    return {
        "stops": stops,
        "symbols": symbols,
        "rule_index": rule_index,
        "bet": BET,
        "payout": payout,
    }


def theoretical_stats(config):
    """Calculate the exact probabilities, hit frequency and RTP.

    Instead of formulas, all symbol combinations are evaluated with the same
    function that is used when playing (evaluate). Each combination is
    weighted by how often its symbols appear on the reels. With six symbols
    these are at most 6 x 6 x 6 = 216 combinations, independent of the length
    of the reel strips.
    """
    strips = config["reel_strips"]
    paytable = config["paytable"]
    counts = [Counter(strip) for strip in strips]
    total = 1
    for strip in strips:
        total *= len(strip)

    rule_probabilities = [0.0] * len(paytable)
    for combination in product(*(reel.items() for reel in counts)):
        symbols = [symbol for symbol, _ in combination]
        weight = 1
        for _, count in combination:
            weight *= count
        rule_index, _ = evaluate(symbols, paytable)
        if rule_index is not None:
            rule_probabilities[rule_index] += weight / total

    rules = [
        {
            "rule": rule,
            "probability": probability,
            "rtp_contribution": probability * rule["payout"],
        }
        for rule, probability in zip(paytable, rule_probabilities, strict=True)
    ]
    return {
        "rules": rules,
        "hit_frequency": sum(rule_probabilities),
        "rtp": sum(rule["rtp_contribution"] for rule in rules) / BET,
    }
