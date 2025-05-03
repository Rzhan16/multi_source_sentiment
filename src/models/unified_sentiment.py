import numpy as np
import pandas as pd
from models.reddit_sentiment   import RedditSentimentAnalyzer
from models.twitter_sentiment  import TwitterSentimentAnalyzer
from models.news_sentiment     import NewsSentimentAnalyzer
from models.stock_data         import StockDataFetcher

reddit_analyzer  = RedditSentimentAnalyzer()
twitter_analyzer = TwitterSentimentAnalyzer()
news_analyzer    = NewsSentimentAnalyzer()
stock_fetcher    = StockDataFetcher()

def get_unified_sentiment(symbol: str) -> dict:
    # --- fetch each source ---
    rd = reddit_analyzer.analyze_sentiment(symbol)
    tw = twitter_analyzer.analyze_sentiment(symbol)
    nw = news_analyzer.analyze_sentiment(symbol)

    scores = {
        'reddit': rd.get('average_sentiment', 0) if rd.get('success') else 0,
        'twitter': tw.get('average_sentiment', 0) if tw.get('success') else 0,
        'news': nw.get('average_sentiment', 0) if nw.get('success') else 0
    }
    avg_sent = float(np.mean(list(scores.values())))

    # --- daily sentiment & post‐counts from Reddit ---
    daily_sent   = rd.get('daily_sentiment', pd.Series(dtype=float))
    daily_counts = rd.get('daily_counts',    pd.Series(dtype=int))

    # --- weight by volume (downweight low‐count days) ---
    if not daily_counts.empty and daily_counts.max() > 0:
        weights = daily_counts / daily_counts.max()
        weighted = daily_sent * weights
    else:
        weighted = daily_sent.copy()

    # --- rolling stats for CI with a 5-day window, require ≥3 days ---
    window = 5
    rm = weighted.rolling(window, min_periods=3).mean()
    rs = weighted.rolling(window, min_periods=3).std().fillna(0)

    # --- only compute CI where we had ≥5 posts that day ---
    valid = daily_counts.reindex(rm.index, fill_value=0) >= 5
    ci_lower = pd.Series(index=rm.index, data=np.nan)
    ci_upper = pd.Series(index=rm.index, data=np.nan)
    ci_lower.loc[valid] = rm[valid] - rs[valid]
    ci_upper.loc[valid] = rm[valid] + rs[valid]

    # --- current price & history ---
    price_res     = stock_fetcher.get_stock_data(symbol)
    current_price = price_res.get('data', {}).get('current_price', 0.0)
    currency      = price_res.get('data', {}).get('currency', 'USD')
    history_df    = stock_fetcher.history(symbol)

    # --- simple trend on smoothed series ---
    trend = 'Neutral'
    if not rm.dropna().empty:
        last = rm.dropna().iloc[-1]
        if last > 0.2:    trend = 'Bullish'
        elif last < -0.2: trend = 'Bearish'

    return {
        'success'           : True,
        'average_sentiment' : avg_sent,
        'sources'           : scores,
        'daily_sentiment'   : weighted,
        'daily_counts'      : daily_counts,
        'rolling_mean'      : rm,
        'ci_lower'          : ci_lower,
        'ci_upper'          : ci_upper,
        'post_count'        : rd.get('post_count', 0),
        'trend'             : trend,
        'current_price'     : float(current_price),
        'currency'          : currency,
        'stock_history'     : history_df
    }
