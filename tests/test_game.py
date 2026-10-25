"""Unit tests for the game logic. They need no database and no network."""

import copy
import random
from itertools import product

import pytest

from app import game, rng

# Every reel: 1 cherry, 1 seven, 2 blanks (4 positions).
# Probability per reel: cherry 1/4, seven 1/4, other 3/4 resp. 2/4.
CONFIG = {
    "reel_strips": [["CHERRY", "SEVEN", "BLANK", "BLANK"]] * 3,
    "paytable": [
        {"type": "three_of_a_kind", "symbol": "SEVEN", "payout": 100},
        {"type": "three_of_a_kind", "symbol": "CHERRY", "payout": 20},
        {"type": "cherry_count", "count": 3, "payout": 10},
        {"type": "cherry_count", "count": 2, "payout": 5},
        {"type": "cherry_count", "count": 1, "payout": 2},
    ],
}


def fixed(*stops):
    """A random source that always returns the given stop positions."""
    return lambda strip_lengths: list(stops)


# --- spin and evaluate ---


def test_spin_takes_symbols_at_stop_positions():
    result = game.spin(CONFIG, fixed(1, 2, 0))

    assert result["stops"] == [1, 2, 0]
    assert result["symbols"] == ["SEVEN", "BLANK", "CHERRY"]


def test_three_of_a_kind_pays():
    result = game.spin(CONFIG, fixed(1, 1, 1))

    assert result["rule_index"] == 0
    assert result["payout"] == 100


@pytest.mark.parametrize(
    "symbols, expected_rule, expected_payout",
    [
        (["CHERRY", "BLANK", "BLANK"], 4, 2),
        (["BLANK", "BLANK", "CHERRY"], 4, 2),
        (["CHERRY", "SEVEN", "CHERRY"], 3, 5),
    ],
)
def test_cherry_count_pays_exact_count_at_any_position(
    symbols, expected_rule, expected_payout
):
    assert game.evaluate(symbols, CONFIG["paytable"]) == (
        expected_rule,
        expected_payout,
    )


def test_only_highest_matching_rule_pays():
    # Three cherries match "three_of_a_kind CHERRY" (20) and "cherry_count 3" (10).
    assert game.evaluate(["CHERRY"] * 3, CONFIG["paytable"]) == (1, 20)


def test_no_win_pays_nothing():
    assert game.evaluate(["SEVEN", "BLANK", "SEVEN"], CONFIG["paytable"]) == (None, 0)


def test_spin_rejects_stop_outside_strip():
    with pytest.raises(ValueError):
        game.spin(CONFIG, fixed(0, 0, 4))


# --- theoretical values ---


def test_theoretical_stats_match_hand_calculation():
    stats = game.theoretical_stats(CONFIG)
    probabilities = [rule["probability"] for rule in stats["rules"]]

    # 3 sevens: 1/64. 3 cherries: 1/64 (paid by rule 1, rule 2 never pays).
    # Exactly 2 cherries: 3 * 1/4 * 1/4 * 3/4 = 9/64.
    # Exactly 1 cherry:   3 * 1/4 * 3/4 * 3/4 = 27/64.
    assert probabilities == pytest.approx([1 / 64, 1 / 64, 0, 9 / 64, 27 / 64])
    assert stats["hit_frequency"] == pytest.approx(38 / 64)
    assert stats["rtp"] == pytest.approx((100 + 20 + 45 + 54) / 64)


def test_theoretical_stats_match_all_stop_positions():
    """Counting symbols must give the same result as trying every position."""
    config = {
        "reel_strips": [
            ["CHERRY", "BLANK", "BAR", "SEVEN", "BLANK"],
            ["BLANK", "CHERRY", "CHERRY", "BAR"],
            ["SEVEN", "BLANK", "BLANK", "LEMON", "CHERRY", "BELL"],
        ],
        "paytable": CONFIG["paytable"],
    }
    lengths = [len(strip) for strip in config["reel_strips"]]
    all_stops = list(product(*(range(length) for length in lengths)))
    payouts = [game.spin(config, fixed(*stops))["payout"] for stops in all_stops]

    stats = game.theoretical_stats(config)

    assert stats["rtp"] == pytest.approx(sum(payouts) / len(all_stops))
    assert stats["hit_frequency"] == pytest.approx(
        sum(1 for payout in payouts if payout > 0) / len(all_stops)
    )


