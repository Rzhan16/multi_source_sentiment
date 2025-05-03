import os, requests, statistics
from dotenv import load_dotenv; load_dotenv()
from textblob import TextBlob

BEARER = os.getenv("TWITTER_BEARER_TOKEN")

def get_twitter_sentiment(symbol, max_results=50):
    """
    Returns average polarity score for recent tweets containing <symbol>.
    """
    query   = f"{symbol} stock lang:en -is:retweet"
    headers = {"Authorization": f"Bearer {BEARER}"}
    params  = {"query": query, "max_results": max_results, "tweet.fields": "text"}

    url = "https://api.twitter.com/2/tweets/search/recent"
    resp = requests.get(url, headers=headers, params=params).json()
    tweets = [t["text"] for t in resp.get("data", [])]

    scores = [TextBlob(txt).sentiment.polarity for txt in tweets]
    return statistics.mean(scores) if scores else 0.0
