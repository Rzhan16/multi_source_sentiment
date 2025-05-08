import os
import re
import pandas as pd
import praw
from datetime import datetime
from dotenv import load_dotenv
from .enhanced_sentiment import EnhancedSentimentAnalyzer

load_dotenv()

class RedditSentimentAnalyzer:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.enh = EnhancedSentimentAnalyzer()
        self._daily_series = pd.Series(dtype=float)

    def _clean(self, txt: str) -> str:
        return re.sub(r'http\S+|\[[^\]]+\]\([^)]+\)|[^\w\s]', '', str(txt))

    def _fetch_posts(self, symbol: str, limit: int) -> pd.DataFrame:
        rows = []
        for post in self.reddit.subreddit('stocks+investing+wallstreetbets') \
                               .search(f'{symbol} stock', limit=limit, time_filter='month'):
            rows.append({
                'title': post.title,
                'text': self._clean(f"{post.title} {post.selftext}"),
                'score': post.score,
                'created_utc': datetime.utcfromtimestamp(post.created_utc),
                'url': f'https://reddit.com{post.permalink}',
                'subreddit': post.subreddit.display_name
            })
        return pd.DataFrame(rows)

    def analyze_sentiment(self, symbol: str, limit: int = 120) -> dict:
        df = self._fetch_posts(symbol, limit)
        if df.empty:
            return {'success': False, 'error': f'No Reddit posts for {symbol}'}

        # score & filter
        df['sentiment'] = df['text'].apply(self.enh.score)
        df = self.enh.filter_low_quality(df)

        # build daily sentiment & post‐counts
        df['date'] = pd.to_datetime(df['created_utc'])
        daily_sent  = df.set_index('date')['sentiment'].resample('D').mean()
        daily_count = df.set_index('date')['sentiment'].resample('D').count()
        self._daily_series = daily_sent

        # distribution & top posts
        dist = (
            df['sentiment']
              .apply(lambda v: 'positive' if v>0 else ('negative' if v<0 else 'neutral'))
              .value_counts().to_dict()
        )
        top = df.nlargest(5, 'score').to_dict('records')

        return {
            'success'               : True,
            'average_sentiment'     : float(df['sentiment'].mean()),
            'post_count'            : len(df),
            'sentiment_distribution': dist,
            'top_posts'             : top,
            'daily_sentiment'       : daily_sent,
            'daily_counts'          : daily_count
        }

    def daily_series(self) -> pd.Series:
        return self._daily_series