def test_empty_paytable_has_zero_rtp():
    config = {"reel_strips": CONFIG["reel_strips"], "paytable": []}

    stats = game.theoretical_stats(config)

    assert stats == {"rules": [], "hit_frequency": 0, "rtp": 0}


# --- validation ---


def test_valid_config_passes():
    game.validate_config(CONFIG)


def broken(change):
    """Return a copy of CONFIG with one change applied."""
    config = copy.deepcopy(CONFIG)
    change(config)
    return config


@pytest.mark.parametrize(
    "config",
    [
        "not a dict",
        broken(lambda c: c["reel_strips"].pop()),
        broken(lambda c: c["reel_strips"].__setitem__(0, [])),
        broken(lambda c: c["reel_strips"][0].append("DIAMOND")),
        broken(lambda c: c.pop("paytable")),
        broken(lambda c: c["paytable"].append({"type": "any_bar", "payout": 5})),
        broken(lambda c: c["paytable"][0].update(symbol="DIAMOND")),
        broken(lambda c: c["paytable"][3].update(count=4)),
        broken(lambda c: c["paytable"][0].update(payout=0)),
        broken(lambda c: c["paytable"][0].update(payout=2.5)),
        broken(lambda c: c["paytable"][0].update(payout=True)),
    ],
)
def test_invalid_config_is_rejected(config):
    with pytest.raises(ValueError):
        game.validate_config(config)


# --- random source ---


def test_python_stop_positions_are_within_strips():
    for _ in range(1000):
        stops = rng.python_stop_positions([3, 1, 7])
        assert 0 <= stops[0] < 3
        assert stops[1] == 0
        assert 0 <= stops[2] < 7


def test_manual_stop_positions_use_random_org(monkeypatch):
    monkeypatch.setattr(rng, "random_org_stop_positions", lambda lengths: [1, 2, 3])

    assert rng.manual_stop_positions([5, 5, 5]) == ([1, 2, 3], "random.org")


def test_manual_stop_positions_fall_back_to_python(monkeypatch):
    def failing(strip_lengths):
        raise OSError("random.org not reachable")

    monkeypatch.setattr(rng, "random_org_stop_positions", failing)

    stops, source = rng.manual_stop_positions([5, 5, 5])

    assert source == "python"
    assert all(0 <= stop < 5 for stop in stops)


def test_random_org_answer_is_parsed():
    assert rng.parse_random_org_number("17\n", 20) == 17


@pytest.mark.parametrize("text", ["20\n", "-1\n", "Error: quota exceeded\n"])
def test_unexpected_random_org_answer_is_rejected(text):
    with pytest.raises(ValueError):
        rng.parse_random_org_number(text, 20)


# --- default configuration ---


def test_default_config_is_valid_and_favours_the_house():
    game.validate_config(game.DEFAULT_CONFIG)

    stats = game.theoretical_stats(game.DEFAULT_CONFIG)

    assert stats["rtp"] == pytest.approx(0.9098, abs=0.0001)
    assert stats["hit_frequency"] == pytest.approx(0.2835, abs=0.0001)


def test_reel_with_30_positions_is_valid():
    config = broken(lambda c: c["reel_strips"].__setitem__(0, ["BLANK"] * 30))

    game.validate_config(config)


def test_reel_with_31_positions_is_rejected():
    config = broken(lambda c: c["reel_strips"].__setitem__(0, ["BLANK"] * 31))

    with pytest.raises(ValueError):
        game.validate_config(config)


# --- analysis (decision 0018) ---


