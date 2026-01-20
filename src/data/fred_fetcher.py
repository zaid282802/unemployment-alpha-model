import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FREDFetcher:

    SERIES_IDS = {
        'unemployment_rate': 'UNRATE',
        'initial_claims': 'ICSA',
        'continued_claims': 'CCSA',
        'nonfarm_payrolls': 'PAYEMS',
        'labor_participation': 'CIVPART',
    }

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.use_demo_mode = api_key is None

        if self.use_demo_mode:
            print("Running in DEMO MODE - using simulated data")

    def get_unemployment_data(self, start_date, end_date):
        if self.use_demo_mode:
            return self._generate_demo_data(start_date, end_date, 'unemployment')

        try:
            from fredapi import Fred
            fred = Fred(api_key=self.api_key)

            unrate = fred.get_series(self.SERIES_IDS['unemployment_rate'], start_date, end_date)
            civpart = fred.get_series(self.SERIES_IDS['labor_participation'], start_date, end_date)
            payrolls = fred.get_series(self.SERIES_IDS['nonfarm_payrolls'], start_date, end_date)

            df = pd.DataFrame({
                'date': unrate.index,
                'unemployment_rate': unrate.values,
                'participation_rate': civpart.reindex(unrate.index, method='ffill').values,
                'nonfarm_payrolls': payrolls.reindex(unrate.index, method='ffill').values
            })

            df.set_index('date', inplace=True)
            return df

        except ImportError:
            print("fredapi not installed, using demo data")
            return self._generate_demo_data(start_date, end_date, 'unemployment')
        except Exception as e:
            print(f"Error fetching data: {e}")
            return self._generate_demo_data(start_date, end_date, 'unemployment')

    def get_claims_data(self, start_date, end_date):
        if self.use_demo_mode:
            return self._generate_demo_data(start_date, end_date, 'claims')

        try:
            from fredapi import Fred
            fred = Fred(api_key=self.api_key)

            initial = fred.get_series(self.SERIES_IDS['initial_claims'], start_date, end_date)
            continued = fred.get_series(self.SERIES_IDS['continued_claims'], start_date, end_date)

            df = pd.DataFrame({
                'date': initial.index,
                'initial_claims': initial.values,
                'continued_claims': continued.reindex(initial.index, method='ffill').values
            })

            df.set_index('date', inplace=True)
            return df

        except ImportError:
            print("fredapi not installed, using demo data")
            return self._generate_demo_data(start_date, end_date, 'claims')
        except Exception as e:
            print(f"Error fetching data: {e}")
            return self._generate_demo_data(start_date, end_date, 'claims')

    def _generate_demo_data(self, start_date, end_date, data_type):
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        if data_type == 'unemployment':
            base_unrate = 5.0 + np.random.randn(len(dates)).cumsum() * 0.1
            base_unrate = np.clip(base_unrate, 3.5, 10.0)

            participation = 63.0 + np.random.randn(len(dates)).cumsum() * 0.05
            participation = np.clip(participation, 61.0, 67.0)

            payrolls = 150000 + np.random.randn(len(dates)).cumsum() * 1000

            return pd.DataFrame({
                'unemployment_rate': base_unrate,
                'participation_rate': participation,
                'nonfarm_payrolls': payrolls
            }, index=dates)

        elif data_type == 'claims':
            dates_weekly = pd.date_range(start=start_date, end=end_date, freq='W')

            initial = 250000 + np.random.randn(len(dates_weekly)) * 20000
            initial = np.clip(initial, 180000, 400000)

            continued = 2000000 + np.random.randn(len(dates_weekly)) * 150000
            continued = np.clip(continued, 1500000, 3000000)

            return pd.DataFrame({
                'initial_claims': initial,
                'continued_claims': continued
            }, index=dates_weekly)

        return pd.DataFrame()
