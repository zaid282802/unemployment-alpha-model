# Unemployment Alpha Model

Systematic macro trading strategy using employment data surprises to generate SPY/TLT allocation signals.

## Overview

This project implements a systematic trading strategy based on employment data from FRED. The hypothesis is that employment surprises (actual data vs. expectations) create predictable market movements that can be traded systematically with better risk-adjusted returns.

The strategy uses four employment indicators:
- Unemployment Rate (UNRATE)
- Initial Jobless Claims (ICSA)
- Nonfarm Payrolls (PAYEMS)
- Labor Force Participation Rate (CIVPART)

These are combined into a composite surprise index that generates dynamic allocation signals between SPY (equities) and TLT (treasuries).

## Backtest Results (2010-2024)

| Metric | Strategy | SPY Buy & Hold |
|--------|----------|----------------|
| Total Return | 271.36% | 925.65% |
| Sharpe Ratio | 0.81 | 0.82 |
| Max Drawdown | -25.54% | -33.72% |
| Win Rate | 66.1% | N/A |

The strategy underperforms SPY in absolute returns but provides 24% better downside protection (-25.5% vs -33.7% max drawdown) with similar Sharpe ratio. The 2010-2024 period was a historic bull market, which favors buy-and-hold. The value proposition is risk reduction, not maximum returns.

## How It Works

**Step 1: Calculate Surprises**

For each employment indicator, calculate the surprise as:
```
surprise = (actual - 12_month_MA) / 12_month_std
```

**Step 2: Create Composite Index**

Weighted average of surprises:
```
composite = 0.4 * (-unemployment) + 0.3 * (-claims) + 0.2 * payrolls + 0.1 * participation
```

**Step 3: Generate Signals**

Apply 3-month moving average for smoothing, then:
- Surprise > +0.5σ → Risk-ON (80% SPY, 20% TLT)
- Surprise < -0.5σ → Risk-OFF (20% SPY, 80% TLT)
- Otherwise → Neutral (50% SPY, 50% TLT)

**Step 4: Backtest**

Monthly rebalancing with 5 bps transaction costs.

## Installation and Usage

### Quick Demo (No Setup)

```bash
python demo_backtest.py
```

Uses simulated data to demonstrate strategy logic without needing API keys.

### Real Backtest

1. Get free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

2. Create `.env` file:
```
FRED_API_KEY=your_api_key_here
USE_DEMO_MODE=False
START_DATE=2010-01-01
END_DATE=2024-12-31
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run backtest:
```bash
python employment_strategy.py
```

This fetches real FRED data, calculates surprises, generates signals, and runs the full backtest.

## Project Structure

```
unemployment_alpha_model/
├── employment_strategy.py      # Main backtest script (standalone)
├── demo_backtest.py            # Quick demo with simulated data
├── src/                        # Modular OOP implementation
│   ├── data/fred_fetcher.py
│   ├── features/surprise_calculator.py
│   ├── models/signal_generator.py
│   ├── backtest/engine.py
│   └── run_backtest.py
├── requirements.txt
├── .env.example
└── README.md
```

The `employment_strategy.py` script is standalone and generates the results above. The `src/` folder contains a modular OOP implementation demonstrating software architecture with reusable components.

## Key Insights

**Why Employment Data?**

Employment is a leading indicator of economic health that affects Fed policy, consumer spending, and corporate earnings. Unlike high-frequency data that's already priced in, employment surprises reveal changes in economic fundamentals.

**Why SPY/TLT?**

These assets have negative correlation (~-0.3 to -0.5). When employment surprises are negative (recession risk), TLT provides a hedge. When positive (expansion), SPY captures upside.

**Why Underperform SPY?**

The strategy is designed for downside protection, not maximum returns. The conservative allocation caps upside but reduces drawdown significantly. In real-world investing, large losses are psychologically difficult to recover from.

## Limitations

1. Underperforms in strong bull markets (2010-2024 was historic)
2. Transaction costs in real markets may exceed 5 bps assumption
3. Assumes employment surprises remain predictive (regime change risk)
4. Monthly rebalancing may not capture intra-month opportunities

## Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
fredapi>=0.5.1
yfinance>=0.2.28
python-dotenv>=1.0.0
pykalman>=0.9.5
```

See `requirements.txt` for complete list.

## Sample Output

```
================================================================================
BACKTEST RESULTS (2010-2024)
================================================================================

STRATEGY PERFORMANCE:
  Total Return:          271.36%
  Sharpe Ratio:            0.81
  Max Drawdown:          -25.54%
  Win Rate (Monthly):      66.1%
  Final Value:         $  371,355.91

BENCHMARK (SPY Buy & Hold):
  Total Return:          925.65%
  Sharpe Ratio:            0.82
  Max Drawdown:          -33.72%
  Final Value:         $1,025,649.78

TRANSACTION COSTS:
  Total Costs:         $      210.00
  Number of Rebalances: 14
```

## Interview Talking Points

**60-second pitch:**

"I built a systematic macro strategy that trades employment data surprises from FRED. The model fetches unemployment, jobless claims, payrolls, and participation data, calculates surprises versus a 12-month moving average, and generates a composite index weighted by economic importance.

When the smoothed composite signal exceeds +0.5 standard deviations, the strategy goes Risk-ON with 80% SPY and 20% TLT. Below -0.5, it goes Risk-OFF with 20% SPY and 80% TLT. Otherwise, it stays neutral at 50/50.

Over a 14-year backtest from 2010 to 2024, the strategy achieved a 0.81 Sharpe ratio with 24% better downside protection than SPY, though it underperformed in absolute returns due to the conservative allocation during a historic bull market."

**Common questions:**

Q: Why underperform SPY?
A: The strategy is designed for downside protection, not maximum returns. The value proposition is reducing max drawdown from -33% to -25%.

Q: What would you improve?
A: (1) Machine learning to predict employment surprises, (2) Regime detection to avoid high volatility periods, (3) Integration with live data feeds for real-time trading.

## Disclaimer

This project is for educational and interview purposes only. Not financial advice. Past performance does not guarantee future results.

## License

MIT License

---

Last Updated: January 2026
