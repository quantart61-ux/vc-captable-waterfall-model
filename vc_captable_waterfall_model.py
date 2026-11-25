"""Venture-capital cap table, exit waterfall, and fund carry calculations."""

import pandas as pd


def build_cap_table(esop_a_target_post=0.10, esop_b_target_post=0.125):
    """Build the case-study cap table and stage-by-stage ownership percentages."""
    founders_shares = 7_000_000
    seed_investment = 3_000_000
    seed_post_cap = 15_000_000
    seed_shares = int(round(founders_shares * (
        (seed_investment / seed_post_cap) / (1.0 - seed_investment / seed_post_cap)
    )))

    series_a_pre = 32_000_000
    series_a_inv = 8_000_000
    series_a_ownership = series_a_inv / (series_a_pre + series_a_inv)
    post_a_total_shares = int(round(
        (founders_shares + seed_shares) /
        (1.0 - series_a_ownership - esop_a_target_post)
    ))
    esop_a_shares = int(round(post_a_total_shares * esop_a_target_post))
    series_a_shares = int(round(post_a_total_shares * series_a_ownership))
    series_a_pps = series_a_pre / (
        founders_shares + seed_shares + esop_a_shares
    )

    series_b_pre = 90_000_000
    series_b_inv = 30_000_000
    series_b_ownership = series_b_inv / (series_b_pre + series_b_inv)
    non_esop_pre_b = founders_shares + seed_shares + series_a_shares
    post_b_total_shares = int(round(
        non_esop_pre_b / (1.0 - series_b_ownership - esop_b_target_post)
    ))
    esop_b_total_shares = int(round(post_b_total_shares * esop_b_target_post))
    series_b_shares = int(round(post_b_total_shares * series_b_ownership))
    series_b_pps = series_b_pre / (non_esop_pre_b + esop_b_total_shares)

    ownership_post_seed = {
        "Founders": founders_shares / (founders_shares + seed_shares),
        "Seed": seed_shares / (founders_shares + seed_shares),
    }
    ownership_post_a = {
        "Founders": founders_shares / post_a_total_shares,
        "ESOP": esop_a_shares / post_a_total_shares,
        "Seed": seed_shares / post_a_total_shares,
        "Series A": series_a_shares / post_a_total_shares,
    }
    ownership_post_b = {
        "Founders": founders_shares / post_b_total_shares,
        "ESOP": esop_b_total_shares / post_b_total_shares,
        "Seed": seed_shares / post_b_total_shares,
        "Series A": series_a_shares / post_b_total_shares,
        "Series B": series_b_shares / post_b_total_shares,
    }
    cap_table = pd.DataFrame([
        {
            "Stakeholder": "Founders (Common)",
            "Security_Type": "Common Stock",
            "Shares": founders_shares,
            "Invested_Capital": 0.0,
            "Issue_PPS": 0.00,
            "Post_A_Pct": ownership_post_a["Founders"],
            "Post_B_Pct": ownership_post_b["Founders"],
        },
        {
            "Stakeholder": "Employee Option Pool (ESOP)",
            "Security_Type": "Common Options",
            "Shares": esop_b_total_shares,
            "Invested_Capital": 0.0,
            "Issue_PPS": 0.00,
            "Post_A_Pct": ownership_post_a["ESOP"],
            "Post_B_Pct": ownership_post_b["ESOP"],
        },
        {
            "Stakeholder": "Seed Investors (Post-Money SAFE)",
            "Security_Type": "Series Seed Preferred",
            "Shares": seed_shares,
            "Invested_Capital": seed_investment,
            "Issue_PPS": seed_investment / seed_shares,
            "Post_A_Pct": ownership_post_a["Seed"],
            "Post_B_Pct": ownership_post_b["Seed"],
        },
        {
            "Stakeholder": "Series A Investors",
            "Security_Type": "Series A Preferred",
            "Shares": series_a_shares,
            "Invested_Capital": series_a_inv,
            "Issue_PPS": series_a_pps,
            "Post_A_Pct": ownership_post_a["Series A"],
            "Post_B_Pct": ownership_post_b["Series A"],
        },
        {
            "Stakeholder": "Series B Investors",
            "Security_Type": "Series B Preferred",
            "Shares": series_b_shares,
            "Invested_Capital": series_b_inv,
            "Issue_PPS": series_b_pps,
            "Post_A_Pct": 0.0,
            "Post_B_Pct": ownership_post_b["Series B"],
        },
    ])
    return {
        "founders_shares": founders_shares,
        "seed_shares": seed_shares,
        "series_a_shares": series_a_shares,
        "series_b_shares": series_b_shares,
        "esop_a_shares": esop_a_shares,
        "esop_b_total_shares": esop_b_total_shares,
        "post_a_total_shares": post_a_total_shares,
        "post_b_total_shares": post_b_total_shares,
        "seed_investment": seed_investment,
        "series_a_investment": series_a_inv,
        "series_b_investment": series_b_inv,
        "series_a_pps": series_a_pps,
        "series_b_pps": series_b_pps,
        "series_a_round_ownership": series_a_ownership,
        "series_b_round_ownership": series_b_ownership,
        "ownership_post_seed": ownership_post_seed,
        "ownership_post_a": ownership_post_a,
        "ownership_post_b": ownership_post_b,
        "cap_table": cap_table,
    }


