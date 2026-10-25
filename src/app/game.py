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

import math
from collections import Counter
from itertools import product

from collections import Counter
from itertools import product

SYMBOLS = ("CHERRY", "LEMON", "BELL", "BAR", "SEVEN", "BLANK")
REEL_COUNT = 3
BET = 1
# Classic mechanical slot machines had 20 to 22 stops per reel (decision 0017).
MAX_STRIP_LENGTH = 30

# z value of the 95 % expected range in the analysis (decision 0018).
Z_95 = 1.96

# Default configuration (decision 0013). It is stored when the database has no
# configuration yet. Each reel has 20 positions: 2 cherries, 3 lemons, 4 bells,
# 2 bars, 1 seven and 8 blanks. Theoretical RTP 91.0 %, hit frequency 28.4 %.
DEFAULT_CONFIG_NAME = "Classic (default)"
_DEFAULT_STRIP = [
    "BLANK", "CHERRY", "BLANK", "LEMON", "BLANK",
    "BELL", "BLANK", "BAR", "BLANK", "SEVEN",
    "BLANK", "LEMON", "BELL", "BLANK", "CHERRY",
    "BELL", "BLANK", "LEMON", "BAR", "BELL",
]  # fmt: skip
DEFAULT_CONFIG = {
    "reel_strips": [list(_DEFAULT_STRIP) for _ in range(REEL_COUNT)],
    "paytable": [
        {"type": "three_of_a_kind", "symbol": "SEVEN", "payout": 200},
        {"type": "three_of_a_kind", "symbol": "BAR", "payout": 50},
        {"type": "three_of_a_kind", "symbol": "BELL", "payout": 20},
        {"type": "three_of_a_kind", "symbol": "CHERRY", "payout": 20},
        {"type": "three_of_a_kind", "symbol": "LEMON", "payout": 10},
        {"type": "cherry_count", "count": 2, "payout": 5},
        {"type": "cherry_count", "count": 1, "payout": 2},
    ],
}


def validate_config(config):
    """Check a configuration. Raises ValueError with a readable message."""
    if not isinstance(config, dict):
        raise ValueError("configuration must be an object")

    strips = config.get("reel_strips")
    if not isinstance(strips, list) or len(strips) != REEL_COUNT:
        raise ValueError(f"reel_strips must be a list of {REEL_COUNT} reels")
    for number, strip in enumerate(strips, start=1):
        if not isinstance(strip, list) or not 1 <= len(strip) <= MAX_STRIP_LENGTH:
            raise ValueError(
                f"reel {number} must have 1 to {MAX_STRIP_LENGTH} positions"
            )
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

def expected_range(theoretical, std_dev, spins, upper_limit=None):
    """Return (low, high): the range in which the actual value lies with 95 %
    probability, if the spins follow the configuration (decision 0018).

    The standard error of an average over `spins` spins is std_dev / sqrt(spins).
    """
    margin = Z_95 * std_dev / math.sqrt(spins)
    low = max(0.0, theoretical - margin)
    high = theoretical + margin
    if upper_limit is not None:
        high = min(upper_limit, high)
    return low, high


def _compare(actual, theoretical, std_dev, spins, upper_limit=None):
    """One line of the analysis: actual vs. theoretical value with the range."""
    if spins == 0:
        return {
            "actual": None,
            "theoretical": theoretical,
            "low": None,
            "high": None,
            "in_range": None,
        }
    low, high = expected_range(theoretical, std_dev, spins, upper_limit)
    return {
        "actual": actual,
        "theoretical": theoretical,
        "low": low,
        "high": high,
        "in_range": low <= actual <= high,
    }


def _binomial_std_dev(probability):
    """Standard deviation of a yes/no event (hit or no hit) per spin."""
    return math.sqrt(probability * (1 - probability))


def analyse(config, rows):
    """Compare stored spins with the theoretical values (decision 0018).

    rows are the spins grouped by their three symbols, exactly as returned by
    the database: {"symbol_1": ..., "symbol_2": ..., "symbol_3": ...,
    "spins": n, "bet": total bet, "payout": total payout}. There are at most
    6 x 6 x 6 = 216 rows, independent of the number of spins.

    The winning rule is recalculated from the symbols with the same function
    that is used when playing (evaluate, decision 0012).
    """
    stats = theoretical_stats(config)
    paytable = config["paytable"]

    spins = sum(row["spins"] for row in rows)
    total_bet = sum(row["bet"] for row in rows)
    total_payout = sum(row["payout"] for row in rows)

    hits_per_rule = [0] * len(paytable)
    for row in rows:
        symbols = [row["symbol_1"], row["symbol_2"], row["symbol_3"]]
        rule_index, _ = evaluate(symbols, paytable)
        if rule_index is not None:
            hits_per_rule[rule_index] += row["spins"]
    hits = sum(hits_per_rule)

    # Standard deviation of the payout of one spin, used for the RTP range:
    # variance = E[payout^2] - E[payout]^2
    mean_square = sum(
        rule["probability"] * (rule["rule"]["payout"] * BET) ** 2
        for rule in stats["rules"]
    )
    payout_std_dev = math.sqrt(max(0.0, mean_square - (stats["rtp"] * BET) ** 2))

    def share(count):
        return count / spins if spins else None

    rules = []
    for rule, rule_hits in zip(stats["rules"], hits_per_rule, strict=True):
        probability = rule["probability"]
        rules.append(
            {
                "rule": rule["rule"],
                "hits": rule_hits,
                **_compare(
                    share(rule_hits),
                    probability,
                    _binomial_std_dev(probability),
                    spins,
                    upper_limit=1.0,
                ),
            }
        )

    return {
        "spins": spins,
        "total_bet": total_bet,
        "total_payout": total_payout,
        "rtp": _compare(
            total_payout / total_bet if total_bet else None,
            stats["rtp"],
            payout_std_dev / BET,
            spins,
        ),
        "hit_frequency": _compare(
            share(hits),
            stats["hit_frequency"],
            _binomial_std_dev(stats["hit_frequency"]),
            spins,
            upper_limit=1.0,
        ),
        "rules": rules,
    }