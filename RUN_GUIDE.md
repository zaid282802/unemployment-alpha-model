# Unemployment Alpha Model - How to Run Guide

##  Overview

This guide explains how to run all scripts in the correct order and what each one does.

---

##  Execution Flow Chart

```
┌─────────────────────────────────────────────────────────────┐
│                    START HERE                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Set up your FRED API key                           │
│  File: .env                                                 │
│  Action: Create file with: FRED_API_KEY=your_key_here       │
│  Why: Required to download employment data from FRED        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Run the main backtest                              │
│  Command: python employment_strategy.py                     │
│  Duration: ~30 seconds                                      │
│  Output:                                                    │
│    • results/employment_signals.csv (39 KB, monthly data)   │
│    • results/full_backtest_results.csv (831 KB, daily data) │
│    • Terminal output with performance metrics               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Generate visualizations                            │
│  Command: python create_visualizations.py                   │
│  Duration: ~45-60 seconds                                   │
│  Requires: Files from Step 2 must exist!                    │
│  Output:                                                    │
│    • visualizations/1_equity_curve_comparison.png           │
│    • visualizations/2_drawdown_comparison.png               │
│    • visualizations/3_allocation_timeline.png               │
│    • visualizations/4_signal_evolution.png                  │
│    • visualizations/5_rolling_sharpe.png                    │
│    • visualizations/6_factor_attribution.png                │
│    • visualizations/7_covid_case_study.png                  │
│    • visualizations/8_transaction_cost_sensitivity.png      │
│    Total: 8 PNG files at 300 DPI (~3.7 MB)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
                           DONE
```

---

##  File Dependencies

### What Each Script Needs:

#### `employment_strategy.py`
**Dependencies:**
-  `.env` file with FRED API key
-  Internet connection (to download FRED data)
-  Python packages: pandas, numpy, fredapi, yfinance, python-dotenv, scipy

**Creates:**
- `results/employment_signals.csv`
- `results/full_backtest_results.csv`

---

#### `create_visualizations.py`
**Dependencies:**
-  `results/employment_signals.csv` (from Step 2)
-  `results/full_backtest_results.csv` (from Step 2)
-  Python packages: pandas, numpy, matplotlib, seaborn

**Creates:**
- All 8 PNG files in `visualizations/` folder

---

##  Quick Start Commands

### Full Pipeline (Run All Steps):
```bash
# Navigate to project folder
cd "C:\Users\moham\Documents\MQF\projects\projects_git\unemployment_alpha_model"

# Step 1: Create .env file (one-time setup)
echo FRED_API_KEY=dfbef93f936911dc5c9bd9ec1c6ed4dc > .env

# Step 2: Run backtest (downloads data, generates signals)
python employment_strategy.py

# Step 3: Create visualizations
python create_visualizations.py

```
---

## What Each File Does

### Main Scripts:

| File | Purpose | Runtime | Output |
|------|---------|---------|--------|
| `employment_strategy.py` | Downloads FRED data, calculates signals, runs backtest | ~30s | 2 CSV files |
| `create_visualizations.py` | Reads CSV files, creates 8 professional charts | ~60s | 8 PNG files |
| `demo_backtest.py` | Simplified demonstration version | ~10s | Terminal output only |
| `kalman_filter.py` | Signal smoothing (called by other scripts) | N/A | Helper module |
| `statistical_tests.py` | Newey-West, Welch t-test (called by others) | N/A | Helper module |

### Data Files:

| File | Size | Rows | Columns | Description |
|------|------|------|---------|-------------|
| `results/employment_signals.csv` | 39 KB | ~180 | 15 | Monthly employment indicators and allocation weights |
| `results/full_backtest_results.csv` | 831 KB | ~3,700 | 12 | Daily portfolio returns, prices, and cumulative performance |

### Visualizations:

| Chart | Filename | Purpose |
|-------|----------|---------|
| 1 | `1_equity_curve_comparison.png` | Strategy vs SPY cumulative returns |
| 2 | `2_drawdown_comparison.png` | Underwater equity curves |
| 3 | `3_allocation_timeline.png` | SPY/TLT weights over time |
| 4 | `4_signal_evolution.png` | Composite signal with thresholds |
| 5 | `5_rolling_sharpe.png` | 12-month rolling Sharpe ratio |
| 6 | `6_factor_attribution.png` | Z-score surprises for 4 indicators |
| 7 | `7_covid_case_study.png` | COVID-19 period deep dive (2020) |
| 8 | `8_transaction_cost_sensitivity.png` | Sharpe and returns vs transaction costs |

---

## Data Flow Diagram

```
FRED API                                    Yahoo Finance
   │                                              │
   │  (UNRATE, ICSA,                              │ (SPY/TLT
   │  PAYEMS, CIVPART)                            │  prices)
   │                                              │
   └──────────────┬───────────────────────────────┘
                  │
                  ↓
        ┌─────────────────────┐
        │ employment_strategy │
        │       .py           │
        └─────────────────────┘
                  │
                  ├──→ results/employment_signals.csv
                  │    (Monthly: indicators, z-scores, weights)
                  │
                  └──→ results/full_backtest_results.csv
                       (Daily: prices, returns, portfolio value)

                  ↓
        ┌─────────────────────┐
        │create_visualizations│
        │       .py           │
        └─────────────────────┘
                  │
                  ├──→ visualizations/1_equity_curve_comparison.png
                  ├──→ visualizations/2_drawdown_comparison.png
                  ├──→ visualizations/3_allocation_timeline.png
                  ├──→ visualizations/4_signal_evolution.png
                  ├──→ visualizations/5_rolling_sharpe.png
                  ├──→ visualizations/6_factor_attribution.png
                  ├──→ visualizations/7_covid_case_study.png
                  └──→ visualizations/8_transaction_cost_sensitivity.png
```
---