# Unemployment Alpha Model - Visualization Generator
# Creates 8 professional portfolio charts (300 DPI)
# Usage: python create_visualizations.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


# Setup paths
script_dir = Path(__file__).parent
results_dir = script_dir / 'results'
viz_dir = script_dir / 'visualizations'
viz_dir.mkdir(exist_ok=True)

# Load data
backtest = pd.read_csv(results_dir / 'full_backtest_results.csv', index_col=0, parse_dates=True)
signals = pd.read_csv(results_dir / 'employment_signals.csv', index_col=0, parse_dates=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Chart 1: Equity curve comparison
backtest['portfolio_6040'] = (1 + (0.6 * backtest['spy_return'] + 0.4 * backtest['tlt_return']).fillna(0)).cumprod()
fig, ax = plt.subplots(figsize=(14, 8))

# Plot all strategies
ax.plot(backtest.index, backtest['strategy_cumulative'],
        linewidth=2.5, label='Unemployment Alpha', color='#2E86AB', zorder=3)
ax.plot(backtest.index, backtest['spy_cumulative'],
        linewidth=2, label='SPY Buy & Hold', color='#A23B72', alpha=0.8)
ax.plot(backtest.index, backtest['portfolio_6040'],
        linewidth=2, label='60/40 Portfolio', color='#F18F01', alpha=0.8)

# Highlight recession periods
recession_periods = [
    ('2020-02-01', '2020-04-30'),  # COVID crash
]
for start, end in recession_periods:
    ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
              alpha=0.2, color='red', label='COVID Recession' if start == '2020-02-01' else '')

ax.set_title('Equity Curve Comparison: Unemployment Alpha vs Benchmarks (2010-2024)',
            fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Cumulative Return (Initial $100k)', fontsize=12)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
ax.grid(True, alpha=0.3)
ax.set_ylim(bottom=0.8)

# Add annotations for final values
final_date = backtest.index[-1]
for cumul, label, color, yoffset in [
    (backtest['strategy_cumulative'].iloc[-1], 'Strategy', '#2E86AB', 0),
    (backtest['spy_cumulative'].iloc[-1], 'SPY', '#A23B72', -0.5),
    (backtest['portfolio_6040'].iloc[-1], '60/40', '#F18F01', 0.5)
]:
    ax.annotate(f'{label}: ${100000*cumul:,.0f}',
               xy=(final_date, cumul),
               xytext=(10, yoffset*20),
               textcoords='offset points',
               fontsize=9, color=color, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=color))

