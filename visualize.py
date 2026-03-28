import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---------------------- READ AND SORT DATA ------------------------

price_day1 = pd.read_csv("prices_round_0_day_-1.csv", sep=';').sort_values("timestamp")
trades_day1 = pd.read_csv("trades_round_0_day_-1.csv", sep=';').sort_values("timestamp")
price_day2 = pd.read_csv("prices_round_0_day_-2.csv", sep=';').sort_values("timestamp")
trades_day2 = pd.read_csv("trades_round_0_day_-2.csv", sep=';').sort_values("timestamp")

# ---------------------- VERIFY PRODUCT NAMES ------------------------

TOMATO_NAME  = price_day1['product'].unique()[0]
EMERALD_NAME = price_day1['product'].unique()[1] 

# ---------------------- SPLIT PRICE DATA (FULL ORDER BOOK) ------------------------
# Keep price data separate and complete 
# This is used for spread analysis, model estimation, and mid price plots

tomato_price1  = price_day1[price_day1['product'] == "TOMATOES"].copy().reset_index(drop=True)
emerald_price1 = price_day1[price_day1['product'] == "EMERALDS"].copy().reset_index(drop=True)
tomato_price2  = price_day2[price_day2['product'] == "TOMATOES"].copy().reset_index(drop=True)
emerald_price2 = price_day2[price_day2['product'] == "EMERALDS"].copy().reset_index(drop=True)

for df in [tomato_price1, emerald_price1, tomato_price2, emerald_price2]:
    df['spread_1'] = df['ask_price_1'] - df['bid_price_1']
    df['spread_2'] = df['ask_price_2'] - df['bid_price_2']

# ---------------------- MERGE TRADES ONTO ORDER BOOK ------------------------
# merge_asof: for each TRADE, attach the most recent ORDER BOOK snapshot
# This gives every trade its contemporaneous book state — no stale forward-fill across all rows

tomato_trades1  = trades_day1[trades_day1['symbol'] == "TOMATOES"].copy().reset_index(drop=True)
emerald_trades1 = trades_day1[trades_day1['symbol'] == "EMERALDS"].copy().reset_index(drop=True)
tomato_trades2  = trades_day2[trades_day2['symbol'] == "TOMATOES"].copy().reset_index(drop=True)
emerald_trades2 = trades_day2[trades_day2['symbol'] == "EMERALDS"].copy().reset_index(drop=True)

def attach_book(trades_df, price_df):
    """Attach the most recent order book snapshot to each trade row."""
    return pd.merge_asof(
        trades_df.sort_values('timestamp'),
        price_df.sort_values('timestamp'),
        on='timestamp',
        direction='backward' 
    )

tomato_exec1  = attach_book(tomato_trades1,  tomato_price1)
emerald_exec1 = attach_book(emerald_trades1, emerald_price1)
tomato_exec2  = attach_book(tomato_trades2,  tomato_price2)
emerald_exec2 = attach_book(emerald_trades2, emerald_price2)

# ---------------------- MID PRICE + EXECUTED TRADES PLOT ------------------------
# Use full price data for the line, and trades_df for scatter points
# scatter uses raw trade timestamps/prices — no merge needed for plotting