def row(symbols, spins, payout):
    """One row as returned by the database: spins grouped by their symbols."""
    s1, s2, s3 = symbols
    return {
        "symbol_1": s1,
        "symbol_2": s2,
        "symbol_3": s3,
        "spins": spins,
        "bet": spins * game.BET,
        "payout": payout,
    }


def test_analysis_counts_hits_per_rule():
    rows = [
        row(["SEVEN", "SEVEN", "SEVEN"], 1, 100),
        row(["CHERRY", "CHERRY", "BLANK"], 2, 10),
        row(["CHERRY", "BLANK", "BLANK"], 3, 6),
        row(["BLANK", "BLANK", "BLANK"], 4, 0),
    ]

    result = game.analyse(CONFIG, rows)

    assert result["spins"] == 10
    assert result["total_bet"] == 10
    assert result["total_payout"] == 116
    assert [rule["hits"] for rule in result["rules"]] == [1, 0, 0, 2, 3]
    assert result["rules"][3]["actual"] == pytest.approx(0.2)
    assert result["hit_frequency"]["actual"] == pytest.approx(0.6)
    assert result["rtp"]["actual"] == pytest.approx(11.6)


def test_analysis_counts_three_cherries_only_for_the_highest_rule():
    # Three cherries match "three of a kind CHERRY" (20) and "cherry count 3"
    # (10); only the higher one pays (decision 0012).
    result = game.analyse(CONFIG, [row(["CHERRY"] * 3, 5, 100)])

    assert [rule["hits"] for rule in result["rules"]] == [0, 5, 0, 0, 0]


def test_analysis_without_spins_has_no_actual_values():
    result = game.analyse(CONFIG, [])

    assert result["spins"] == 0
    assert result["rtp"]["actual"] is None
    assert result["rtp"]["in_range"] is None
    assert result["rtp"]["theoretical"] == pytest.approx(
        game.theoretical_stats(CONFIG)["rtp"]
    )


def test_expected_range_gets_narrower_with_more_spins():
    low_100, high_100 = game.expected_range(0.5, 0.5, 100)
    low_10000, high_10000 = game.expected_range(0.5, 0.5, 10_000)

    # 1.96 * 0.5 / sqrt(100) = 0.098
    assert (low_100, high_100) == pytest.approx((0.402, 0.598))
    assert high_10000 - low_10000 == pytest.approx((high_100 - low_100) / 10)


def test_expected_range_stays_between_0_and_1_for_frequencies():
    low, high = game.expected_range(0.99, 0.1, 4, upper_limit=1.0)

    assert low >= 0.0
    assert high == 1.0


def test_default_config_rtp_range_for_1000_spins():
    # Standard deviation of the payout per spin is about 3.5 (decision 0018),
    # so after 1000 spins the RTP lies within about 91 % +/- 21.7 %.
    result = game.analyse(
        game.DEFAULT_CONFIG, [row(["BLANK", "BLANK", "BLANK"], 1000, 0)]
    )

    rtp = result["rtp"]
    assert rtp["high"] - rtp["theoretical"] == pytest.approx(0.217, abs=0.001)
    assert rtp["actual"] == 0.0
    assert rtp["in_range"] is False


def test_simulated_spins_lie_within_the_expected_range():
    # 20,000 spins with a fixed seed: the actual values match the theory.
    generator = random.Random(42)

    def seeded(strip_lengths):
        return [generator.randrange(length) for length in strip_lengths]

    grouped = {}
    for _ in range(20_000):
        result = game.spin(game.DEFAULT_CONFIG, seeded)
        key = tuple(result["symbols"])
        spins, payout = grouped.get(key, (0, 0))
        grouped[key] = (spins + 1, payout + result["payout"])
    rows = [row(list(key), spins, payout) for key, (spins, payout) in grouped.items()]

    analysis = game.analyse(game.DEFAULT_CONFIG, rows)

    assert analysis["spins"] == 20_000
    assert analysis["rtp"]["in_range"]
    assert analysis["hit_frequency"]["in_range"]
