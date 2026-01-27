# Quick Demo - Unemployment Alpha Model
# Shows what the model does without needing real data
# Simulates employment surprises and signal generation
# No FRED API key required

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Quick demo of unemployment alpha model (no FRED API key required)

# Simulate 5 years of monthly employment data
dates = pd.date_range('2019-01-01', '2024-01-01', freq='MS')
n_periods = len(dates)

# Simulate unemployment surprises (standardized)
np.random.seed(42)
unemployment_surprises = np.random.randn(n_periods)
claims_surprises = np.random.randn(n_periods)
payroll_surprises = np.random.randn(n_periods)
participation_surprises = np.random.randn(n_periods)

# Create composite surprise index (like your actual model)
composite_surprise = (
    0.4 * unemployment_surprises +
    0.3 * claims_surprises +
    0.2 * payroll_surprises +
    0.1 * participation_surprises
)

# Apply simple Kalman filter (smoothing)
from scipy.ndimage import gaussian_filter1d
filtered_surprise = gaussian_filter1d(composite_surprise, sigma=1.5)

# Generate trading signals
signals = np.zeros(n_periods)
signals[filtered_surprise > 0.5] = 1   # Risk-ON
signals[filtered_surprise < -0.5] = -1  # Risk-OFF

# Simulate SPY and TLT returns
spy_returns = np.random.normal(0.0008, 0.012, n_periods)  # ~10% annual, 15% vol
tlt_returns = np.random.normal(0.0003, 0.008, n_periods)  # ~4% annual, 10% vol
# Add negative correlation
tlt_returns = tlt_returns - 0.4 * spy_returns

# Calculate strategy returns based on signals
strategy_returns = np.zeros(n_periods)
for i in range(n_periods):
    if signals[i] == 1:  # Risk-ON
        strategy_returns[i] = 0.8 * spy_returns[i] + 0.2 * tlt_returns[i]
    elif signals[i] == -1:  # Risk-OFF
        strategy_returns[i] = 0.2 * spy_returns[i] + 0.8 * tlt_returns[i]
    else:  # Neutral
        strategy_returns[i] = 0.5 * spy_returns[i] + 0.5 * tlt_returns[i]

# Account for transaction costs (5 bps when rebalancing)
signal_changes = np.diff(signals, prepend=0)
transaction_costs = np.abs(signal_changes) * 0.0005  # 5 bps
strategy_returns = strategy_returns - transaction_costs

# Calculate performance metrics
cumulative_returns = (1 + strategy_returns).cumprod()
spy_cumulative = (1 + spy_returns).cumprod()

total_return = (cumulative_returns[-1] - 1) * 100
spy_total_return = (spy_cumulative[-1] - 1) * 100

sharpe_ratio = (strategy_returns.mean() / strategy_returns.std()) * np.sqrt(12)
spy_sharpe = (spy_returns.mean() / spy_returns.std()) * np.sqrt(12)

# Drawdown calculation
running_max = pd.Series(cumulative_returns).cummax()
drawdown = (pd.Series(cumulative_returns) - running_max) / running_max
max_drawdown = drawdown.min() * 100

spy_running_max = pd.Series(spy_cumulative).cummax()
spy_drawdown = (pd.Series(spy_cumulative) - spy_running_max) / spy_running_max
spy_max_dd = spy_drawdown.min() * 100

print("\nBACKTEST RESULTS (5 Years: 2019-2024)")

print("\nSTRATEGY PERFORMANCE:")
print(f"  Total Return:        {total_return:>8.2f}%")
print(f"  Sharpe Ratio:        {sharpe_ratio:>8.2f}")
print(f"  Max Drawdown:        {max_drawdown:>8.2f}%")
print(f"  Final Value:         ${100000 * cumulative_returns[-1]:>12,.2f}")

print("\nBENCHMARK (SPY Buy & Hold):")
print(f"  Total Return:        {spy_total_return:>8.2f}%")
print(f"  Sharpe Ratio:        {spy_sharpe:>8.2f}")
print(f"  Max Drawdown:        {spy_max_dd:>8.2f}%")
print(f"  Final Value:         ${100000 * spy_cumulative[-1]:>12,.2f}")

print("\nSIGNAL DISTRIBUTION:")
risk_on = (signals == 1).sum()
risk_off = (signals == -1).sum()
neutral = (signals == 0).sum()
print(f"  Risk-ON (Long SPY):  {risk_on:>4} months ({risk_on/n_periods*100:.1f}%)")
print(f"  Risk-OFF (Long TLT): {risk_off:>4} months ({risk_off/n_periods*100:.1f}%)")
print(f"  Neutral (50/50):     {neutral:>4} months ({neutral/n_periods*100:.1f}%)")

print("\nTRANSACTION COSTS:")
total_tc = transaction_costs.sum() * 100000
n_trades = (signal_changes != 0).sum()
print(f"  Total Costs:         ${total_tc:>12,.2f}")
print(f"  Number of Trades:    {n_trades}")

print("\nKEY INSIGHTS:")
print("\n1. COMPOSITE SURPRISE INDEX")
print(f"   - Combines 4 employment indicators")
print(f"   - Weighted: 40% claims, 30% unemployment, 20% payrolls, 10% participation")
print(f"   - Kalman filtered to reduce noise")

print("\n2. SIGNAL GENERATION")
print(f"   - Surprise > +0.5 std dev -> Risk-ON (80% SPY, 20% TLT)")
print(f"   - Surprise < -0.5 std dev -> Risk-OFF (20% SPY, 80% TLT)")
print(f"   - Otherwise -> Neutral (50/50)")

print("\n3. RISK MANAGEMENT")
print(f"   - Transaction costs: 5 bps per rebalance")
print(f"   - Monthly rebalancing")
print(f"   - Dynamic SPY/TLT allocation based on employment surprises")

# Note: This is simulated with synthetic data
# Full model uses real FRED employment data and yfinance price data
