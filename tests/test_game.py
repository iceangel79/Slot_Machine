"""Unit tests for the game logic. They need no database and no network."""

import copy
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
