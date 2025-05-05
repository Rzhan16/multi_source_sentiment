# src/models/stock_data.py

import yfinance as yf, time
from requests.exceptions import HTTPError

class StockDataFetcher:
    def get_stock_data(self, sym, retries=3, delay=4):
        for i in range(retries):
            try:
                ticker = yf.Ticker(sym)
                info = ticker.info

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
