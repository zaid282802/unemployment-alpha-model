# Unemployment Alpha Model

> Systematic macro trading strategy using employment data surprises to generate dynamic SPY/TLT allocation signals with superior downside protection.

## Project Overview

This project implements a defensive trading strategy based on employment data from FRED (Federal Reserve Economic Data). The core insight: employment surprises reveal economic regime shifts before markets fully adjust, enabling timely risk-on/risk-off positioning.

**Key Finding**: The strategy achieves **24% better drawdown protection** than SPY buy-and-hold (-25.5% vs -33.7%) with similar Sharpe ratio (0.81 vs 0.82) over 14 years (2010-2024).

### Employment Indicators Used

- **Unemployment Rate (UNRATE)** - 40% weight
- **Initial Jobless Claims (ICSA)** - 30% weight
- **Nonfarm Payrolls (PAYEMS)** - 20% weight
- **Labor Force Participation Rate (CIVPART)** - 10% weight

These are combined into a composite surprise index that generates dynamic allocation signals between SPY (equities) and TLT (treasuries).

---

## Backtest Results (2010-2024, 180 Months)

| Metric | Strategy | SPY Buy & Hold | 60/40 Portfolio |
|--------|----------|----------------|-----------------|
| **Total Return** | 271% | 926% | 318% |
| **Sharpe Ratio** | **0.81** | 0.82 | 0.65 |
| **Max Drawdown** | **-25.5%** | -33.7% | -28.1% |
| **Win Rate** | **66.1%** | N/A | N/A |
| **Volatility** | **12%** | 15% | 10% |
| **Sortino Ratio** | **1.12** | 1.18 | 0.89 |

** Important**: This is a **DEFENSIVE strategy**, not a growth strategy. It underperforms buy-and-hold during bull markets by design. The 2010-2024 period was the longest bull market in history—SPY returned 12.1% annually. The value proposition is **capital preservation**, not maximum returns.

### COVID-19 Performance (2020 Crash)

- **Strategy Drawdown**: -12.1% (peak to trough)
- **SPY Drawdown**: -33.7%
- **Protection**: **64% better** downside protection
- **Signal Trigger**: Jobless claims spiked to 6.9M (13σ event), shifting allocation to Risk-OFF before peak crash

---

## Quick Start

### Prerequisites
```bash
Python 3.8+
numpy, pandas, yfinance, fredapi, matplotlib, seaborn, scipy
```

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/unemployment-alpha-model.git
cd unemployment-alpha-model

# Install dependencies
pip install numpy pandas yfinance fredapi matplotlib seaborn scipy python-dotenv
```

### Run Analysis

**Option 1: Quick Demo (No Setup Required)**
```bash
python demo_backtest.py
```
Uses simulated data to demonstrate strategy logic without needing API keys.

**Option 2: Real Backtest**

1. Get free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

2. Create `.env` file:
```bash
FRED_API_KEY=your_api_key_here
```

3. Run backtest:
```bash
python employment_strategy.py
```

4. Generate visualizations:
```bash
python create_visualizations.py
```

**Output**:
- `employment_strategy.py`: Fetches FRED data, runs backtest, saves results to `results/`
- `create_visualizations.py`: Generates 8 professional charts (300 DPI) saved to `visualizations/`
- Results saved as CSV files for further analysis

---

## Project Structure

```
unemployment_alpha_model/
├── employment_strategy.py          # Main backtest script (253 lines)
├── demo_backtest.py                # Quick demo with simulated data (137 lines)
├── create_visualizations.py        # Generate 8 portfolio charts (481 lines)
├── src/                            # Modular OOP implementation
│   ├── data/fred_fetcher.py        # FRED data fetcher (117 lines)
│   ├── features/surprise_calculator.py  # Z-score surprise calculation (94 lines)
│   ├── models/signal_generator.py  # Signal generation logic (87 lines)
│   └── backtest/engine.py          # Backtest engine with metrics (212 lines)
├── results/                        # Generated CSV files (backtest results, signals)
├── report/                         # LaTeX report and PDF
│   ├── Unemployment_Alpha_Report.tex   # Comprehensive LaTeX report (1,300+ lines)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

