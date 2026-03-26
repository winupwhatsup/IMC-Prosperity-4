import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

# ---------------------- READ AND SORT DATA ------------------------

# Read all 4 datasets and separate dataframe by ;
price_day1 = pd.read_csv("prices_round_0_day_-1.csv", sep=';')
trades_day1 = pd.read_csv("trades_round_0_day_-1.csv", sep=';')
price_day2 = pd.read_csv("prices_round_0_day_-2.csv", sep=';')
trades_day2 = pd.read_csv("trades_round_0_day_-2.csv", sep=';')

# Merge price and trade data on timestamp, then split by product
merged_day1 = pd.merge(price_day1, trades_day1, on='timestamp', how='inner', suffixes=('_price', '_trade'))
merged_day2 = pd.merge(price_day2, trades_day2, on='timestamp', how='inner', suffixes=('_price', '_trade'))

tomato_merged1 = merged_day1[merged_day1['product'] == 'TOMATOES'].reset_index(drop=True)
emerald_merged1 = merged_day1[merged_day1['product'] == 'EMERALDS'].reset_index(drop=True)
tomato_merged2 = merged_day2[merged_day2['product'] == 'TOMATOES'].reset_index(drop=True)
emerald_merged2 = merged_day2[merged_day2['product'] == 'EMERALDS'].reset_index(drop=True)

# ---------------------- MID-PRICE PLOT AND EXECUTED TRADE ------------------------

# Plot mid_price of Day 1 against timestamps with executed trades price
# Top Diagram is Tomato, Bottom Diagram is Emerald
fig, axes = plt.subplots(2, 1, figsize=(14, 6))
axes[0].plot(tomato_merged1['timestamp'], tomato_merged1['mid_price'])
axes[0].scatter(tomato_merged1['timestamp'], tomato_merged1['price'],
                color='red', s=10, label='Executed Trades', zorder=2, alpha=0.6)
axes[0].set_title('TOMATO Mid Price (Day 1)')
axes[0].set_ylim(4940, 5011)
axes[0].legend()

axes[1].plot(emerald_merged1['timestamp'], emerald_merged1['mid_price'])
axes[1].scatter(emerald_merged1['timestamp'], emerald_merged1['price'],
                color='red', s=10, label='Executed Trades', zorder=2, alpha=0.6)
axes[1].set_ylim(9990, 10010)
axes[1].set_title('EMERALD Mid Price (Day 1)')

plt.tight_layout()
plt.savefig("midprice_plot1.png")

# Plot mid_price of Day 2 against timestamps with executed trades price
# Top Diagram is Tomato, Bottom Diagram is Emerald
fig, axes = plt.subplots(2, 1, figsize=(14, 6))
axes[0].plot(tomato_merged2['timestamp'], tomato_merged2['mid_price'])
axes[0].scatter(tomato_merged2['timestamp'], tomato_merged2['price'],
                color='red', s=10, label='Executed Trades', zorder=2, alpha=0.6)
axes[0].set_ylim(4980, 5040)
axes[0].set_title('TOMATO Mid Price (Day 2)')

axes[1].plot(emerald_merged2['timestamp'], emerald_merged2['mid_price'])
axes[1].scatter(emerald_merged2['timestamp'], emerald_merged2['price'],
                color='red', s=10, label='Executed Trades', zorder=2, alpha=0.6)
axes[1].set_ylim(9990, 10010)
axes[1].set_title('EMERALD Mid Price (Day 2)')

plt.tight_layout()
plt.savefig("midprice_plot2.png")

# ---------------------- BID-ASK SPREAD ------------------------

# Uncategorized Scatter plot of tomato and emeralds bid-ask spread price
tomato_merged1['spread_1'] = tomato_merged1['ask_price_1'] - tomato_merged1['bid_price_1']
emerald_merged1['spread_1'] = emerald_merged1['ask_price_1'] - emerald_merged1['bid_price_1']
tomato_merged1['spread_2'] = tomato_merged1['ask_price_2'] - tomato_merged1['bid_price_2']
emerald_merged1['spread_2'] = emerald_merged1['ask_price_2'] - emerald_merged1['bid_price_2']

fig, axes = plt.subplots(2, 1, figsize=(14, 6))

# TOMATO — both levels
axes[0].plot(tomato_merged1['timestamp'], tomato_merged1['spread_1'], 
             label='Spread Level 1 (Best)', color='blue', alpha=0.8)
axes[0].plot(tomato_merged1['timestamp'], tomato_merged1['spread_2'], 
             label='Spread Level 2', color='orange', alpha=0.6)
axes[0].set_title('TOMATO Spread ')
axes[0].legend()

# EMERALD — both levels
axes[1].plot(emerald_merged1['timestamp'], emerald_merged1['spread_1'], 
             label='Spread Level 1 (Best)', color='blue', alpha=0.8)
axes[1].plot(emerald_merged1['timestamp'], emerald_merged1['spread_2'], 
             label='Spread Level 2', color='orange', alpha=0.6)
axes[1].set_title('EMERALD Spread — Both Levels')
axes[1].legend()

plt.tight_layout()
plt.savefig("spread.png")

# Tomato Spread 1: Categorize low spread and high spread with 13 as a threshold
fig, ax = plt.subplots(figsize=(14, 5))
low = tomato_merged1[tomato_merged1['spread_1'] < 13]
high = tomato_merged1[tomato_merged1['spread_1'] >= 13]
ax.scatter(low['timestamp'], low['mid_price'], color='steelblue', alpha=0.5, s=10, label='Spread < 13')
ax.scatter(high['timestamp'], high['mid_price'], color='tomato', alpha=0.5, s=10, label='Spread >= 13')
ax.set_title('TOMATO Mid Price by Spread Group (Day 1)')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Mid Price')
ax.legend()
plt.tight_layout()
plt.savefig("tomato_spread_scatter.png")

# Emeralds: Separate into two state, spread of 8 or 16
fig, ax = plt.subplots(figsize=(14, 5))
spread8 = emerald_merged1[emerald_merged1['spread_1'] == 8]
spread16 = emerald_merged1[emerald_merged1['spread_1'] == 16]
ax.scatter(spread8['timestamp'], spread8['mid_price'], color='steelblue', alpha=0.5, s=10, label='Spread = 8')
ax.scatter(spread16['timestamp'], spread16['mid_price'], color='tomato', alpha=0.5, s=10, label='Spread = 16')
ax.set_title('EMERALD Mid Price by Spread Group (Day 1)')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Mid Price')
ax.legend()
plt.tight_layout()
plt.savefig("emerald_spread_scatter.png")

# ---------------------- EXECUTED POINT OF ORDER ------------------------
def classify_execution(row):
    p = row['price']
    if p >= row['ask_price_2']:
        return 'Zone C - Hit L2 Ask'
    elif p >= row['ask_price_1']:
        return 'Zone A - Hit L1 Ask'
    elif p <= row['bid_price_2']:
        return 'Zone D - Hit L2 Bid'
    elif p <= row['bid_price_1']:
        return 'Zone B - Hit L1 Bid'
    else:
        return 'Zone E - Inside Spread'

combined_merged1 = pd.concat([tomato_merged1, emerald_merged1], ignore_index=True)
combined_merged1['execution_zone'] = combined_merged1.apply(classify_execution, axis=1)
print(combined_merged1.groupby(['symbol', 'execution_zone'])['price'].describe())
