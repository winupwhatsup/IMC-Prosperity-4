# IMC Prosperity 4 — Tutorial Round

Quantitative research and strategy development for IMC Prosperity 4, an algorithmic trading competition. This repository covers the full research pipeline from exploratory data analysis to statistical model estimation for two products: **TOMATOES** and **EMERALDS**.

---

## Repository Structure

```
├── visualize.py                  # Main analysis script
├── prices_round_0_day_-1.csv     # Order book snapshots — Day 1
├── prices_round_0_day_-2.csv     # Order book snapshots — Day 2
├── trades_round_0_day_-1.csv     # Executed trades — Day 1
├── trades_round_0_day_-2.csv     # Executed trades — Day 2
└── README.md
```

---

## Products

| Product | Price Level | Behavior | Strategy Class |
|---|---|---|---|
| TOMATOES | ~4,950–5,010 | Mean-reverting with negative drift | OU Process + directional sizing |
| EMERALDS | ~10,000 (fixed) | Two-state spread (8 or 16) | Markov Chain market making |

---

## Analysis Pipeline (`visualize.py`)

### 1. Data Loading and Merging
Reads all four CSV datasets (semicolon-delimited) and sorts by timestamp. Uses `merge_asof` to attach the most recent order book snapshot to each executed trade — ensuring every trade has its correct contemporaneous book state without stale forward-fills.

### 2. Mid Price + Executed Trades
Plots the order book mid price across all timestamps for both products on both days, with executed trade prices overlaid as scatter points. Used to identify price behavior regimes visually — TOMATOES shows a mean-reverting oscillation with downward drift; EMERALDS sits at a near-constant 10,000.

### 3. Bid-Ask Spread Analysis
Plots Level 1 and Level 2 bid-ask spreads over time per product. Key findings:
- **TOMATOES**: Spread oscillates between 6–14, resting at 13–14. Narrow spread (< 13) clusters at local price extremes — used as a directional conviction signal.
- **EMERALDS**: Spread is a two-state system switching between exactly 8 (narrow) and 16 (wide), driven by a single automated market maker.

### 4. Execution Zone Classification
Classifies each executed trade into one of five zones relative to the order book:
- Zone A: Hit L1 Ask (aggressive buyer)
- Zone B: Hit L1 Bid (aggressive seller)
- Zone C: Hit L2 Ask (walked up past L1)
- Zone D: Hit L2 Bid (walked down past L1)
- Zone E: Inside spread (anomaly)

Result: 100% of trades in both products hit L1 only — L2 quotes are never consumed.

### 5. Optimal Sizing
Determines trade size (2–4 units) based on spread width at each timestamp — no fair value estimation required:

| Spread | Signal | Size |
|---|---|---|
| ≥ 13 | Passive, no conviction | 2 |
| 10–12 | Moderate compression | 3 |
| ≤ 9 | High conviction extreme | 4 |

### 6. TOMATOES Model — Ornstein-Uhlenbeck Process
Models TOMATOES price dynamics as a continuous-time mean-reverting process:

```
dS_t = θ(μ - S_t)dt + σdB_t
```

Parameters estimated via AR(1) regression on the discretized form `S(t+1) = a + b·S(t) + ε(t)`:

| Parameter | Meaning | Estimated Value |
|---|---|---|
| θ | Mean reversion speed | 0.0043 |
| μ | Long-run fair value | 4976.43 |
| σ | Noise per timestamp | 0.0626 |
| t½ | Half-life (timestamps) | 161.3 |

Outputs three diagnostic plots: real vs simulated paths, mean reversion force over time, and residual distribution.

### 7. EMERALDS Model — Markov Transition Matrix
Models the spread state as a two-state Markov chain:

```
States: Wide (16) ↔ Narrow (8)
P(Wide → Narrow) = p
P(Narrow → Wide) = q
```

Estimated from empirical state transition frequencies on Day 1. Parameters p and q determine average time in each state and the stationary distribution — directly informing how aggressively to quote during wide vs narrow periods.

---

## Quoting Strategy Summary

**TOMATOES** — Hybrid market making with directional overlay:
- Post bid at `bid_price_1 + 1`, ask at `ask_price_1 - 1` (undercut L1 by 1 tick)
- At narrow spread extremes: suppress one side (don't buy at peaks, don't sell at troughs)
- Size by spread width: 2 / 3 / 4 units

**EMERALDS** — Pure market making against known fair value (10,000):
- Wide state (spread = 16): quote at 9,993 / 10,007 — undercut both sides by 1 tick, earn 14 ticks per round trip
- Narrow state (spread = 8): step back, do not quote

---

## Data Split

| Dataset | Role |
|---|---|
| Day 1 order book + trades | Model fitting and strategy design |
| Day 2 order book + trades | Backtesting and parameter validation |

---

## Next Steps

- [ ] Validate OU and Markov parameters on Day 2 — check stability across days
- [ ] Implement inventory skewing for TOMATOES to account for downward drift
- [ ] Backtest quoting strategy on Day 2 and compute realized P&L
- [ ] Compile full written analysis as PDF document
