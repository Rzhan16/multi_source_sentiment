import praw, pandas as pd, re, os
from datetime import datetime
from dotenv import load_dotenv
from models.enhanced_sentiment import EnhancedSentimentAnalyzer
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

    # ---------- helpers ----------
    def _clean(self, txt):
        return re.sub(r'http\S+|\[[^\]]+\]\([^)]+\)|[^\w\s]', '', str(txt))

    def _fetch_posts(self, sym, limit):
        rows=[]
        for p in self.reddit.subreddit('stocks+investing+wallstreetbets') \
                             .search(f'{sym} stock', limit=limit, time_filter='month'):
            rows.append({
                'title'      : p.title,
                'text'       : self._clean(f"{p.title} {p.selftext}"),
                'score'      : p.score,
                'created_utc': datetime.utcfromtimestamp(p.created_utc),
                'url'        : f'https://reddit.com{p.permalink}',
                'subreddit'  : p.subreddit.display_name
            })
        return pd.DataFrame(rows)

    # ---------- public ----------
    def analyze(self, sym, limit=120):
        df = self._fetch_posts(sym, limit)
        if df.empty:
            return dict(success=False, error=f"No Reddit posts for {sym}")

        df['sentiment'] = df.text.apply(self.enh.score)
        df = self.enh.filter_low_quality(df)

        # build daily series for plotting
        self._daily_series = df.set_index(pd.to_datetime(df.created_utc)) \
                               .sentiment.resample('D').mean()

        dist = df.sentiment.apply(lambda v: 'positive' if v>0 else ('negative' if v<0 else 'neutral')) \
                           .value_counts().to_dict()

        return dict(
            success=True,
            average_sentiment=float(df.sentiment.mean()),
            post_count=len(df),
            sentiment_distribution=dist,
            top_posts=df.nlargest(5, 'score').to_dict('records')
        )

    def daily_series(self):
        return self._daily_series
