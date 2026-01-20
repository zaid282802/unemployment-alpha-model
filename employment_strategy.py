"""
Complete Working Backtest - Unemployment Alpha Model
Uses real FRED data and yfinance price data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
FRED_API_KEY = os.getenv('FRED_API_KEY')

print("=" * 80)
print("UNEMPLOYMENT ALPHA MODEL - FULL BACKTEST")
print("=" * 80)
print()

# ==================== STEP 1: FETCH FRED DATA ====================
print("[1/6] Fetching employment data from FRED...")

try:
    from fredapi import Fred
    fred = Fred(api_key=FRED_API_KEY)

    start_date = '2010-01-01'
    end_date = '2024-12-31'

    # Get monthly data
    unrate = fred.get_series('UNRATE', start_date, end_date)
    claims = fred.get_series('ICSA', start_date, end_date)
    payrolls = fred.get_series('PAYEMS', start_date, end_date)
    participation = fred.get_series('CIVPART', start_date, end_date)

    print(f"   Unemployment Rate: {len(unrate)} observations")
    print(f"   Initial Claims: {len(claims)} observations")
    print(f"   Payrolls: {len(payrolls)} observations")
    print(f"   Participation: {len(participation)} observations")

except Exception as e:
    print(f"   Error: {e}")
    print("   Check your FRED API key")
    exit(1)

# ==================== STEP 2: CALCULATE SURPRISES ====================
print("\n[2/6] Calculating employment surprises...")

# Convert claims to monthly
claims_monthly = claims.resample('MS').mean()

# Create combined dataframe
df = pd.DataFrame({
    'unemployment_rate': unrate,
    'participation_rate': participation,
    'payrolls': payrolls
})

# Join claims
claims_monthly.name = 'initial_claims'
df = df.join(claims_monthly, how='left')
df = df.ffill()

# Calculate surprises (actual vs 12-month moving average)
lookback = 12

df['unrate_ma'] = df['unemployment_rate'].rolling(lookback).mean()
df['claims_ma'] = df['initial_claims'].rolling(lookback).mean()
df['payrolls_ma'] = df['payrolls'].rolling(lookback).mean()
df['participation_ma'] = df['participation_rate'].rolling(lookback).mean()

# Z-score surprises
df['unrate_surprise'] = (df['unemployment_rate'] - df['unrate_ma']) / df['unemployment_rate'].rolling(lookback).std()
df['claims_surprise'] = (df['initial_claims'] - df['claims_ma']) / df['initial_claims'].rolling(lookback).std()
df['payrolls_surprise'] = (df['payrolls'] - df['payrolls_ma']) / df['payrolls'].rolling(lookback).std()
df['participation_surprise'] = (df['participation_rate'] - df['participation_ma']) / df['participation_rate'].rolling(lookback).std()

# Composite surprise (weighted average)
df['composite_surprise'] = (
    0.4 * -df['unrate_surprise'] +      # Lower unemployment = good
    0.3 * -df['claims_surprise'] +      # Lower claims = good
    0.2 * df['payrolls_surprise'] +     # Higher payrolls = good
    0.1 * df['participation_surprise']  # Higher participation = good
)

# Simple smoothing (3-month MA)
df['smoothed_surprise'] = df['composite_surprise'].rolling(3).mean()

print(f"   Surprise range: [{df['smoothed_surprise'].min():.2f}, {df['smoothed_surprise'].max():.2f}]")

# ==================== STEP 3: GENERATE SIGNALS ====================
print("\n[3/6] Generating trading signals...")

# Generate signals based on thresholds
df['signal'] = 0
df.loc[df['smoothed_surprise'] > 0.5, 'signal'] = 1    # Risk-ON
df.loc[df['smoothed_surprise'] < -0.5, 'signal'] = -1  # Risk-OFF

# Allocation weights
df['spy_weight'] = 0.5  # Default 50/50
df['tlt_weight'] = 0.5

df.loc[df['signal'] == 1, 'spy_weight'] = 0.8
df.loc[df['signal'] == 1, 'tlt_weight'] = 0.2

df.loc[df['signal'] == -1, 'spy_weight'] = 0.2
df.loc[df['signal'] == -1, 'tlt_weight'] = 0.8

risk_on = (df['signal'] == 1).sum()
risk_off = (df['signal'] == -1).sum()
neutral = (df['signal'] == 0).sum()
total = len(df)

print(f"   Risk-ON: {risk_on} months ({risk_on/total*100:.1f}%)")
print(f"   Risk-OFF: {risk_off} months ({risk_off/total*100:.1f}%)")
print(f"   Neutral: {neutral} months ({neutral/total*100:.1f}%)")

# ==================== STEP 4: FETCH PRICE DATA ====================
print("\n[4/6] Fetching SPY/TLT price data from yfinance...")

try:
    import yfinance as yf

    spy_ticker = yf.Ticker('SPY')
    tlt_ticker = yf.Ticker('TLT')

    spy_hist = spy_ticker.history(start=start_date, end=end_date)
    tlt_hist = tlt_ticker.history(start=start_date, end=end_date)

    prices = pd.DataFrame({
        'spy_price': spy_hist['Close'],
        'tlt_price': tlt_hist['Close']
    })

    # Remove timezone info to match FRED data
    prices.index = prices.index.tz_localize(None)

    prices['spy_return'] = prices['spy_price'].pct_change()
    prices['tlt_return'] = prices['tlt_price'].pct_change()

    print(f"   SPY: {len(prices)} days")
    print(f"   TLT: {len(prices)} days")

except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ==================== STEP 5: RUN BACKTEST ====================
print("\n[5/6] Running backtest simulation...")

# Resample signals to daily frequency
signals_daily = df[['spy_weight', 'tlt_weight']].reindex(prices.index, method='ffill')

# Combine with prices
backtest = prices.join(signals_daily, how='left')
backtest = backtest.ffill().fillna(0.5)  # Default to 50/50

# Calculate portfolio returns
backtest['portfolio_return'] = (
    backtest['spy_weight'] * backtest['spy_return'] +
    backtest['tlt_weight'] * backtest['tlt_return']
)

# Transaction costs (5 bps when rebalancing)
backtest['weight_change'] = backtest['spy_weight'].diff().abs()
backtest['transaction_cost'] = backtest['weight_change'] * 0.0005  # 5 bps
backtest['portfolio_return_net'] = backtest['portfolio_return'] - backtest['transaction_cost']

# Calculate cumulative returns
backtest['strategy_cumulative'] = (1 + backtest['portfolio_return_net'].fillna(0)).cumprod()
backtest['spy_cumulative'] = (1 + backtest['spy_return'].fillna(0)).cumprod()
backtest['tlt_cumulative'] = (1 + backtest['tlt_return'].fillna(0)).cumprod()

initial_capital = 100000
backtest['portfolio_value'] = initial_capital * backtest['strategy_cumulative']

print(f"   Simulation complete: {len(backtest)} days")

# ==================== STEP 6: CALCULATE METRICS ====================
print("\n[6/6] Calculating performance metrics...")

# Strategy metrics
returns = backtest['portfolio_return_net'].dropna()
total_return = (backtest['strategy_cumulative'].iloc[-1] - 1) * 100
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

# Drawdown
running_max = backtest['strategy_cumulative'].cummax()
drawdown = (backtest['strategy_cumulative'] - running_max) / running_max
max_drawdown = drawdown.min() * 100

# SPY benchmark
spy_returns = backtest['spy_return'].dropna()
spy_total_return = (backtest['spy_cumulative'].iloc[-1] - 1) * 100
spy_sharpe = (spy_returns.mean() / spy_returns.std()) * np.sqrt(252)

spy_running_max = backtest['spy_cumulative'].cummax()
spy_dd = ((backtest['spy_cumulative'] - spy_running_max) / spy_running_max).min() * 100

# Transaction costs
total_tc = backtest['transaction_cost'].sum() * initial_capital
n_trades = (backtest['weight_change'] > 0.01).sum()

# Win rate
monthly_returns = backtest['portfolio_return_net'].resample('M').sum()
win_rate = (monthly_returns > 0).sum() / len(monthly_returns) * 100

# ==================== DISPLAY RESULTS ====================
print("\n" + "=" * 80)
print("BACKTEST RESULTS (2010-2024)")
print("=" * 80)

print("\nSTRATEGY PERFORMANCE:")
print(f"  Total Return:        {total_return:>8.2f}%")
print(f"  Sharpe Ratio:        {sharpe_ratio:>8.2f}")
print(f"  Max Drawdown:        {max_drawdown:>8.2f}%")
print(f"  Win Rate (Monthly):  {win_rate:>8.1f}%")
print(f"  Final Value:         ${backtest['portfolio_value'].iloc[-1]:>12,.2f}")

print("\nBENCHMARK (SPY Buy & Hold):")
print(f"  Total Return:        {spy_total_return:>8.2f}%")
print(f"  Sharpe Ratio:        {spy_sharpe:>8.2f}")
print(f"  Max Drawdown:        {spy_dd:>8.2f}%")
print(f"  Final Value:         ${initial_capital * backtest['spy_cumulative'].iloc[-1]:>12,.2f}")

print("\nTRANSACTION COSTS:")
print(f"  Total Costs:         ${total_tc:>12,.2f}")
print(f"  Number of Rebalances: {n_trades}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)

print(f"\nAlpha vs SPY: {total_return - spy_total_return:+.2f}%")
print(f"Risk-Adjusted Alpha: Sharpe {sharpe_ratio:.2f} vs {spy_sharpe:.2f}")
print(f"Downside Protection: Max DD {max_drawdown:.1f}% vs {spy_dd:.1f}%")

# Save results
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)

backtest.to_csv(results_dir / 'full_backtest_results.csv')
df.to_csv(results_dir / 'employment_signals.csv')

print(f"\nResults saved to: {results_dir.absolute()}")
print("=" * 80)
