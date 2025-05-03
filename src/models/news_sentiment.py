import os, requests, statistics
from dotenv import load_dotenv; load_dotenv()
from textblob import TextBlob

API_KEY = os.getenv("NEWS_API_KEY")

def get_news_sentiment(symbol, max_articles=30):
    url=f"https://newsapi.org/v2/everything?q={symbol}&language=en&pageSize={max_articles}&apiKey={API_KEY}"
    articles = requests.get(url).json().get("articles", [])
    texts = [(a.get("description") or a["title"]) for a in articles]

    scores=[TextBlob(t).sentiment.polarity for t in texts if t]
    return statistics.mean(scores) if scores else 0.0
