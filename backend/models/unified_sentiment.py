import numpy as np
import pandas as pd

from .reddit_sentiment   import RedditSentimentAnalyzer
from .twitter_sentiment  import TwitterSentimentAnalyzer
from .news_sentiment     import NewsSentimentAnalyzer
from .stock_data         import StockDataFetcher
from .fundamentals       import FundamentalsFetcher

# one‑time objects
reddit_analyzer  = RedditSentimentAnalyzer()
twitter_analyzer = TwitterSentimentAnalyzer()
news_analyzer    = NewsSentimentAnalyzer()
stock_fetcher    = StockDataFetcher()
fund_fetcher     = FundamentalsFetcher()


def get_unified_sentiment(symbol: str,
                          window: int = 5,
                          include_twitter: bool = True) -> dict:
    """
    Return an aggregated sentiment + market snapshot for <symbol>.
    window = rolling‑mean window (days)
    include_twitter = toggle Twitter scrape to conserve free API quota
    """
    # ── 1) individual sources ──────────────────────────────────────────
    rd = reddit_analyzer.analyze_sentiment(symbol)
    tw = twitter_analyzer.analyze_sentiment(symbol) if include_twitter else {}
    nw = news_analyzer.analyze_sentiment(symbol)

    scores = {
        'reddit' : rd.get('average_sentiment', 0) if rd.get('success') else 0,
        'twitter': tw.get('average_sentiment', 0) if tw.get('success') else 0,
        'news'   : nw.get('average_sentiment', 0) if nw.get('success') else 0
    }
    average_sentiment = float(np.mean(list(scores.values())))

    # ── 2) Reddit daily series & counts ────────────────────────────────
    daily_sent   = rd.get('daily_sentiment', pd.Series(dtype=float))
    daily_counts = rd.get('daily_counts',    pd.Series(dtype=int))

    # drop timezone so it aligns with OHLC index
    if getattr(daily_sent.index, 'tz', None):
        daily_sent.index = daily_sent.index.tz_localize(None)
    if getattr(daily_counts.index, 'tz', None):
        daily_counts.index = daily_counts.index.tz_localize(None)

    # volume‑weighted sentiment
    if not daily_counts.empty and daily_counts.max() > 0:
        weights  = daily_counts / daily_counts.max()
        weighted = daily_sent * weights
    else:
        weighted = daily_sent.copy()

    # rolling mean / std → confidence interval
    rm = weighted.rolling(window, min_periods=3).mean()
    rs = weighted.rolling(window, min_periods=3).std().fillna(0)

    valid     = daily_counts.reindex(rm.index, fill_value=0) >= 5
    ci_lower  = pd.Series(np.nan, index=rm.index)
    ci_upper  = ci_lower.copy()
    ci_lower.loc[valid] = rm[valid] - rs[valid]
    ci_upper.loc[valid] = rm[valid] + rs[valid]

    # ── 3) market & fundamentals ───────────────────────────────────────
    price_res  = stock_fetcher.get_stock_data(symbol)
    history_df = stock_fetcher.history(symbol)
    fnd        = fund_fetcher.get_fundamentals(symbol)

    trend = 'Neutral'
    m = rm.dropna()
    if not m.empty:
        last = m.iloc[-1]
        if   last > 0.20: trend = 'Bullish'
        elif last < -0.20: trend = 'Bearish'

    return {
        'success'          : True,
        'average_sentiment': average_sentiment,
        'sources'          : scores,
        'daily_sentiment'  : weighted,
        'daily_counts'     : daily_counts,
        'rolling_mean'     : rm,
        'ci_lower'         : ci_lower,
        'ci_upper'         : ci_upper,
        'post_count'       : rd.get('post_count', 0),
        'trend'            : trend,
        'stock_history'    : history_df,
        'current_price'    : price_res['data'].get('current_price', 0),
        'currency'         : price_res['data'].get('currency', 'USD'),
        'pe'               : fnd['pe'],
        'eps'              : fnd['eps']
    }
