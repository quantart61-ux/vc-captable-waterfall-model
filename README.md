# Venture Capital Cap Table, Term Sheet Waterfall & Fund Economics Model

An institutional-grade Venture Capital modeling and term sheet analysis engine implemented in Python. Built to evaluate **Startup Unit Economics & SaaS Valuation**, **Multi-Round Cap Table Dilution** (YC Post-Money SAFE conversion and Pre-Money Option Pool Shuffles), **Liquidation Preference Waterfalls** (solving for rational Nash conversion thresholds across Senior/Junior Preferred classes), and **2/20 VC Fund Economics** (Gross vs. Net TVPI, DPI, RVPI, and European Carried Interest waterfalls).

---

## 1. Executive Summary & Case Study Parameters

The model evaluates **Vanguard Cloud Analytics Inc.**, a representative Series B B2B AI Infrastructure & Data Observability SaaS company raising **$30.0M** at a **$90.0M Pre-Money Valuation** (**$120.0M Post-Money**).

### Core Analytical Outputs
- **SaaS Unit Economics & Pricing:** **$12.0M Current ARR** ($20.0M NTM ARR, **85% YoY growth**), **78% Gross Margin**, **124% Net Dollar Retention (NDR)**, **4.8x LTV/CAC**, **53.0% Rule of 40**, and a **0.82x Burn Multiple** (20.0 months cash runway), supporting a **7.5x Current ARR** ($90.0M) pre-money valuation.
- **Cap Table & Dilution Mechanics:** Tracks ownership from Founding (`7.00M` shares) through a **$3.0M YC Post-Money SAFE** ($15.0M cap $\rightarrow$ 20.0% pre-Series A ownership), a **$40.0M Post-Money Series A** ($3.20/share with a 10.0% pre-money ESOP shuffle), and a **$120.0M Post-Money Series B** ($6.67/share with a 12.5% pre-money ESOP top-up), diluting Founders to **38.89%** across **18,000,000** fully diluted shares.
- **Exit Waterfall & Conversion Equilibria:** Models Senior Series B **1.0x Participating Preferred (3.0x cap)** stacked above *pari passu* Series A and Seed **1.0x Non-Participating Preferred**. At a **$150M exit**, Series A and Seed rationally convert to Common (`$16.67M` / `2.08x` and `$11.67M` / `3.89x`) while Series B remains Preferred to capture participation (`$60.00M` / `2.00x`); at a **$400M IPO exit**, Series B converts to Common (`$100.00M` / `3.33x`) to exceed its `$90.0M` participation cap.
- **VC Fund Economics ($200M Fund III):** Deducts **$36.0M** in lifetime management fees (2.0% investment period / 1.5% harvest step-down) and org expenses to yield **$164.0M Investable Capital**. Across **$475.0M** in gross portfolio value (`$340.0M` realized + `$135.0M` NAV), the fund achieves **2.90x Gross MOIC**, **2.38x Gross TVPI**, **1.70x DPI**, **$55.00M GP Carry** (clearing the 8% compounded hurdle), **2.10x LP Net TVPI**, and **14.44% LP Net IRR**.

---

## 2. Startup Unit Economics & Multi-Round Cap Table

### Key Venture Formulas
1. **Burn Multiple:**
   $$\text{Burn Multiple} = \frac{\text{Net Burn}}{\text{Net New ARR}}$$
2. **YC Post-Money SAFE Ownership:**
   $$\text{SAFE Ownership \%} = \frac{\text{Investment Amount}}{\text{Post-Money Valuation Cap}}$$
3. **Pre-Money Option Pool Shuffle Share Price:**
   $$\text{Issue PPS} = \frac{\text{Pre-Money Valuation}}{\text{Pre-Round Shares} + \text{New ESOP Top-Up Shares}}$$

### Post-Series B Fully Diluted Cap Table (`18,000,000` Total Shares)

| Stakeholder | Security Type | Fully Diluted Shares | Invested Capital | Issue PPS | Post-Series A % | Post-Series B % |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Founders (Common)** | Common Stock | 7,000,000 | $0.00M | — | 56.00% | **38.89%** |
| **Employee Option Pool (ESOP)** | Common Options | 2,250,000 | $0.00M | — | 10.00% | **12.50%** |
| **Seed Investors (Post-Money SAFE)** | Series Seed Preferred | 1,750,000 | $3.00M | $1.71 | 14.00% | **9.72%** |
| **Series A Investors** | Series A Preferred | 2,500,000 | $8.00M | $3.20 | 20.00% | **13.89%** |
| **Series B Investors** | Series B Preferred | 4,500,000 | $30.00M | $6.67 | 0.00% | **25.00%** |

---

## 3. Exit Waterfall & Liquidation Preference Matrix