def plot_midprice_with_trades(price_df, trades_df, title, ax, ylim=None):
    ax.plot(price_df['timestamp'], price_df['mid_price'],
            color='steelblue', linewidth=0.8, label='Mid Price')
    ax.scatter(trades_df['timestamp'], trades_df['price'],
               color='red', s=10, label='Executed Trades', zorder=2, alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Price')
    ax.legend()
    if ylim:
        ax.set_ylim(ylim)

fig, axes = plt.subplots(2, 1, figsize=(14, 6))
plot_midprice_with_trades(tomato_price1,  tomato_trades1,
                            'TOMATO Mid Price (Day 1)',  axes[0], ylim=(4940, 5011))
plot_midprice_with_trades(emerald_price1, emerald_trades1,
                           'EMERALD Mid Price (Day 1)', axes[1], ylim=(9990, 10010))
plt.tight_layout()
plt.savefig("midprice_plot1.png")
plt.close()

fig, axes = plt.subplots(2, 1, figsize=(14, 6))
plot_midprice_with_trades(tomato_price2,  tomato_trades2,
                            'TOMATO Mid Price (Day 2)',  axes[0], ylim=(4980, 5040))
plot_midprice_with_trades(emerald_price2, emerald_trades2,
                           'EMERALD Mid Price (Day 2)', axes[1], ylim=(9990, 10010))
plt.tight_layout()
plt.savefig("midprice_plot2.png")
plt.close()

# ---------------------- BID-ASK SPREAD (FULL PRICE BOOK) ------------------------

fig, axes = plt.subplots(2, 1, figsize=(14, 6))
axes[0].plot(tomato_price1['timestamp'], tomato_price1['spread_1'],
             label='Spread Level 1 (Best)', color='blue', alpha=0.8)
axes[0].plot(tomato_price1['timestamp'], tomato_price1['spread_2'],
             label='Spread Level 2', color='orange', alpha=0.6)
axes[0].set_title('TOMATO Spread — Both Levels (Day 1)')
axes[0].legend()

axes[1].plot(emerald_price1['timestamp'], emerald_price1['spread_1'],
             label='Spread Level 1 (Best)', color='blue', alpha=0.8)
axes[1].plot(emerald_price1['timestamp'], emerald_price1['spread_2'],
             label='Spread Level 2', color='orange', alpha=0.6)
axes[1].set_title('EMERALD Spread — Both Levels (Day 1)')
axes[1].legend()

plt.tight_layout()
plt.savefig("spread.png")
plt.close()

# ---------------------- SPREAD GROUP SCATTER (FULL PRICE BOOK) ------------------------

# TOMATO, Spread Level 1 — threshold at 13
fig, ax = plt.subplots(figsize=(14, 5))
low  = tomato_price1[tomato_price1['spread_1'] < 13]
high = tomato_price1[tomato_price1['spread_1'] >= 13]
ax.scatter(low['timestamp'],  low['mid_price'],  color='steelblue',
            alpha=0.5, s=10, label='Spread < 13')
ax.scatter(high['timestamp'], high['mid_price'], color='tomato',
            alpha=0.5, s=10, label='Spread >= 13')
ax.set_title('TOMATO Mid Price by Spread Group (Day 1)')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Mid Price')
ax.legend()
plt.tight_layout()
plt.savefig("tomato_spread_scatter.png")
plt.close()

# EMERALD, Spread Level 1 — two-state: 8 or 16
fig, ax = plt.subplots(figsize=(14, 5))
spread8  = emerald_price1[emerald_price1['spread_1'] == 8]
spread16 = emerald_price1[emerald_price1['spread_1'] == 16]
ax.scatter(spread8['timestamp'],  spread8['mid_price'],  color='steelblue',
            alpha=0.5, s=10, label='Spread = 8')
ax.scatter(spread16['timestamp'], spread16['mid_price'], color='tomato',
            alpha=0.5, s=10, label='Spread = 16')
ax.set_ylim(9990, 10010)  
ax.set_title('EMERALD Mid Price by Spread Group (Day 1)')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Mid Price')
ax.legend()
plt.tight_layout()
plt.savefig("emerald_spread_scatter.png")
plt.close()

# ---------------------- EXECUTION ZONE CLASSIFICATION ------------------------
# Apply ONLY to actual trade rows (exec dataframes)

def classify_execution(row):
    p = row['price']
    if pd.isna(p):
        return 'No Trade'
    elif p >= row['ask_price_2']:
        return 'Zone C - Hit L2 Ask'
    elif p >= row['ask_price_1']:
        return 'Zone A - Hit L1 Ask'
    elif p <= row['bid_price_2']:
        return 'Zone D - Hit L2 Bid'
    elif p <= row['bid_price_1']:
        return 'Zone B - Hit L1 Bid'
    else:
        return 'Zone E - Inside Spread'

tomato_exec1['execution_zone']  = tomato_exec1.apply(classify_execution, axis=1)
emerald_exec1['execution_zone'] = emerald_exec1.apply(classify_execution, axis=1)

# Tag with product name for groupby (symbol column from trades side)
tomato_exec1['product_label']  = "TOMATOES"
emerald_exec1['product_label'] = "EMERALDS"

combined_exec1 = pd.concat([tomato_exec1, emerald_exec1], ignore_index=True)

# Zone distribution — count and mean price per zone per product
print("\n=== Execution Zone Distribution ===")
print(combined_exec1.groupby(['product_label', 'execution_zone'])['price'].agg(['count', 'mean']))

# Zone as % of total trades per product
print("\n=== Execution Zone as % of Trades ===")
print(combined_exec1.groupby(['product_label', 'execution_zone']).size()
      .groupby(level=0).transform(lambda x: x / x.sum() * 100)
      .reset_index(name='pct'))

# ---------------------- TOMATO OPTIMAL QUANTITY ------------------------
print("Tomato Bid Volume: ", tomato_price1['bid_volume_1'].describe())
print("Tomato Ask Volume: ", tomato_price1['ask_volume_1'].describe())
print("Tomato Executed Quantity: ", tomato_exec1['quantity'].describe())

# ---------------------- TOMATO MODEL: OU PARAMETER ESTIMATION ------------------------
# dS_t = θ(μ - S_t)dt + σdB_t -> S(t+1) = θμ + (1 - θ)S(t) + σε(t)
# S(t+1) is in the form of S(t+1) = a + b·S(t) + ε(t), 
S = tomato_price1['mid_price'].dropna()
S_t  = S[:-1] # input
S_t1 = S[1:] # predicted output

b, a = np.polyfit(S_t, S_t1, 1)   # returns [slope, intercept]

print(f"a (intercept): {a:.4f}")
print(f"b (slope):     {b:.4f}")

# θ = 1 - b
theta = 1 - b

# μ = a / θ
mu = a / theta

# σ = std of residuals
residuals = S_t1 - (a + b * S_t)
sigma = np.std(residuals)

# Half-life = how long until deviation is 50% corrected
half_life = np.log(2) / theta

print(f"\n=== OU Parameters ===")
print(f"  theta (reversion speed): {theta:.4f}")
print(f"  mu (long-run mean):   {mu:.4f}")
print(f"  sigma (volatility):      {sigma:.4f}")
print(f"  half-life:           {half_life:.1f} timestamps")

S0        = tomato_price1['mid_price'].iloc[0]   # start at real Day 1 price
N         = len(tomato_price1)                    # same length as real data
dt        = 1                                     # one timestamp per step
n_paths   = 5                                     # simulate multiple paths

# ── Simulate OU paths ────────────────────────────────────────
np.random.seed(42)
real_price = tomato_price1['mid_price'].values
timestamps = tomato_price1['timestamp'].values

fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# ── Plot 1: Real vs Simulated paths ─────────────────────────
axes[0].plot(timestamps, real_price,
             color='black', linewidth=0.8, label='Real TOMATO', zorder=3)

for i in range(n_paths):
    S_sim = np.zeros(N)
    S_sim[0] = S0
    for t in range(1, N):
        dS = theta * (mu - S_sim[t-1]) * dt + sigma * np.random.randn()
        S_sim[t] = S_sim[t-1] + dS
    axes[0].plot(timestamps, S_sim,
                 alpha=0.4, linewidth=0.6, label=f'Sim path {i+1}')

axes[0].axhline(mu, color='red', linestyle='--', linewidth=1,
                alpha=0.7, label=f'mu = {mu:.1f}')
axes[0].set_title('Real TOMATO vs OU Simulated Paths')
axes[0].set_ylabel('Price')
axes[0].legend(fontsize=8)

# ── Plot 2: Mean reversion force at each timestamp ───────────
# Shows the "pull" term: theta * (mu - S_t)
real_price_series = tomato_price1['mid_price']
reversion_force   = theta * (mu - real_price_series)

axes[1].plot(timestamps, reversion_force,
             color='steelblue', linewidth=0.8)
axes[1].axhline(0, color='red', linestyle='--', linewidth=0.8)
axes[1].fill_between(timestamps, reversion_force, 0,
                     where=(reversion_force > 0),
                     alpha=0.3, color='green', label='Pull up (buy signal)')
axes[1].fill_between(timestamps, reversion_force, 0,
                     where=(reversion_force < 0),
                     alpha=0.3, color='red', label='Pull down (sell signal)')
axes[1].set_title('Mean Reversion Force: theta x (mu - S_t)')
axes[1].set_ylabel('Force magnitude')
axes[1].legend(fontsize=8)

# ── Plot 3: Residual distribution ───────────────────────────
S     = real_price_series.values
S_t   = S[:-1]
S_t1  = S[1:]
b, a  = np.polyfit(S_t, S_t1, 1)
residuals = S_t1 - (a + b * S_t)

axes[2].hist(residuals, bins=60, color='steelblue',
             edgecolor='none', alpha=0.8)
axes[2].axvline(0, color='red', linestyle='--', linewidth=1)
axes[2].set_title('Residual Distribution — should be bell-shaped')
axes[2].set_xlabel('Residual')
axes[2].set_ylabel('Count')

plt.tight_layout()
plt.savefig('ou_full_plot.png')

# ---------------------- EMERALD MODEL: MARKOV TRANSITION MATRIX ------------------------
