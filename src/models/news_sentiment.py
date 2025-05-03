# src/models/news_sentiment.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# ensure VADER lexicon is available
nltk.download('vader_lexicon', quiet=True)
load_dotenv()

class NewsSentimentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
        self.sia = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, symbol: str, limit: int = 20) -> dict:
        """
        Fetch recent news articles for <symbol>, compute sentiment via VADER,
        and return a dict matching Reddit/Twitter analyzer style.
        """
        try:
            params = {
                "q": f"{symbol} stock",
                "apiKey": self.api_key,
                "pageSize": limit,
                "language": "en",
                "sortBy": "relevancy"
            }
            resp = requests.get(self.base_url, params=params).json()
            articles = resp.get("articles", [])
            if not articles:
                return {"success": False, "error": "No articles found"}

            # build a time series if desired
            times = []
            scores = []
            for art in articles:
                text = art.get("title", "") + " " + art.get("description", "")
                score = self.sia.polarity_scores(text)["compound"]
                scores.append(score)
                ts = pd.to_datetime(art.get("publishedAt", None))
                times.append(ts)

            df = pd.DataFrame({"sentiment": scores}, index=pd.to_datetime(times))
            daily = df["sentiment"].resample("D").mean()

            return {
                "success": True,
                "average_sentiment": float(df["sentiment"].mean()),
                "post_count": len(df),
                "daily_sentiment": daily
            }

        except Exception as e:
            print(f"News sentiment error: {e}")
            return {"success": False, "error": str(e)}
