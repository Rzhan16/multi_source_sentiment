import yfinance as yf, time
from requests.exceptions import HTTPError

class StockDataFetcher:
    def get_stock_data(self, sym, retries=3, delay=4):
        for i in range(retries):
            try:
                t=yf.Ticker(sym)
                price=t.info.get('currentPrice')
                if price is None:
                    raise ValueError("No price data")
                return dict(success=True, data={
                    'current_price': price,
                    'currency'     : t.info.get('currency', 'USD')
                })
            except HTTPError as e:
                if e.response.status_code==429 and i<retries-1:
                    time.sleep(delay); continue
                return dict(success=False, error=str(e))
            except Exception as e:
                if i<retries-1:
                    time.sleep(delay); continue
                return dict(success=False, error=str(e))

    def history(self, sym, days=30):
        return yf.Ticker(sym).history(period=f'{days}d')
