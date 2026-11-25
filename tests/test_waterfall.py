import numpy as np
import pytest

from vc_captable_waterfall_model import (
    build_cap_table,
    calculate_european_carry,
    calculate_exit_payouts,
    evaluate_conversion_state,
    find_conversion_thresholds,
)


def test_exit_proceeds_are_conserved_across_valuation_sweep():
    cap = build_cap_table()
    for exit_value in np.linspace(0.0, 500_000_000.0, 50):
        payouts = calculate_exit_payouts(exit_value, cap)
        assert payouts["total_payout"] == pytest.approx(exit_value, abs=1e-6)


def test_ownership_conservation_and_round_investor_protection():
    baseline = build_cap_table()
    for stage in ("ownership_post_seed", "ownership_post_a", "ownership_post_b"):
        assert sum(baseline[stage].values()) == pytest.approx(1.0, abs=1e-12)

    small_pools = build_cap_table(esop_a_target_post=0.05, esop_b_target_post=0.05)
    large_pools = build_cap_table(esop_a_target_post=0.20, esop_b_target_post=0.20)
    assert small_pools["ownership_post_a"]["Series A"] == pytest.approx(0.20)
    assert large_pools["ownership_post_a"]["Series A"] == pytest.approx(0.20)
    assert small_pools["ownership_post_b"]["Series B"] == pytest.approx(0.25)
    assert large_pools["ownership_post_b"]["Series B"] == pytest.approx(0.25)


def test_four_tier_carry_waterfall_conserves_gross_proceeds():
    outcomes = {
        value: calculate_european_carry(value)
        for value in (180.0, 280.0, 320.0, 475.0)
    }

    for gross_value, outcome in outcomes.items():
        assert outcome["lp_net_proceeds"] + outcome["gp_carry"] == pytest.approx(
            gross_value, abs=1e-10
        )

    assert outcomes[180.0]["gp_carry"] == pytest.approx(0.0)
    assert outcomes[280.0]["gp_carry"] == pytest.approx(0.0)
    assert 0.0 < outcomes[320.0]["tier3_gp"] < outcomes[320.0]["catch_up_target"]
    assert outcomes[475.0]["gp_carry"] == pytest.approx(55.0, abs=1e-10)
    assert outcomes[475.0]["lp_net_proceeds"] == pytest.approx(420.0)


def test_equilibrium_never_prefers_conversion_when_it_pays_less():
    cap = build_cap_table()
    for exit_value in np.linspace(0.0, 500_000_000.0, 50):
        equilibrium = calculate_exit_payouts(exit_value, cap)
        for index, investor in enumerate(("B", "A", "Seed")):
            opposite = list(equilibrium["conversion"])
            opposite[index] = not opposite[index]
            alternative = evaluate_conversion_state(exit_value, tuple(opposite), cap)
            assert equilibrium[investor] >= alternative[investor] - 1e-6


def test_conversion_thresholds_are_exact_equilibrium_switches():
    cap = build_cap_table()
    thresholds = find_conversion_thresholds(cap)
    assert {row["Security"] for row in thresholds} == {
        "Series B", "Series A", "Seed SAFE"
    }
    expected = {
        "Seed SAFE": 64_571_428.57142857,
        "Series A": 87_600_000.0,
        "Series B": 360_000_000.0,
    }
    for row in thresholds:
        threshold = row["Exit_Valuation"]
        assert threshold == pytest.approx(expected[row["Security"]], abs=0.01)
        before = calculate_exit_payouts(threshold - 1.0, cap)["conversion"]
        after = calculate_exit_payouts(threshold + 1.0, cap)["conversion"]
        index = {"Series B": 0, "Series A": 1, "Seed SAFE": 2}[row["Security"]]
        assert before[index] != after[index]


def test_case_study_cap_table_baseline():
    cap = build_cap_table()
    assert cap["post_b_total_shares"] == 18_000_000
    assert cap["ownership_post_b"]["Founders"] == pytest.approx(7 / 18)
