import pandas as pd
import yfinance as yf

class FundamentalsFetcher:
    def get_fundamentals(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        info   = ticker.info

        pe  = info.get("forwardPE") or info.get("trailingPE")
        eps = info.get("forwardEps") or info.get("trailingEps")

        raw_dates = info.get("earningsDate") or []
        earnings_dates = [pd.to_datetime(d).date() for d in raw_dates]

        return {
            "pe": pe,
            "eps": eps,
            "earnings_dates": earnings_dates
        }