def _payout_for_state(exit_value, conversion, cap):
    """Allocate an exit under one fixed set of preferred/common elections."""
    conv_b, conv_a, conv_seed = conversion
    rem = float(exit_value)
    pay_b = pay_a = pay_seed = 0.0
    pay_founders = pay_esop = 0.0

    if not conv_b:
        pay_b = min(rem, cap["series_b_investment"])
        rem -= pay_b

    tier2_claims = {}
    if not conv_a:
        tier2_claims["A"] = cap["series_a_investment"]
    if not conv_seed:
        tier2_claims["Seed"] = cap["seed_investment"]
    total_tier2 = sum(tier2_claims.values())
    if total_tier2 > 0 and rem > 0:
        allocation = min(rem, total_tier2)
        if "A" in tier2_claims:
            pay_a += allocation * tier2_claims["A"] / total_tier2
        if "Seed" in tier2_claims:
            pay_seed += allocation * tier2_claims["Seed"] / total_tier2
        rem -= allocation

    common_shares = cap["founders_shares"] + cap["esop_b_total_shares"]
    if conv_b:
        common_shares += cap["series_b_shares"]
    if conv_a:
        common_shares += cap["series_a_shares"]
    if conv_seed:
        common_shares += cap["seed_shares"]

    if rem > 0:
        if not conv_b:
            participation_pool = common_shares + cap["series_b_shares"]
            participation_share = cap["series_b_shares"] / participation_pool
            remaining_cap = max(
                0.0, cap["series_b_investment"] * 3.0 - pay_b
            )
            participation = min(rem * participation_share, remaining_cap)
            pay_b += participation
            rem -= participation

        pay_founders = rem * cap["founders_shares"] / common_shares
        pay_esop = rem * cap["esop_b_total_shares"] / common_shares
        if conv_b:
            pay_b += rem * cap["series_b_shares"] / common_shares
        if conv_a:
            pay_a += rem * cap["series_a_shares"] / common_shares
        if conv_seed:
            pay_seed += rem * cap["seed_shares"] / common_shares

    return {
        "B": pay_b,
        "A": pay_a,
        "Seed": pay_seed,
        "Founders": pay_founders,
        "ESOP": pay_esop,
        "conversion": conversion,
    }


def _all_states(exit_value, cap):
    return {
        (conv_b, conv_a, conv_seed): _payout_for_state(
            exit_value, (conv_b, conv_a, conv_seed), cap
        )
        for conv_b in (False, True)
        for conv_a in (False, True)
        for conv_seed in (False, True)
    }


def _equilibrium_state(exit_value, cap):
    states = _all_states(exit_value, cap)
    for state, payout in states.items():
        conv_b, conv_a, conv_seed = state
        b_ok = payout["B"] >= states[(not conv_b, conv_a, conv_seed)]["B"] - 1e-6
        a_ok = payout["A"] >= states[(conv_b, not conv_a, conv_seed)]["A"] - 1e-6
        seed_ok = payout["Seed"] >= states[(conv_b, conv_a, not conv_seed)]["Seed"] - 1e-6
        if b_ok and a_ok and seed_ok:
            return payout
    raise ArithmeticError(f"No pure-strategy conversion equilibrium at exit {exit_value}")


def calculate_exit_payouts(exit_value, cap=None):
    """Return the Nash-equilibrium exit allocation, with exit value in dollars."""
    cap = cap or build_cap_table()
    payout = _equilibrium_state(exit_value, cap).copy()
    payout["exit_value"] = float(exit_value)
    payout["total_payout"] = sum(
        payout[key] for key in ("B", "A", "Seed", "Founders", "ESOP")
    )
    return payout


def evaluate_conversion_state(exit_value, conversion, cap=None):
    """Return a payout for an explicitly supplied (B, A, Seed) election profile."""
    return _payout_for_state(exit_value, conversion, cap or build_cap_table())


