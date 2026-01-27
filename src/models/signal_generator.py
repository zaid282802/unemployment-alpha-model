# Signal Generator
# Converts composite surprise index into Risk-ON/Neutral/Risk-OFF signals
# Thresholds: +0.5σ (Risk-ON), -0.5σ (Risk-OFF), else Neutral
# Maps signals to SPY/TLT allocation weights

import pandas as pd
import numpy as np

class SignalGenerator:

    def __init__(self, long_threshold=0.5, short_threshold=-0.5, use_regime_filter=False):
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.use_regime_filter = use_regime_filter

    def generate_signals(self, surprise_data):
        df = surprise_data.copy()

        # Use filtered surprise if available, otherwise use composite
        signal_col = 'filtered_surprise' if 'filtered_surprise' in df.columns else 'composite_surprise'

        # Generate signals based on thresholds
        df['raw_signal'] = 0
        df.loc[df[signal_col] > self.long_threshold, 'raw_signal'] = 1    # Good news = risk on
        df.loc[df[signal_col] < self.short_threshold, 'raw_signal'] = -1  # Bad news = risk off

        # Apply regime filter if enabled
        if self.use_regime_filter:
            df['regime'] = self._identify_regime(df[signal_col])
            df['signal'] = df['raw_signal'] * df['regime']
        else:
            df['signal'] = df['raw_signal']

        # Map to positions
        df['position'] = df['signal'].map({
            1: 'LONG_RISK_ON',
            -1: 'LONG_RISK_OFF',
            0: 'NEUTRAL'
        })

        # Calculate allocation weights
        df = self._generate_allocation(df)

        return df

    def _identify_regime(self, surprise_series, lookback=6):
        # Check if market is in high volatility regime
        vol = surprise_series.rolling(window=lookback).std()

        # Only trade in normal volatility regimes
        regime = (vol < vol.quantile(0.8)).astype(int)

        return regime

    def _generate_allocation(self, df):
        # Simple allocation based on signal
        df['spy_weight'] = 0.0
        df['tlt_weight'] = 0.0

        # Risk-on: 80% SPY, 20% TLT
        df.loc[df['signal'] == 1, 'spy_weight'] = 0.8
        df.loc[df['signal'] == 1, 'tlt_weight'] = 0.2

        # Risk-off: 20% SPY, 80% TLT
        df.loc[df['signal'] == -1, 'spy_weight'] = 0.2
        df.loc[df['signal'] == -1, 'tlt_weight'] = 0.8

        # Neutral: 50/50
        df.loc[df['signal'] == 0, 'spy_weight'] = 0.5
        df.loc[df['signal'] == 0, 'tlt_weight'] = 0.5

        return df

    def get_signal_summary(self, signals_df):
        total_signals = len(signals_df)
        risk_on = (signals_df['signal'] == 1).sum()
        risk_off = (signals_df['signal'] == -1).sum()
        neutral = (signals_df['signal'] == 0).sum()

        return {
            'total': total_signals,
            'risk_on': risk_on,
            'risk_off': risk_off,
            'neutral': neutral,
            'risk_on_pct': risk_on / total_signals * 100,
            'risk_off_pct': risk_off / total_signals * 100
        }
