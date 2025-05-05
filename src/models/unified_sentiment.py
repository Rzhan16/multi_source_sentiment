import numpy as np
import pandas as pd
from models.reddit_sentiment   import RedditSentimentAnalyzer
from models.twitter_sentiment  import TwitterSentimentAnalyzer
from models.news_sentiment     import NewsSentimentAnalyzer
from models.stock_data         import StockDataFetcher
from models.fundamentals       import FundamentalsFetcher

fund_fetcher    = FundamentalsFetcher()
reddit_analyzer  = RedditSentimentAnalyzer()
twitter_analyzer = TwitterSentimentAnalyzer()
news_analyzer    = NewsSentimentAnalyzer()
stock_fetcher    = StockDataFetcher()

def get_unified_sentiment(symbol: str,
                          window: int = 5,
                          include_twitter: bool = True) -> dict:
    # 1) Reddit
    rd = reddit_analyzer.analyze_sentiment(symbol)
    reddit_score = rd.get('average_sentiment', 0) if rd.get('success') else 0

    # 2) Twitter
    scores = {'reddit': reddit_score}
    if include_twitter:
        tw = twitter_analyzer.analyze_sentiment(symbol)
        scores['twitter'] = tw.get('average_sentiment', 0) if tw.get('success') else 0

    # 3) News
    nw = news_analyzer.analyze_sentiment(symbol)
    scores['news'] = nw.get('average_sentiment', 0) if nw.get('success') else 0

    average_sentiment = float(np.mean(list(scores.values())))

    # grab the time series from Reddit
    daily_sent   = rd.get('daily_sentiment', pd.Series(dtype=float))
    daily_counts = rd.get('daily_counts',    pd.Series(dtype=int))

    # strip timezone so it matches history_df
    if hasattr(daily_sent.index, 'tz') and daily_sent.index.tz is not None:
        daily_sent.index = daily_sent.index.tz_localize(None)
    if hasattr(daily_counts.index, 'tz') and daily_counts.index.tz is not None:
        daily_counts.index = daily_counts.index.tz_localize(None)

    # ——— VOLUME-WEIGHTING BLOCK (fix!)
    if not daily_counts.empty and daily_counts.max() > 0:
        weights  = daily_counts / daily_counts.max()
        weighted = daily_sent * weights
    else:
        weighted = daily_sent.copy()

    # now you can roll on `weighted`
    rm = weighted.rolling(window, min_periods=3).mean()
    rs = weighted.rolling(window, min_periods=3).std().fillna(0)

    # CI only where ≥5 posts
    valid = daily_counts.reindex(rm.index, fill_value=0) >= 5
    ci_lower = pd.Series(index=rm.index, data=np.nan)
    ci_upper = ci_lower.copy()
    ci_lower.loc[valid] = rm[valid] - rs[valid]
    ci_upper.loc[valid] = rm[valid] + rs[valid]

    # stock info & history
    price_res     = stock_fetcher.get_stock_data(symbol)
    current_price = price_res['data'].get('current_price', 0.0)
    currency      = price_res['data'].get('currency', 'USD')
    history_df    = stock_fetcher.history(symbol)

    # trend on smoothed series
    m = rm.dropna()
    if not m.empty:
        last = m.iloc[-1]
        trend = 'Bullish' if last > 0.2 else 'Bearish' if last < -0.2 else 'Neutral'
    else:
        trend = 'Neutral'

    return {
        'success'           : True,
        'average_sentiment' : average_sentiment,
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
