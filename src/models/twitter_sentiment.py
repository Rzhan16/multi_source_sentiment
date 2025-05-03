# src/models/twitter_sentiment.py

import os
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

    def analyze_sentiment(self, symbol: str, limit: int = 50) -> dict:
        """
        Fetch recent tweets for <symbol>, compute sentiment via VADER,
        and return a dict matching RedditSentimentAnalyzer style.
        """
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

            # build a time series if desired
            times = [t.created_at for t in tweets]
            scores = [self.sia.polarity_scores(t.text)["compound"] for t in tweets]

            df = pd.DataFrame({"sentiment": scores}, index=pd.to_datetime(times))
            daily = df["sentiment"].resample("D").mean()

            return {
                "success": True,
                "average_sentiment": float(df["sentiment"].mean()),
                "post_count": len(df),
                "daily_sentiment": daily
            }

        except Exception as e:
            print(f"Twitter sentiment error: {e}")
            return {"success": False, "error": str(e)}
