import os
import time
from functools import lru_cache
import tweepy
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# ensure VADER lexicon is available
nltk.download("vader_lexicon", quiet=True)
load_dotenv()

class TwitterSentimentAnalyzer:
    def __init__(self):
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.sia = SentimentIntensityAnalyzer()

    @lru_cache(maxsize=32)
    def analyze_sentiment(self, symbol: str, limit: int = 20) -> dict:
        """
        Fetch recent tweets for <symbol>, compute sentiment via VADER,
        with exponential backoff on rate limits, and return
        {success, average_sentiment, post_count, daily_sentiment}.
        """
        for attempt in range(3):
            try:
                query = f"{symbol} stock -is:retweet lang:en"
                resp = self.client.search_recent_tweets(
                    query=query,
                    max_results=limit,
                    tweet_fields=["created_at", "text"]
                )
                tweets = resp.data or []
                if not tweets:
                    return {"success": False, "error": "No tweets found"}

                times  = [t.created_at for t in tweets]
                scores = [self.sia.polarity_scores(t.text)["compound"] for t in tweets]

                df    = pd.DataFrame({"sentiment": scores}, index=pd.to_datetime(times))
                daily = df["sentiment"].resample("D").mean()

                return {
                    "success": True,
                    "average_sentiment": float(df["sentiment"].mean()),
                    "post_count": len(df),
                    "daily_sentiment": daily
                }

            except tweepy.TooManyRequests:
                time.sleep(2 ** attempt)
            except Exception as e:
                print(f"Twitter sentiment error: {e}")
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "Twitter rate-limit exceeded"}