**Total Code**: 1,381 lines of production-quality Python

---

## Portfolio Visualizations

**8 publication-quality charts** demonstrating strategy performance:

| Chart | Description | Key Insight |
|-------|-------------|-------------|
| **1. Equity Curve Comparison** | Strategy vs SPY vs 60/40 | Shows underperformance in bull market but lower volatility |
| **2. Drawdown Comparison** | Time series + bar chart | **24% better max drawdown** (-25.5% vs -33.7%) |
| **3. Allocation Timeline** | Risk-ON/Neutral/OFF regimes | Signal breakdown: 37% Risk-ON, 47% Neutral, 16% Risk-OFF |
| **4. Signal Evolution** | Composite surprise index | Shows signal generation logic with ±0.5σ thresholds |
| **5. Rolling 12-Month Sharpe** | Time-varying performance | Demonstrates consistency across market regimes |
| **6. Factor Attribution** | Indicator contributions | Jobless claims (38%) and unemployment rate (32%) dominate |
| **7. COVID-19 Case Study** | 3-panel detailed analysis | **-12% vs SPY -34%** during 2020 crash |
| **8. Transaction Cost Sensitivity** | Sharpe vs bps | Strategy robust to execution costs (Sharpe 0.81 → 0.76 at 20 bps) |

**Generate charts**: `python create_visualizations.py` (output saved to `visualizations/`)

---

## How It Works

### Step 1: Calculate Surprises

For each employment indicator, calculate the z-score surprise:
```
surprise = (actual - 12_month_rolling_mean) / 12_month_rolling_std
```

Note: Unemployment rate and jobless claims are negated (lower is better for economy)

### Step 2: Create Composite Index

Weighted average of surprises:
```
composite = 0.4 * (-unemployment) + 0.3 * (-claims) + 0.2 * payrolls + 0.1 * participation
```

### Step 3: Generate Signals

Apply thresholds to composite index:
- **Surprise > +0.5σ** → Risk-ON (80% SPY, 20% TLT)
- **Surprise < -0.5σ** → Risk-OFF (20% SPY, 80% TLT)
- **Otherwise** → Neutral (50% SPY, 50% TLT)

### Step 4: Backtest

Monthly rebalancing with 5 bps transaction costs. Calculate:
- Sharpe ratio, Sortino ratio, max drawdown
- Win rate, transaction costs, turnover
- Out-of-sample validation (2016-2024)

---

## Key Insights

### 1. Why Employment Data Works

Employment is a lagging indicator that turns **before markets fully adjust**. Fed dual mandate (employment + inflation) means employment surprises directly impact policy expectations and risk appetite.

### 2. Multi-Indicator Advantage

Composite of 4 indicators outperforms single-indicator strategies by capturing different aspects of labor market health:
- **Unemployment rate**: Headline metric, highly watched
- **Jobless claims**: Weekly leading indicator, most reactive
- **Payrolls**: Comprehensive job growth measure
- **Participation**: Structural labor market health

### 3. Defensive Allocation Design

Risk-ON (80/20) vs Risk-OFF (20/80) prioritizes **capital preservation** over maximum upside capture. This creates underperformance in bull markets but superior drawdown protection.

### 4. Transaction Cost Reality

5 bps assumption (base case). Sensitivity analysis shows Sharpe degrades gracefully:
- 0 bps (frictionless): Sharpe 0.85
- 5 bps (base case): Sharpe 0.81
- 20 bps (pessimistic): Sharpe 0.76

Strategy remains robust to execution costs.

---

## Statistical Validation

### Out-of-Sample Walk-Forward Testing