def _state_breakpoints(conversion, cap):
    """All allocation kinks for one conversion profile (exit values in dollars)."""
    conv_b, conv_a, conv_seed = conversion
    senior_claim = 0.0 if conv_b else cap["series_b_investment"]
    junior_claim = (
        (0.0 if conv_a else cap["series_a_investment"])
        + (0.0 if conv_seed else cap["seed_investment"])
    )
    points = {0.0, senior_claim, senior_claim + junior_claim}
    if not conv_b:
        common_shares = (
            cap["founders_shares"] + cap["esop_b_total_shares"]
            + (cap["series_a_shares"] if conv_a else 0)
            + (cap["seed_shares"] if conv_seed else 0)
        )
        participation_share = cap["series_b_shares"] / (
            common_shares + cap["series_b_shares"]
        )
        participation_cap = cap["series_b_investment"] * 2.0
        points.add(
            senior_claim + junior_claim + participation_cap / participation_share
        )
    return sorted(points)


def _deviation_roots(conversion, deviated, investor, cap):
    """Find exact roots of two piecewise-linear payouts' difference."""
    points = sorted(set(
        _state_breakpoints(conversion, cap)
        + _state_breakpoints(deviated, cap)
    ))

    def difference(exit_value):
        return (
            _payout_for_state(exit_value, conversion, cap)[investor]
            - _payout_for_state(exit_value, deviated, cap)[investor]
        )

    roots = set()
    for left, right in zip(points, points[1:]):
        f_left, f_right = difference(left), difference(right)
        if abs(f_left) <= 1e-8:
            roots.add(left)
        if f_left * f_right < 0:
            roots.add(left + (right - left) * (-f_left) / (f_right - f_left))
        if abs(f_right) <= 1e-8:
            roots.add(right)

    last = points[-1]
    f_last = difference(last)
    slope = difference(last + 1.0) - f_last
    if abs(slope) > 1e-12:
        root = last - f_last / slope
        if root > last and abs(difference(root)) <= 1e-5:
            roots.add(root)
    return roots


def find_conversion_thresholds(cap=None):
    """Find exact Nash-election switch values, including the Series B cap kink.

    Payouts are piecewise linear in exit value. The solver enumerates each
    state's analytical kinks and solves every unilateral-indifference equation
    on each linear segment, then checks the equilibrium on either side.
    """
    cap = cap or build_cap_table()
    profiles = [
        (conv_b, conv_a, conv_seed)
        for conv_b in (False, True)
        for conv_a in (False, True)
        for conv_seed in (False, True)
    ]
    breakpoints = {0.0}
    for profile in profiles:
        breakpoints.update(_state_breakpoints(profile, cap))
        for index, investor in enumerate(("B", "A", "Seed")):
            for other_profile in profiles:
                if any(
                    other_profile[position] != profile[position]
                    for position in range(3) if position != index
                ):
                    continue
                deviation = list(profile)
                deviation[index] = not deviation[index]
                breakpoints.update(
                    _deviation_roots(
                        profile, tuple(deviation), investor, cap
                    )
                )

    points = sorted(point for point in breakpoints if point >= 0.0)
    transitions = []
    for index in range(1, len(points)):
        left, right = points[index - 1], points[index]
        left_state = _equilibrium_state((left + right) / 2.0, cap)["conversion"]
        if index + 1 < len(points):
            next_right = points[index + 1]
            right_sample = (right + next_right) / 2.0
        else:
            right_sample = right + max(1.0, right)
        right_state = _equilibrium_state(right_sample, cap)["conversion"]
        for investor_index, investor in enumerate(("B", "A", "Seed")):
            if left_state[investor_index] != right_state[investor_index]:
                transitions.append({
                    "Security": {"B": "Series B", "A": "Series A", "Seed": "Seed SAFE"}[investor],
                    "Exit_Valuation": right,
                    "From": "Common" if left_state[investor_index] else "Preferred",
                    "To": "Common" if right_state[investor_index] else "Preferred",
                })
    return transitions