plt.tight_layout()
plt.savefig(viz_dir / '1_equity_curve_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 2: Drawdown comparison
# Calculate drawdowns
strategy_dd = (backtest['strategy_cumulative'] / backtest['strategy_cumulative'].cummax() - 1) * 100
spy_dd = (backtest['spy_cumulative'] / backtest['spy_cumulative'].cummax() - 1) * 100
portfolio_6040_dd = (backtest['portfolio_6040'] / backtest['portfolio_6040'].cummax() - 1) * 100

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Top: Drawdown over time
ax1.fill_between(backtest.index, strategy_dd, 0, alpha=0.7, color='#2E86AB', label='Unemployment Alpha')
ax1.fill_between(backtest.index, spy_dd, 0, alpha=0.5, color='#A23B72', label='SPY Buy & Hold')
ax1.fill_between(backtest.index, portfolio_6040_dd, 0, alpha=0.5, color='#F18F01', label='60/40 Portfolio')

ax1.set_title('Drawdown Comparison (2010-2024)', fontsize=16, fontweight='bold', pad=20)
ax1.set_ylabel('Drawdown (%)', fontsize=12)
ax1.legend(loc='lower left', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

# Bottom: Bar chart of max drawdowns
strategies = ['Unemployment\nAlpha', 'SPY\nBuy & Hold', '60/40\nPortfolio']
max_dds = [strategy_dd.min(), spy_dd.min(), portfolio_6040_dd.min()]
colors = ['#2E86AB', '#A23B72', '#F18F01']

bars = ax2.bar(strategies, max_dds, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_title('Maximum Drawdown Comparison', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylabel('Max Drawdown (%)', fontsize=12)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, dd in zip(bars, max_dds):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height - 2,
            f'{dd:.1f}%', ha='center', va='top', fontsize=12, fontweight='bold', color='white')

plt.tight_layout()
plt.savefig(viz_dir / '2_drawdown_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 3: Allocation timeline
# Resample signals to monthly for cleaner visualization
monthly_signals = signals[['signal', 'spy_weight', 'smoothed_surprise']].copy()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Top: Signal regime over time
signal_map = {-1: 'Risk-OFF', 0: 'Neutral', 1: 'Risk-ON'}
signal_colors = {-1: '#E63946', 0: '#F1FAEE', 1: '#06A77D'}

for signal_val, color in signal_colors.items():
    mask = monthly_signals['signal'] == signal_val
    ax1.fill_between(monthly_signals.index, 0, 1, where=mask,
                     alpha=0.7, color=color, label=signal_map[signal_val], step='post')

ax1.set_title('Risk Regime Timeline (2010-2024)', fontsize=16, fontweight='bold', pad=20)
ax1.set_ylabel('Signal State', fontsize=12)
ax1.set_yticks([0.25, 0.5, 0.75])
ax1.set_yticklabels(['Risk-OFF', 'Neutral', 'Risk-ON'])
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3, axis='x')

# Highlight COVID
ax1.axvspan(pd.to_datetime('2020-02-01'), pd.to_datetime('2020-04-30'),
           alpha=0.2, color='red', zorder=-1)
ax1.text(pd.to_datetime('2020-03-15'), 0.9, 'COVID', fontsize=10,
        ha='center', fontweight='bold', color='darkred')

# Bottom: SPY allocation weight
ax2.fill_between(monthly_signals.index, 0, monthly_signals['spy_weight']*100,
                 alpha=0.7, color='#2E86AB', step='post')
ax2.set_title('Equity Allocation Over Time', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('SPY Allocation (%)', fontsize=12)
ax2.set_ylim(0, 100)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Neutral (50%)')
ax2.legend(loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig(viz_dir / '3_allocation_timeline.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 4: Signal evolution with composite index
fig, ax = plt.subplots(figsize=(14, 8))

# Plot composite surprise index
ax.plot(signals.index, signals['smoothed_surprise'],
       linewidth=2, color='#2E86AB', label='Composite Surprise Index', zorder=2)

# Add threshold bands
ax.axhline(y=0.5, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Risk-ON Threshold (+0.5σ)')
ax.axhline(y=-0.5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Risk-OFF Threshold (-0.5σ)')
ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

# Fill regions
ax.fill_between(signals.index, 0.5, signals['smoothed_surprise'].max(),
               alpha=0.2, color='green', label='Risk-ON Region')
ax.fill_between(signals.index, -0.5, signals['smoothed_surprise'].min(),
               alpha=0.2, color='red', label='Risk-OFF Region')
ax.fill_between(signals.index, -0.5, 0.5, alpha=0.1, color='gray', label='Neutral Region')

ax.set_title('Employment Composite Surprise Index Evolution (2010-2024)',
            fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Surprise Index (Standard Deviations)', fontsize=12)
ax.legend(loc='upper left', fontsize=10, ncol=2, framealpha=0.95)
ax.grid(True, alpha=0.3)

# Annotate key events
events = [
    ('2020-03-01', 2.5, 'COVID Crash\nMassive jobless claims'),
    ('2021-06-01', 1.2, 'Recovery\nPayrolls surge'),
]
for date, y, text in events:
    ax.annotate(text, xy=(pd.to_datetime(date), y),
               xytext=(10, 10), textcoords='offset points',
               fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

plt.tight_layout()
plt.savefig(viz_dir / '4_signal_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 5: Rolling 12-month Sharpe ratio
# Calculate rolling Sharpe (12-month window)
window = 252  # 1 year daily
strategy_rolling_sharpe = (backtest['portfolio_return_net'].rolling(window).mean() /
                          backtest['portfolio_return_net'].rolling(window).std()) * np.sqrt(252)
spy_rolling_sharpe = (backtest['spy_return'].rolling(window).mean() /
                     backtest['spy_return'].rolling(window).std()) * np.sqrt(252)

fig, ax = plt.subplots(figsize=(14, 8))

ax.plot(backtest.index, strategy_rolling_sharpe,
       linewidth=2.5, color='#2E86AB', label='Unemployment Alpha', alpha=0.9, zorder=3)
ax.plot(backtest.index, spy_rolling_sharpe,
       linewidth=2, color='#A23B72', label='SPY Buy & Hold', alpha=0.7)

# Highlight when strategy outperforms
outperform = strategy_rolling_sharpe > spy_rolling_sharpe
ax.fill_between(backtest.index, 0, 3, where=outperform,
               alpha=0.15, color='green', label='Strategy Outperforms', step='post')

ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Sharpe = 1.0')
ax.set_title('Rolling 12-Month Sharpe Ratio Comparison (2010-2024)',
            fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Rolling Sharpe Ratio', fontsize=12)
ax.set_ylim(-1, 3)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(viz_dir / '5_rolling_sharpe.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 6: Factor attribution
# Calculate individual indicator signal contributions
indicators = {
    'Unemployment Rate': -signals['unrate_surprise'] * 0.4,
    'Jobless Claims': -signals['claims_surprise'] * 0.3,
    'Payrolls': signals['payrolls_surprise'] * 0.2,
    'Labor Participation': signals['participation_surprise'] * 0.1
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Stacked area chart of contributions over time
contrib_df = pd.DataFrame(indicators)
contrib_df = contrib_df.fillna(0)

ax1.stackplot(contrib_df.index,
             contrib_df['Unemployment Rate'],
             contrib_df['Jobless Claims'],
             contrib_df['Payrolls'],
             contrib_df['Labor Participation'],
             labels=contrib_df.columns,
             alpha=0.8,
             colors=['#E63946', '#F1FAEE', '#A8DADC', '#457B9D'])

ax1.plot(signals.index, signals['composite_surprise'],
        color='black', linewidth=2, label='Total Composite', zorder=5)

ax1.set_title('Factor Contributions Over Time', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Contribution to Signal', fontsize=12)
ax1.legend(loc='upper left', fontsize=10, framealpha=0.95)
ax1.grid(True, alpha=0.3)

# Right: Average absolute contribution (bar chart)
avg_contrib = contrib_df.abs().mean().sort_values(ascending=True)
colors_bar = ['#457B9D', '#A8DADC', '#F1FAEE', '#E63946']

bars = ax2.barh(avg_contrib.index, avg_contrib.values, color=colors_bar, alpha=0.8, edgecolor='black')
ax2.set_title('Average Indicator Importance', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Mean Absolute Contribution', fontsize=12)
ax2.grid(True, alpha=0.3, axis='x')

# Add percentage labels
total = avg_contrib.sum()
for bar, val in zip(bars, avg_contrib.values):
    pct = (val / total) * 100
    ax2.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(viz_dir / '6_factor_attribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 7: COVID case study
# Focus on COVID period
covid_start = '2020-01-01'
covid_end = '2020-06-30'
covid_bt = backtest.loc[covid_start:covid_end].copy()
covid_sig = signals.loc[covid_start:covid_end].copy()

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

# Top: Equity curves during COVID
ax1.plot(covid_bt.index, (covid_bt['strategy_cumulative'] / covid_bt['strategy_cumulative'].iloc[0] - 1) * 100,
        linewidth=3, color='#2E86AB', label='Unemployment Alpha', zorder=3)
ax1.plot(covid_bt.index, (covid_bt['spy_cumulative'] / covid_bt['spy_cumulative'].iloc[0] - 1) * 100,
        linewidth=2, color='#A23B72', label='SPY Buy & Hold', alpha=0.8)

ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax1.set_title('COVID-19 Case Study: Strategy vs SPY (Jan-Jun 2020)',
             fontsize=16, fontweight='bold', pad=20)
ax1.set_ylabel('Return Since Jan 2020 (%)', fontsize=12)
ax1.legend(loc='lower left', fontsize=11)
ax1.grid(True, alpha=0.3)

# Add annotations for key dates
key_dates = [
    ('2020-02-19', 'SPY Peak'),
    ('2020-03-23', 'SPY Bottom\n-33.7%'),
]
for date, label in key_dates:
    y_val = (covid_bt.loc[date, 'spy_cumulative'] / covid_bt['spy_cumulative'].iloc[0] - 1) * 100
    ax1.axvline(x=pd.to_datetime(date), color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax1.text(pd.to_datetime(date), y_val - 5, label, fontsize=9, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

# Middle: Allocation shifts
ax2.fill_between(covid_sig.index, 0, covid_sig['spy_weight']*100,
                 alpha=0.7, color='#2E86AB', step='post', label='SPY Allocation')
ax2.fill_between(covid_sig.index, covid_sig['spy_weight']*100, 100,
                 alpha=0.7, color='#F4A261', step='post', label='TLT Allocation')

ax2.set_ylabel('Allocation (%)', fontsize=12)
ax2.set_ylim(0, 100)
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3)

# Annotate allocation changes
for idx in covid_sig.index:
    if covid_sig.loc[idx, 'signal'] != 0:
        signal_val = covid_sig.loc[idx, 'signal']
        if signal_val == -1:
            ax2.annotate('Risk-OFF\n(80% TLT)', xy=(idx, 20), xytext=(0, -20),
                       textcoords='offset points', fontsize=8, color='darkred',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='pink', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='red'))
            break

# Bottom: Composite signal
ax3.plot(covid_sig.index, covid_sig['smoothed_surprise'],
        linewidth=2.5, color='#2E86AB', marker='o', markersize=6)
ax3.axhline(y=0.5, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
ax3.axhline(y=-0.5, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
ax3.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

ax3.fill_between(covid_sig.index, -0.5, covid_sig['smoothed_surprise'].min(),
                alpha=0.2, color='red')
ax3.set_xlabel('Date', fontsize=12)
ax3.set_ylabel('Composite Signal (σ)', fontsize=12)
ax3.grid(True, alpha=0.3)

# Annotate signal drop
signal_drop_date = covid_sig['smoothed_surprise'].idxmin()
ax3.annotate(f'Signal Plunges\n{covid_sig["smoothed_surprise"].min():.2f}σ',
            xy=(signal_drop_date, covid_sig['smoothed_surprise'].min()),
            xytext=(20, 20), textcoords='offset points',
            fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3'))

plt.tight_layout()
plt.savefig(viz_dir / '7_covid_case_study.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 8: Transaction cost sensitivity analysis
# Test different transaction cost assumptions
tc_levels = [0, 2.5, 5, 10, 15, 20, 30]  # basis points
sharpe_results = []
return_results = []

for tc_bps in tc_levels:
    tc_rate = tc_bps / 10000
    returns_net = backtest['portfolio_return'] - (backtest['weight_change'] * tc_rate)
    sharpe = (returns_net.mean() / returns_net.std()) * np.sqrt(252)
    total_ret = ((1 + returns_net.fillna(0)).cumprod().iloc[-1] - 1) * 100

    sharpe_results.append(sharpe)
    return_results.append(total_ret)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Sharpe vs transaction costs
ax1.plot(tc_levels, sharpe_results, marker='o', markersize=10, linewidth=2.5,
        color='#2E86AB', markerfacecolor='#F4A261', markeredgewidth=2)
ax1.axvline(x=5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Base Case (5 bps)')
ax1.axhline(y=sharpe_results[tc_levels.index(5)], color='red', linestyle='--', linewidth=1, alpha=0.5)

ax1.set_title('Sharpe Ratio vs Transaction Costs', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Transaction Cost (basis points)', fontsize=12)
ax1.set_ylabel('Sharpe Ratio', fontsize=12)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0.806, 0.814])

# Right: Total return vs transaction costs
ax2.plot(tc_levels, return_results, marker='s', markersize=10, linewidth=2.5,
        color='#A23B72', markerfacecolor='#F4A261', markeredgewidth=2)
ax2.axvline(x=5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Base Case (5 bps)')
ax2.axhline(y=return_results[tc_levels.index(5)], color='red', linestyle='--', linewidth=1, alpha=0.5)

ax2.set_title('Total Return vs Transaction Costs', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Transaction Cost (basis points)', fontsize=12)
ax2.set_ylabel('Total Return (%)', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_ylim([265, 273])

plt.tight_layout()
plt.savefig(viz_dir / '8_transaction_cost_sensitivity.png', dpi=300, bbox_inches='tight')
plt.close()

# All 8 charts saved to visualizations folder
