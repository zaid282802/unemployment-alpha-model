import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class BacktestEngine:

    def __init__(self, initial_capital=100000, transaction_cost_bps=5.0,
                 max_drawdown_limit=0.15, rebalance_freq='M'):
        self.initial_capital = initial_capital
        self.transaction_cost_bps = transaction_cost_bps / 10000
        self.max_drawdown_limit = max_drawdown_limit
        self.rebalance_freq = rebalance_freq

    def run(self, signals, start_date='2010-01-01', end_date='2024-12-31'):
        # Get price data
        prices = self._fetch_price_data(start_date, end_date)

        # Merge signals with prices
        df = signals.join(prices, how='right')
        df = df.fillna(method='ffill')

        # Run the backtest
        portfolio = self._initialize_portfolio(df)
        portfolio = self._simulate_trading(df, portfolio)

        # Calculate performance
        results = self._calculate_metrics(portfolio)

        return results

    def _fetch_price_data(self, start_date, end_date):
        try:
            import yfinance as yf

            spy = yf.download('SPY', start=start_date, end=end_date, progress=False)
            tlt = yf.download('TLT', start=start_date, end=end_date, progress=False)

            df = pd.DataFrame({
                'spy_price': spy['Adj Close'],
                'tlt_price': tlt['Adj Close']
            })

            df['spy_return'] = df['spy_price'].pct_change()
            df['tlt_return'] = df['tlt_price'].pct_change()

            return df

        except:
            print("Using simulated price data")
            return self._generate_demo_prices(start_date, end_date)

    def _generate_demo_prices(self, start_date, end_date):
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)

        spy_returns = np.random.normal(0.0003, 0.01, len(dates))
        spy_price = 100 * (1 + spy_returns).cumprod()

        tlt_returns = -0.3 * spy_returns + np.random.normal(0.0001, 0.005, len(dates))
        tlt_price = 100 * (1 + tlt_returns).cumprod()

        df = pd.DataFrame({
            'spy_price': spy_price,
            'tlt_price': tlt_price,
            'spy_return': spy_returns,
            'tlt_return': tlt_returns
        }, index=dates)

        return df

    def _initialize_portfolio(self, df):
        df['cash'] = self.initial_capital
        df['spy_shares'] = 0.0
        df['tlt_shares'] = 0.0
        df['portfolio_value'] = self.initial_capital
        df['turnover'] = 0.0
        df['transaction_costs'] = 0.0

        return df

    def _simulate_trading(self, df, portfolio):
        # Default to 50/50 if no weights specified
        if 'spy_weight' not in df.columns:
            df['spy_weight'] = 0.5
            df['tlt_weight'] = 0.5

        prev_spy_shares = 0.0
        prev_tlt_shares = 0.0
        prev_portfolio_value = self.initial_capital

        for i in range(len(df)):
            if i == 0:
                continue

            # Get current prices and weights
            spy_price = df['spy_price'].iloc[i]
            tlt_price = df['tlt_price'].iloc[i]
            spy_weight = df['spy_weight'].iloc[i]
            tlt_weight = df['tlt_weight'].iloc[i]

            # Calculate portfolio value from price changes
            current_value = (prev_spy_shares * spy_price +
                           prev_tlt_shares * tlt_price)

            # Check if we need to rebalance
            if self._should_rebalance(df.index[i], df.index[i-1]):
                # Target positions
                target_spy_value = current_value * spy_weight
                target_tlt_value = current_value * tlt_weight

                new_spy_shares = target_spy_value / spy_price
                new_tlt_shares = target_tlt_value / tlt_price

                # Calculate turnover
                turnover = (abs(new_spy_shares - prev_spy_shares) * spy_price +
                          abs(new_tlt_shares - prev_tlt_shares) * tlt_price)

                # Calculate transaction costs
                costs = turnover * self.transaction_cost_bps

                # Update
                df.loc[df.index[i], 'spy_shares'] = new_spy_shares
                df.loc[df.index[i], 'tlt_shares'] = new_tlt_shares
                df.loc[df.index[i], 'turnover'] = turnover
                df.loc[df.index[i], 'transaction_costs'] = costs
                df.loc[df.index[i], 'portfolio_value'] = current_value - costs

                prev_spy_shares = new_spy_shares
                prev_tlt_shares = new_tlt_shares
                prev_portfolio_value = current_value - costs
            else:
                # No rebalancing, just mark to market
                df.loc[df.index[i], 'spy_shares'] = prev_spy_shares
                df.loc[df.index[i], 'tlt_shares'] = prev_tlt_shares
                df.loc[df.index[i], 'portfolio_value'] = current_value
                prev_portfolio_value = current_value

        # Calculate returns
        df['strategy_return'] = df['portfolio_value'].pct_change()

        return df

    def _should_rebalance(self, current_date, prev_date):
        if self.rebalance_freq == 'M':
            return current_date.month != prev_date.month
        elif self.rebalance_freq == 'W':
            return current_date.week != prev_date.week
        else:
            return True

    def _calculate_metrics(self, portfolio):
        # Remove NaN values
        returns = portfolio['strategy_return'].dropna()

        # Basic metrics
        total_return = (portfolio['portfolio_value'].iloc[-1] / self.initial_capital - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(returns)) - 1) * 100

        # Risk metrics
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        sortino = (returns.mean() / returns[returns < 0].std()) * np.sqrt(252) if len(returns[returns < 0]) > 0 else 0

        # Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        # Transaction costs
        total_costs = portfolio['transaction_costs'].sum()
        avg_turnover = portfolio['turnover'].mean()

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'total_transaction_costs': total_costs,
            'avg_monthly_turnover': avg_turnover,
            'final_value': portfolio['portfolio_value'].iloc[-1],
            'n_trades': (portfolio['turnover'] > 0).sum()
        }

    def get_benchmark_comparison(self, portfolio_df, start_date, end_date):
        # Get SPY buy and hold
        try:
            import yfinance as yf
            spy = yf.download('SPY', start=start_date, end=end_date, progress=False)
            spy_returns = spy['Adj Close'].pct_change()
            spy_cumulative = (1 + spy_returns).cumprod()

            # Calculate SPY metrics
            spy_total = (spy_cumulative.iloc[-1] - 1) * 100
            spy_sharpe = (spy_returns.mean() / spy_returns.std()) * np.sqrt(252)

            spy_cum = (1 + spy_returns).cumprod()
            spy_dd = ((spy_cum - spy_cum.cummax()) / spy_cum.cummax()).min() * 100

            return {
                'spy_total_return': spy_total,
                'spy_sharpe': spy_sharpe,
                'spy_max_drawdown': spy_dd
            }
        except:
            return {}
