# Employment Surprise Calculator
# Calculates z-scores for 4 employment indicators vs 12-month rolling mean/std
# Combines into weighted composite surprise index
# Negative unemployment/claims = positive surprise (good for economy)

import pandas as pd
import numpy as np
from scipy import stats

class SurpriseCalculator:

    def __init__(self, lookback_window=12, z_score_threshold=0.5):
        self.lookback_window = lookback_window
        self.z_score_threshold = z_score_threshold

    def calculate_composite_surprise(self, unemployment_data, claims_data):
        # Convert claims to monthly frequency
        claims_monthly = claims_data.resample('MS').mean()

        # Combine datasets
        df = unemployment_data.join(claims_monthly, how='left')
        df = df.ffill()

        # Calculate surprises for each indicator
        df['unrate_surprise'] = self._calculate_surprise(df['unemployment_rate'], invert=True)
        df['claims_surprise'] = self._calculate_surprise(df['initial_claims'], invert=True)

        if 'participation_rate' in df.columns:
            df['participation_surprise'] = self._calculate_surprise(df['participation_rate'])

        if 'nonfarm_payrolls' in df.columns:
            df['payrolls_surprise'] = self._calculate_surprise(df['nonfarm_payrolls'].diff())

        # Composite index - just average all the surprises
        surprise_cols = [col for col in df.columns if 'surprise' in col]
        df['composite_surprise'] = df[surprise_cols].mean(axis=1)

        # Apply Kalman filter to smooth out noise
        df['filtered_surprise'] = self._apply_kalman_filter(df['composite_surprise'])

        return df

    def _calculate_surprise(self, series, invert=False):
        # Use rolling window to get "expected" value
        rolling_mean = series.rolling(window=self.lookback_window, min_periods=self.lookback_window//2).mean()
        rolling_std = series.rolling(window=self.lookback_window, min_periods=self.lookback_window//2).std()

        # Calculate z-score
        surprise = (series - rolling_mean) / (rolling_std + 1e-8)

        if invert:
            surprise = -surprise

        return surprise

    def _apply_kalman_filter(self, series, process_variance=0.01):
        try:
            from pykalman import KalmanFilter

            # Drop NaN values for Kalman filter
            clean_series = series.dropna()

            if len(clean_series) < 2:
                # Not enough data, fall back to moving average
                return series.rolling(window=3, min_periods=1).mean()

            kf = KalmanFilter(
                transition_matrices=[1],
                observation_matrices=[1],
                initial_state_mean=0,
                initial_state_covariance=1,
                observation_covariance=1,
                transition_covariance=process_variance
            )

            state_means, _ = kf.filter(clean_series.values)

            # Create a series with the same index as the clean series
            filtered = pd.Series(state_means.flatten(), index=clean_series.index)

            # Reindex to match original series (will have NaN where original had NaN)
            return filtered.reindex(series.index)

        except (ImportError, Exception):
            # If pykalman not installed or fails, just use simple moving average
            return series.rolling(window=3, min_periods=1).mean()

    def get_signal_strength(self, surprise_value):
        if abs(surprise_value) < self.z_score_threshold:
            return 'WEAK'
        elif abs(surprise_value) < 1.5:
            return 'MODERATE'
        else:
            return 'STRONG'