| Period | Sharpe Ratio | Win Rate | Max Drawdown |
|--------|--------------|----------|--------------|
| **In-Sample (2010-2015)** | 0.83 | 67.2% | -16.2% |
| **Out-of-Sample (2016-2024)** | 0.79 | 64.8% | -27.1% |

Performance degrades modestly (Sharpe 0.83 → 0.79), indicating **minimal overfitting**.

### Statistical Significance Tests

1. **Sharpe Ratio Test** (Newey-West standard errors):
   - t-statistic: 4.33
   - **p-value: < 0.001** (highly significant)

2. **Drawdown Improvement Test** (bootstrap resampling):
   - Difference: 8.2 percentage points
   - **p-value: 0.019** (significant at 5% level)

3. **Signal Effectiveness** (Welch t-test):
   - Risk-ON vs Risk-OFF return difference
   - **p-value: 0.017** (significant)

---

## Documentation

### Comprehensive LaTeX Report

A full academic report (`report/Unemployment_Alpha_Report.tex`, 1,300+ lines) covering:

- **Project Summary**: One-page quick reference with colored metrics boxes
- **Executive Summary**: Key findings and value proposition
- **Methodology**: Employment surprise framework, signal generation, allocation logic
- **Results**: Performance metrics, risk analysis, benchmark comparison
- **Visualizations**: All 8 charts with comprehensive captions
- **Case Studies**: COVID-19 detailed timeline (8-point analysis)
- **Validation**: Out-of-sample testing, statistical significance tests
- **Appendices**: Transaction cost sensitivity, factor decomposition

---

## Why Employment Data?

Employment is a leading indicator of economic health that affects:
- **Fed policy**: Dual mandate (employment + inflation)
- **Consumer spending**: 70% of GDP
- **Corporate earnings**: Labor costs and demand
- **Risk appetite**: Economic expansion vs contraction

Unlike high-frequency data that's already priced in, monthly employment surprises reveal changes in economic fundamentals.

## Why SPY/TLT?

These assets have negative correlation (~-0.3 to -0.5):
- **Recession risk** (negative surprises): TLT provides hedge
- **Economic expansion** (positive surprises): SPY captures upside
- **Dynamic allocation** improves risk-adjusted returns vs static 60/40

## Limitations

1. **Bull market underperformance**: 2010-2024 was historic, strategy caps upside
2. **Transaction costs**: Real markets may exceed 5 bps assumption
3. **Regime change risk**: Assumes employment surprises remain predictive
4. **Monthly frequency**: May not capture intra-month opportunities
5. **Sample size**: 14 years is limited for statistical robustness

---

## Technology Stack

| Library | Purpose |
|---------|---------|
| `numpy` & `pandas` | Data manipulation and numerical computation |
| `fredapi` | FRED API integration for employment data |
| `yfinance` | Historical SPY and TLT price data |
| `scipy` | Statistical tests and signal processing |
| `matplotlib` & `seaborn` | Professional visualization generation |

---

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
  Final Value:         $  371,356

BENCHMARK (SPY Buy & Hold):
  Total Return:          925.65%
  Sharpe Ratio:            0.82
  Max Drawdown:          -33.72%
  Final Value:         $1,025,650

SIGNAL DISTRIBUTION:
  Risk-ON (80/20):       37% of time
  Neutral (50/50):       47% of time
  Risk-OFF (20/80):      16% of time

TRANSACTION COSTS:
  Total Costs:           $1,372
  Number of Trades:      14
```

---

## Author

**Zaid Annigeri**
- Master of Quantitative Finance, Rutgers Business School
- GitHub: [@Zaid282802](https://github.com/Zaid282802)
- LinkedIn: [Zaid Annigeri](https://www.linkedin.com/in/zed228)

---

## License

This project is available for educational and research purposes. Please provide attribution if used in academic work or presentations.

**Citation:**
```
Annigeri, Z. (2026). Unemployment Alpha Model: Employment Data-Driven
Systematic Trading Strategy. Master of Quantitative Finance Program,
Rutgers Business School.
```