### Seniority & Conversion Rules
- **Tier 1 (Senior):** Series B Preferred ($30.0M invested) holds **1.0x Senior Liquidation Preference** with **Participation up to a 3.0x cap** ($90.0M).
- **Tier 2 (Junior Preferred, *Pari Passu*):** Series A ($8.0M) and Series Seed ($3.0M) hold **1.0x Non-Participating Liquidation Preferences** subordinate to Series B.
- **Nash Conversion Equilibrium:** Each preferred class independently elects to convert to Common Stock if and only if its pro-rata Common payout strictly exceeds its Preferred waterfall payout.

| Exit Valuation | Series B Payout (MOIC) | Series A Payout (MOIC) | Seed SAFE Payout (MOIC) | Founders Payout | ESOP Payout | Equilibrium Conversion State |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **$25M (Distressed)** | **$25.00M** (0.83x) | $0.00M (0.00x) | $0.00M (0.00x) | $0.00M | $0.00M | `B:Pref \| A:Pref \| Seed:Pref` |
| **$60M (Modest M&A)** | **$36.22M** (1.21x) | $8.00M (1.00x) | $3.00M (1.00x) | $9.67M | $3.11M | `B:Pref \| A:Pref \| Seed:Pref` |
| **$150M (Base Growth)** | **$60.00M** (2.00x) | $16.67M (2.08x) | $11.67M (3.89x) | $46.67M | $15.00M | `B:Pref \| A:Conv \| Seed:Conv` |
| **$400M (IPO Breakout)** | **$100.00M** (3.33x) | $55.56M (6.94x) | $38.89M (12.96x) | $155.56M | $50.00M | `B:Conv \| A:Conv \| Seed:Conv` |

---

## 4. VC Fund Economics & European Carry Waterfall ($200.0M Fund)

| Fund Metric | Value | Analytical Definition |
| :--- | :---: | :--- |
| **Committed Capital** | $200.0M | Total LP capital commitments across 10-year fund life |
| **Lifetime Fees & Org Expenses** | $36.0M | 2.0% yrs 1–5 ($20M) + 1.5% yrs 6–10 ($15M) + $1M setup |
| **Investable Capital** | $164.0M | Net capital deployed into portfolio companies |
| **Gross Portfolio Value** | $475.0M | $340.0M Realized Proceeds + $135.0M Unrealized NAV |
| **Gross MOIC / Gross TVPI** | **2.90x / 2.38x** | Gross MOIC on Investable Capital ($164M); TVPI on Committed ($200M) |
| **DPI / RVPI (Pre-Carry)** | **1.70x / 0.68x** | Distributed to Paid-In ($340M / $200M) + Residual Value ($135M / $200M) |
| **8.0% Compounded Hurdle** | $305.39M | Cleared (`$475.0M > $305.39M` over 5.5-year avg hold) |
| **GP Carried Interest (20%)** | **$55.00M** | $20\% \times (\$475.0\text{M} - \$200.0\text{M})$ under European whole-fund waterfall |
| **LP Net TVPI / Net IRR** | **2.10x / 14.44%** | Net LP value ($420.0M / $200.0M) and implied annualized net return |

---

## 5. Quantitative Venture Capital & Term Sheet Audit Rubric

Six verification guardrails codified to audit VC deal structuring and LLM-generated venture analyses:

| Audit Dimension | Common Analytical Failure Mode | Enforced Verification Rule |
| :--- | :--- | :--- |
| **Pre-Money Option Pool Shuffle** | Calculating new ESOP expansion on a post-money basis, unfairly diluting incoming Series A/B investors. | Expand unallocated ESOP inside the **Pre-Money Valuation** so existing shareholders absorb 100% of pool dilution. |
| **Post-Money vs. Pre-Money SAFE** | Treating a YC Post-Money SAFE like a Pre-Money SAFE and diluting SAFE holders with subsequent SAFE issuances. | Lock in $\text{Ownership} = \frac{\text{Investment}}{\text{Post-Money Cap}}$ prior to new priced-round dilution. |
| **Participating Preferred Cap** | Allowing Participating Preferred investors to double-dip indefinitely past their participation cap without converting. | Enforce $\min(\text{Pref} + \text{Pro-Rata}, \text{Cap})$ and switch to Common conversion once Common payout exceeds the cap. |
| **Multi-Class Conversion Coupling** | Evaluating one investor's conversion threshold assuming other preferred classes remain unconverted when they would rationally convert. | Solve simultaneously across all classes for the **Nash Equilibrium** common share denominator. |
| **Gross MOIC vs. Net TVPI Basis** | Dividing gross portfolio proceeds by Committed Capital instead of Investable Capital (or forgetting fee drag in LP Net TVPI). | Compute **Gross MOIC** on Investable Capital ($164M) and **TVPI / DPI / Net IRR** on Committed Capital ($200M). |
| **European vs. American Carry** | Paying GP carried interest on early profitable exits before LPs recover 100% of total fund Committed Capital + Hurdle. | Apply **European Whole-Fund Waterfall**: return Committed Capital + 8% hurdle prior to distributing 20% carry. |

---

## 6. How to Run

```bash
pip install -r requirements.txt
python vc_captable_waterfall_model.py
```