def calculate_european_carry(gross_value, fund=None):
    """Apply a four-tier European waterfall; fund amounts are in $ millions.

    Fees are not deducted here because they have already reduced investable
    capital relative to committed capital.
    """
    fund = fund or {
        "committed_capital": 200.0,
        "carry_rate": 0.20,
        "hurdle_rate": 0.08,
        "avg_hold_years": 5.5,
    }
    capital = fund["committed_capital"]
    carry_rate = fund["carry_rate"]
    hurdle_target = capital * (1.0 + fund["hurdle_rate"]) ** fund["avg_hold_years"]
    hurdle_profit = hurdle_target - capital
    catch_up_target = hurdle_profit * carry_rate / (1.0 - carry_rate)
    gross_value = max(0.0, float(gross_value))

    tier1_lp = min(gross_value, capital)
    tier2_lp = min(max(gross_value - capital, 0.0), hurdle_profit)
    tier3_gp = min(max(gross_value - hurdle_target, 0.0), catch_up_target)
    tier4_residual = max(gross_value - hurdle_target - catch_up_target, 0.0)
    tier4_gp = tier4_residual * carry_rate
    tier4_lp = tier4_residual * (1.0 - carry_rate)
    gp_carry = tier3_gp + tier4_gp
    lp_gross_proceeds = tier1_lp + tier2_lp + tier4_lp
    return {
        "gross_value": gross_value,
        "hurdle_target": hurdle_target,
        "catch_up_target": catch_up_target,
        "tier1_lp": tier1_lp,
        "tier2_lp": tier2_lp,
        "tier3_gp": tier3_gp,
        "tier4_gp": tier4_gp,
        "tier4_lp": tier4_lp,
        "lp_gross_proceeds": lp_gross_proceeds,
        "lp_net_proceeds": lp_gross_proceeds,
        "gp_carry": gp_carry,
    }


