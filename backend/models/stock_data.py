import yfinance as yf
import time
from requests.exceptions import HTTPError

class StockDataFetcher:
    def get_stock_data(self, sym, retries=3, delay=4):
        for i in range(retries):
            try:
                ticker = yf.Ticker(sym)
                info   = ticker.info

                current_price = info.get('currentPrice')
                if current_price is None:
                    raise ValueError("No price data")

                return {
                    'success': True,
                    'data': {
                        'current_price': current_price,
                        'currency'     : info.get('currency', 'USD'),
                        'pe'           : info.get('trailingPE'),
                        'eps'          : info.get('trailingEps')
                    }
                }

            except HTTPError as e:
                if e.response.status_code == 429 and i < retries - 1:
                    time.sleep(delay)
                    continue
                return {'success': False, 'error': str(e)}

            except Exception as e:
                if i < retries - 1:
                    time.sleep(delay)
                    continue
                return {'success': False, 'error': str(e)}

    def history(self, sym: str, days: int = 30):
        """
        Fetch historical OHLC data for the past `days` days.
        Returns a pandas.DataFrame with a tz-naive DateTimeIndex.
        """
        df = yf.Ticker(sym).history(period=f"{days}d")
        # drop any timezone info so it can align with your daily_sent index
        if hasattr(df.index, 'tz') and df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        return df
