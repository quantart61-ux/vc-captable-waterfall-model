import numpy as np
import pandas as pd


def run_vc_model():
    # ==========================================================================
    # 1. STARTUP UNIT ECONOMICS & SERIES B VALUATION BENCHMARKING
    # ==========================================================================
    startup = {
        "name": "Vanguard Cloud Analytics Inc.",
        "sector": "B2B AI Infrastructure & Data Observability SaaS",
        "current_arr": 12.0,          # $M
        "ntm_arr": 20.0,              # $M (Next-Twelve-Months projected ARR)
        "yoy_arr_growth": 0.85,       # 85% YoY
        "gross_margin": 0.78,         # 78%
        "net_dollar_retention": 1.24, # 124% NDR
        "annual_net_burn": 6.6,       # $M
        "cash_balance": 11.0,         # $M
        "cac_payback_months": 14.0,
        "ltv_cac": 4.80,
        "ebitda_margin": -0.32,       # -32%
    }

    runway_months = (startup["cash_balance"] / startup["annual_net_burn"]) * 12.0
    rule_of_40 = (startup["yoy_arr_growth"] + startup["ebitda_margin"]) * 100.0
    net_new_arr = startup["ntm_arr"] - startup["current_arr"]
    burn_multiple = startup["annual_net_burn"] / net_new_arr
    implied_pre_money = startup["current_arr"] * 7.5  # 7.5x Current ARR / 4.5x NTM ARR

    print("=" * 94)
    print("=== [PART 1] STARTUP UNIT ECONOMICS & SERIES B VALUATION ===")
    print(f"Company: {startup['name']} ({startup['sector']})")
    print(f"Current ARR: ${startup['current_arr']:.1f}M | NTM ARR: ${startup['ntm_arr']:.1f}M | YoY Growth: {startup['yoy_arr_growth']:.0%}")
    print(f"Gross Margin: {startup['gross_margin']:.0%} | NDR: {startup['net_dollar_retention']:.0%} | LTV/CAC: {startup['ltv_cac']:.1f}x")
    print(f"Runway: {runway_months:.1f} mos | Rule of 40: {rule_of_40:.1f}% | Burn Multiple: {burn_multiple:.2f}x")
    print(f"Implied Series B Pre-Money Valuation (7.5x Current ARR): ${implied_pre_money:.2f}M\n")

    # ==========================================================================
    # 2. MULTI-ROUND CAP TABLE & TERM SHEET DILUTION ENGINE
    # ==========================================================================
    founders_shares = 7_000_000

    # Stage 1: Seed Round (YC Post-Money SAFE)
    # $3.0M raised on a $15.0M Post-Money Valuation Cap -> locks in 20.0% pre-Series A
    seed_investment = 3_000_000
    seed_post_cap = 15_000_000
    seed_target_ownership = seed_investment / seed_post_cap  # 20.0%

    # Stage 2: Series A Priced Round + Pre-Money Option Pool Shuffle
    # $32.0M Pre-Money, $8.0M Investment -> $40.0M Post-Money (20.0% Series A)
    # Unallocated ESOP set to 10.0% post-Series A on a pre-money basis
    series_a_pre = 32_000_000
    series_a_inv = 8_000_000
    series_a_post = series_a_pre + series_a_inv
    series_a_ownership = series_a_inv / series_a_post
    esop_a_target_post = 0.10

    seed_shares = int(round(founders_shares * (seed_target_ownership / (1.0 - seed_target_ownership))))
    pre_pool_shares = founders_shares + seed_shares
    post_a_total_shares = int(round(pre_pool_shares / (1.0 - series_a_ownership - esop_a_target_post)))
    esop_a_shares = int(round(post_a_total_shares * esop_a_target_post))
    series_a_shares = int(round(post_a_total_shares * series_a_ownership))
    series_a_pps = series_a_pre / (pre_pool_shares + esop_a_shares)
    seed_effective_pps = seed_investment / seed_shares

    # Stage 3: Series B Priced Round + Pre-Money Option Pool Top-Up
    # $90.0M Pre-Money, $30.0M Investment -> $120.0M Post-Money (25.0% Series B)
    # Total ESOP topped up to 12.5% post-Series B on a pre-money basis
    series_b_pre = 90_000_000
    series_b_inv = 30_000_000
    series_b_post = series_b_pre + series_b_inv
    series_b_ownership = series_b_inv / series_b_post
    esop_b_target_post = 0.125

    non_esop_pre_b = founders_shares + seed_shares + series_a_shares
    post_b_total_shares = int(round(non_esop_pre_b / (1.0 - series_b_ownership - esop_b_target_post)))
    esop_b_total_shares = int(round(post_b_total_shares * esop_b_target_post))
    series_b_shares = int(round(post_b_total_shares * series_b_ownership))
    series_b_pps = series_b_pre / (non_esop_pre_b + esop_b_total_shares)

    cap_table = pd.DataFrame([
        {
            "Stakeholder": "Founders (Common)",
            "Security_Type": "Common Stock",
            "Shares": founders_shares,
            "Invested_Capital": 0.0,
            "Issue_PPS": 0.00,
            "Post_A_Pct": founders_shares / post_a_total_shares,
            "Post_B_Pct": founders_shares / post_b_total_shares,
        },
        {
            "Stakeholder": "Employee Option Pool (ESOP)",
            "Security_Type": "Common Options",
            "Shares": esop_b_total_shares,
            "Invested_Capital": 0.0,
            "Issue_PPS": 0.00,
            "Post_A_Pct": esop_a_shares / post_a_total_shares,
            "Post_B_Pct": esop_b_total_shares / post_b_total_shares,
        },
        {
            "Stakeholder": "Seed Investors (Post-Money SAFE)",
            "Security_Type": "Series Seed Preferred",
            "Shares": seed_shares,
            "Invested_Capital": seed_investment,
            "Issue_PPS": seed_effective_pps,
            "Post_A_Pct": seed_shares / post_a_total_shares,
            "Post_B_Pct": seed_shares / post_b_total_shares,
        },
        {
            "Stakeholder": "Series A Investors",
            "Security_Type": "Series A Preferred",
            "Shares": series_a_shares,
            "Invested_Capital": series_a_inv,
            "Issue_PPS": series_a_pps,
            "Post_A_Pct": series_a_shares / post_a_total_shares,
            "Post_B_Pct": series_a_shares / post_b_total_shares,
        },
        {
            "Stakeholder": "Series B Investors",
            "Security_Type": "Series B Preferred",
            "Shares": series_b_shares,
            "Invested_Capital": series_b_inv,
            "Issue_PPS": series_b_pps,
            "Post_A_Pct": 0.0,
            "Post_B_Pct": series_b_shares / post_b_total_shares,
        },
    ])

    print("=== [PART 2] POST-SERIES B FULLY DILUTED CAP TABLE ===")
    print(f"Series A PPS: ${series_a_pps:.2f} | Series B PPS: ${series_b_pps:.2f} | Post-B Shares: {post_b_total_shares:,}")
    display_cap = cap_table.copy()
    display_cap["Shares"] = display_cap["Shares"].map(lambda x: f"{x:,}")
    display_cap["Invested_Capital"] = display_cap["Invested_Capital"].map(lambda x: f"${x/1e6:,.2f}M")
    display_cap["Issue_PPS"] = display_cap["Issue_PPS"].map(lambda x: f"${x:,.2f}" if x > 0 else "-")
    display_cap["Post_A_Pct"] = display_cap["Post_A_Pct"].map(lambda x: f"{x:.2%}")
    display_cap["Post_B_Pct"] = display_cap["Post_B_Pct"].map(lambda x: f"{x:.2%}")
    print(display_cap.to_string(index=False))

    # ==========================================================================
    # 3. EXIT WATERFALL & LIQUIDATION PREFERENCE ENGINE (NASH CONVERSION)
    # ==========================================================================
    # Tier 1 (Senior): Series B Preferred ($30.0M 1.0x Liq Pref, Participating up to 3.0x = $90.0M Cap)
    # Tier 2 (Junior Preferred, Pari Passu): Series A ($8.0M 1.0x Non-Part) & Seed ($3.0M 1.0x Non-Part)
    # Tier 3: Common Stock (Founders + ESOP + Converted Preferred Classes)
    exit_valuations = [25_000_000, 60_000_000, 150_000_000, 400_000_000]
    waterfall_rows = []

    for exit_val in exit_valuations:
        all_states = {}
        for conv_b in [False, True]:
            for conv_a in [False, True]:
                for conv_seed in [False, True]:
                    rem = exit_val
                    pay_b, pay_a, pay_seed = 0.0, 0.0, 0.0

                    # Tier 1: Series B Liquidation Preference
                    if not conv_b:
                        pref_b = min(rem, series_b_inv * 1.0)
                        pay_b += pref_b
                        rem -= pref_b

                    # Tier 2: Series A & Seed Pari Passu Liquidation Preference
                    tier2_claims = {}
                    if not conv_a:
                        tier2_claims["A"] = series_a_inv * 1.0
                    if not conv_seed:
                        tier2_claims["Seed"] = seed_investment * 1.0

                    total_tier2 = sum(tier2_claims.values())
                    if total_tier2 > 0 and rem > 0:
                        alloc = min(rem, total_tier2)
                        if "A" in tier2_claims:
                            pay_a += alloc * (tier2_claims["A"] / total_tier2)
                        if "Seed" in tier2_claims:
                            pay_seed += alloc * (tier2_claims["Seed"] / total_tier2)
                        rem -= alloc

                    # Tier 3: Common Residual & Series B Participation (capped at 3.0x = $90M)
                    common_shares_pool = founders_shares + esop_b_total_shares
                    if conv_b:
                        common_shares_pool += series_b_shares
                    if conv_a:
                        common_shares_pool += series_a_shares
                    if conv_seed:
                        common_shares_pool += seed_shares

                    if rem > 0:
                        if not conv_b:
                            part_shares_pool = common_shares_pool + series_b_shares
                            b_part_share = series_b_shares / part_shares_pool
                            max_b_part = max(0.0, (series_b_inv * 3.0) - pay_b)
                            potential_b_part = rem * b_part_share
                            if potential_b_part <= max_b_part:
                                pay_b += potential_b_part
                                rem -= potential_b_part
                            else:
                                pay_b += max_b_part
                                rem -= max_b_part

                        pay_founders = rem * (founders_shares / common_shares_pool)
                        pay_esop = rem * (esop_b_total_shares / common_shares_pool)
                        if conv_b:
                            pay_b += rem * (series_b_shares / common_shares_pool)
                        if conv_a:
                            pay_a += rem * (series_a_shares / common_shares_pool)
                        if conv_seed:
                            pay_seed += rem * (seed_shares / common_shares_pool)
                    else:
                        pay_founders = 0.0
                        pay_esop = 0.0

                    all_states[(conv_b, conv_a, conv_seed)] = {
                        "B": pay_b,
                        "A": pay_a,
                        "Seed": pay_seed,
                        "Founders": pay_founders,
                        "ESOP": pay_esop,
                        "conv": (conv_b, conv_a, conv_seed),
                    }

        # Solve for Nash Equilibrium conversion outcome across investor classes
        eq_state = None
        for state, p in all_states.items():
            cb, ca, cs = state
            b_ok = p["B"] >= all_states[(not cb, ca, cs)]["B"] - 1e-6
            a_ok = p["A"] >= all_states[(cb, not ca, cs)]["A"] - 1e-6
            s_ok = p["Seed"] >= all_states[(cb, ca, not cs)]["Seed"] - 1e-6
            if b_ok and a_ok and s_ok:
                eq_state = p
                break

        b_moic = eq_state["B"] / series_b_inv
        a_moic = eq_state["A"] / series_a_inv
        seed_moic = eq_state["Seed"] / seed_investment

        waterfall_rows.append({
            "Exit_Val": f"${exit_val/1e6:,.0f}M",
            "Series_B": f"${eq_state['B']/1e6:,.2f}M ({b_moic:.2f}x)",
            "Series_A": f"${eq_state['A']/1e6:,.2f}M ({a_moic:.2f}x)",
            "Seed_SAFE": f"${eq_state['Seed']/1e6:,.2f}M ({seed_moic:.2f}x)",
            "Founders": f"${eq_state['Founders']/1e6:,.2f}M",
            "ESOP": f"${eq_state['ESOP']/1e6:,.2f}M",
            "Conversion_Outcome": (
                f"B:{'Conv' if eq_state['conv'][0] else 'Pref'} | "
                f"A:{'Conv' if eq_state['conv'][1] else 'Pref'} | "
                f"Seed:{'Conv' if eq_state['conv'][2] else 'Pref'}"
            ),
        })

    print("\n=== [PART 3] EXIT WATERFALL & CONVERSION EQUILIBRIUM MATRIX ===")
    wf_df = pd.DataFrame(waterfall_rows)
    print(wf_df.to_string(index=False))

    # ==========================================================================
    # 4. VENTURE CAPITAL FUND ECONOMICS & CARRY WATERFALL (2/20 FUND MODEL)
    # ==========================================================================
    fund = {
        "committed_capital": 200.0,   # $M
        "mgmt_fee_inv_period": 0.02,  # 2.0% yrs 1-5 ($20.0M)
        "mgmt_fee_harvest": 0.015,    # 1.5% step-down yrs 6-10 ($15.0M)
        "org_expenses": 1.0,          # $1.0M
        "carry_rate": 0.20,           # 20% Carried Interest
        "hurdle_rate": 0.08,          # 8% Compounded Preferred Return
        "avg_hold_years": 5.5,
    }

    total_fees_exp = (
        (fund["committed_capital"] * fund["mgmt_fee_inv_period"] * 5.0)
        + (fund["committed_capital"] * fund["mgmt_fee_harvest"] * 5.0)
        + fund["org_expenses"]
    )
    investable_capital = fund["committed_capital"] - total_fees_exp

    realized_proceeds = 340.0
    unrealized_nav = 135.0
    gross_portfolio_value = realized_proceeds + unrealized_nav

    gross_moic = gross_portfolio_value / investable_capital
    gross_tvpi = gross_portfolio_value / fund["committed_capital"]
    dpi_pre_carry = realized_proceeds / fund["committed_capital"]
    rvpi = unrealized_nav / fund["committed_capital"]

    hurdle_target = fund["committed_capital"] * ((1.0 + fund["hurdle_rate"]) ** fund["avg_hold_years"])
    total_profit_above_committed = max(0.0, gross_portfolio_value - fund["committed_capital"])

    if gross_portfolio_value > hurdle_target:
        gp_carry = total_profit_above_committed * fund["carry_rate"]
    else:
        gp_carry = 0.0

    lp_net_value = gross_portfolio_value - gp_carry
    net_tvpi = lp_net_value / fund["committed_capital"]
    net_irr_approx = (net_tvpi ** (1.0 / fund["avg_hold_years"])) - 1.0

    print("\n=== [PART 4] VC FUND ECONOMICS & EUROPEAN CARRY WATERFALL ($200M FUND) ===")
    print(f"Committed Capital: ${fund['committed_capital']:.1f}M | Lifetime Fees & Exp: ${total_fees_exp:.1f}M | Investable Capital: ${investable_capital:.1f}M")
    print(f"Realized Proceeds: ${realized_proceeds:.1f}M | Unrealized NAV: ${unrealized_nav:.1f}M | Gross Portfolio Value: ${gross_portfolio_value:.1f}M")
    print(f"Gross MOIC (on Invested): {gross_moic:.2f}x | Gross TVPI (on Committed): {gross_tvpi:.2f}x")
    print(f"DPI (Realized): {dpi_pre_carry:.2f}x | RVPI (Unrealized): {rvpi:.2f}x")
    print(f"Hurdle Target (8% Compounded): ${hurdle_target:.2f}M -> Hurdle Cleared: {'YES' if gross_portfolio_value > hurdle_target else 'NO'}")
    print(f"GP Carried Interest (20%): ${gp_carry:.2f}M | LP Net TVPI: {net_tvpi:.2f}x | Implied LP Net IRR: {net_irr_approx:.2%}")
    print("=" * 94)


if __name__ == "__main__":
    run_vc_model()
