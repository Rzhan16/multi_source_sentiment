import numpy as np
from .reddit_sentiment import RedditSentimentAnalyzer
from .twitter_sentiment import TwitterSentimentAnalyzer
from .news_sentiment import NewsSentimentAnalyzer

reddit  = RedditSentimentAnalyzer()
twitter = TwitterSentimentAnalyzer()
news    = NewsSentimentAnalyzer()

def get_unified_sentiment(symbol: str):
    sources = []

    # Reddit
    reddit_res = reddit.analyze(symbol)
    if reddit_res.get('success'):
        sources.append(reddit_res['average_sentiment'])

    # Twitter
    twitter_score = twitter.analyze(symbol)
    if twitter_score is not None:
        sources.append(twitter_score)

    # News
    news_score = news.analyze(symbol)
    if news_score is not None:
        sources.append(news_score)

    if not sources:
        return {
            'success': False,
            'error': 'No sentiment sources available.'
        }

    avg = float(np.mean(sources))
    return {
        'success': True,
        'average_sentiment': avg,
        'source_count': len(sources),
        'sources': {
            'reddit': reddit_res.get('average_sentiment'),
            'twitter': twitter_score,
            'news': news_score
        }
    }
