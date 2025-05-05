# src/models/fundamentals.py
import pandas as pd
import yfinance as yf

class FundamentalsFetcher:
    def get_fundamentals(self, symbol: str) -> dict:
        """
        Returns forward P/E, forward EPS, and upcoming earnings dates.
        """
        ticker = yf.Ticker(symbol)
        info   = ticker.info

        pe  = info.get("forwardPE") or info.get("trailingPE")
        eps = info.get("forwardEps") or info.get("trailingEps")

        # earningsDate is a list of timestamps
        raw_dates = info.get("earningsDate") or []
        earnings_dates = [pd.to_datetime(d).date() for d in raw_dates]

        return {
            "pe": pe,
            "eps": eps,
            "earnings_dates": earnings_dates
        }