def run_vc_model():
    startup = {
        "name": "Vanguard Cloud Analytics Inc.",
        "sector": "B2B AI Infrastructure & Data Observability SaaS",
        "current_arr": 12.0,
        "ntm_arr": 20.0,
        "yoy_arr_growth": 0.85,
        "gross_margin": 0.78,
        "net_dollar_retention": 1.24,
        "annual_net_burn": 6.6,
        "cash_balance": 11.0,
        "cac_payback_months": 14.0,
        "ltv_cac": 4.80,
        "ebitda_margin": -0.32,
    }
    runway_months = startup["cash_balance"] / startup["annual_net_burn"] * 12.0
    rule_of_40 = (startup["yoy_arr_growth"] + startup["ebitda_margin"]) * 100.0
    net_new_arr = startup["ntm_arr"] - startup["current_arr"]
    burn_multiple = startup["annual_net_burn"] / net_new_arr
    implied_pre_money = startup["current_arr"] * 7.5

    print("=" * 94)
    print("=== [PART 1] STARTUP UNIT ECONOMICS & SERIES B VALUATION ===")
    print(f"Company: {startup['name']} ({startup['sector']})")
    print(f"Current ARR: ${startup['current_arr']:.1f}M | NTM ARR: ${startup['ntm_arr']:.1f}M | YoY Growth: {startup['yoy_arr_growth']:.0%}")
    print(f"Gross Margin: {startup['gross_margin']:.0%} | NDR: {startup['net_dollar_retention']:.0%} | LTV/CAC: {startup['ltv_cac']:.1f}x")
    print(f"Runway: {runway_months:.1f} mos | Rule of 40: {rule_of_40:.1f}% | Burn Multiple: {burn_multiple:.2f}x")
    print(f"Implied Series B Pre-Money Valuation (7.5x Current ARR): ${implied_pre_money:.2f}M\n")

    cap = build_cap_table()
    cap_table = cap["cap_table"]
    print("=== [PART 2] POST-SERIES B FULLY DILUTED CAP TABLE ===")
    print(f"Series A PPS: ${cap['series_a_pps']:.2f} | Series B PPS: ${cap['series_b_pps']:.2f} | Post-B Shares: {cap['post_b_total_shares']:,}")
    display_cap = cap_table.copy()
    display_cap["Shares"] = display_cap["Shares"].map(lambda x: f"{x:,}")
    display_cap["Invested_Capital"] = display_cap["Invested_Capital"].map(lambda x: f"${x/1e6:,.2f}M")
    display_cap["Issue_PPS"] = display_cap["Issue_PPS"].map(lambda x: f"${x:,.2f}" if x > 0 else "-")
    display_cap["Post_A_Pct"] = display_cap["Post_A_Pct"].map(lambda x: f"{x:.2%}")
    display_cap["Post_B_Pct"] = display_cap["Post_B_Pct"].map(lambda x: f"{x:.2%}")
    print(display_cap.to_string(index=False))

    exit_valuations = [25_000_000, 60_000_000, 150_000_000, 400_000_000]
    waterfall_rows = []
    for exit_value in exit_valuations:
        eq_state = calculate_exit_payouts(exit_value, cap)
        b_moic = eq_state["B"] / cap["series_b_investment"]
        a_moic = eq_state["A"] / cap["series_a_investment"]
        seed_moic = eq_state["Seed"] / cap["seed_investment"]
        conv_b, conv_a, conv_seed = eq_state["conversion"]
        waterfall_rows.append({
            "Exit_Val": f"${exit_value/1e6:,.0f}M",
            "Series_B": f"${eq_state['B']/1e6:,.2f}M ({b_moic:.2f}x)",
            "Series_A": f"${eq_state['A']/1e6:,.2f}M ({a_moic:.2f}x)",
            "Seed_SAFE": f"${eq_state['Seed']/1e6:,.2f}M ({seed_moic:.2f}x)",
            "Founders": f"${eq_state['Founders']/1e6:,.2f}M",
            "ESOP": f"${eq_state['ESOP']/1e6:,.2f}M",
            "Conversion_Outcome": (
                f"B:{'Conv' if conv_b else 'Pref'} | "
                f"A:{'Conv' if conv_a else 'Pref'} | "
                f"Seed:{'Conv' if conv_seed else 'Pref'}"
            ),
        })
    print("\n=== [PART 3] EXIT WATERFALL & CONVERSION EQUILIBRIUM MATRIX ===")
    print(pd.DataFrame(waterfall_rows).to_string(index=False))

    threshold_rows = find_conversion_thresholds(cap)
    threshold_table = pd.DataFrame(threshold_rows)
    if not threshold_table.empty:
        threshold_table["Exit_Valuation"] = threshold_table["Exit_Valuation"].map(
            lambda value: f"${value / 1e6:,.6f}M"
        )
    print("\n=== EXACT NASH CONVERSION INFLECTION POINTS ===")
    print(threshold_table.to_string(index=False) if not threshold_table.empty else "No conversion switches found.")

    fund = {
        "committed_capital": 200.0,
        "mgmt_fee_inv_period": 0.02,
        "mgmt_fee_harvest": 0.015,
        "org_expenses": 1.0,
        "carry_rate": 0.20,
        "hurdle_rate": 0.08,
        "avg_hold_years": 5.5,
    }
    total_fees_exp = (
        fund["committed_capital"] * fund["mgmt_fee_inv_period"] * 5.0
        + fund["committed_capital"] * fund["mgmt_fee_harvest"] * 5.0
        + fund["org_expenses"]
    )
    investable_capital = fund["committed_capital"] - total_fees_exp
    realized_proceeds, unrealized_nav = 340.0, 135.0
    gross_portfolio_value = realized_proceeds + unrealized_nav
    carry_result = calculate_european_carry(
        gross_portfolio_value,
        fund,
    )
    gross_moic = gross_portfolio_value / investable_capital
    gross_tvpi = gross_portfolio_value / fund["committed_capital"]
    dpi_pre_carry = realized_proceeds / fund["committed_capital"]
    rvpi = unrealized_nav / fund["committed_capital"]
    net_tvpi = carry_result["lp_net_proceeds"] / fund["committed_capital"]
    net_irr = net_tvpi ** (1.0 / fund["avg_hold_years"]) - 1.0

    print("\n=== [PART 4] VC FUND ECONOMICS & EUROPEAN CARRY WATERFALL ($200M FUND) ===")
    print(f"Committed Capital: ${fund['committed_capital']:.1f}M | Lifetime Fees & Exp: ${total_fees_exp:.1f}M | Investable Capital: ${investable_capital:.1f}M")
    print(f"Realized Proceeds: ${realized_proceeds:.1f}M | Unrealized NAV: ${unrealized_nav:.1f}M | Gross Portfolio Value: ${gross_portfolio_value:.1f}M")
    print(f"Gross MOIC (on Invested): {gross_moic:.2f}x | Gross TVPI (on Committed): {gross_tvpi:.2f}x")
    print(f"DPI (Realized): {dpi_pre_carry:.2f}x | RVPI (Unrealized): {rvpi:.2f}x")
    print(f"Hurdle Target (8% Compounded): ${carry_result['hurdle_target']:.2f}M -> Hurdle Cleared: {'YES' if gross_portfolio_value > carry_result['hurdle_target'] else 'NO'}")
    print(f"GP Carried Interest (20%): ${carry_result['gp_carry']:.2f}M | LP Net TVPI: {net_tvpi:.2f}x | Implied LP Net IRR: {net_irr:.2%}")
    print(f"LP Net Proceeds + GP Carry: ${carry_result['lp_net_proceeds'] + carry_result['gp_carry']:.2f}M")
    print("=" * 94)


if __name__ == "__main__":
    run_vc_model()
