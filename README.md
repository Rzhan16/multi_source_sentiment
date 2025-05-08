# Multi-Source Stock Sentiment Dashboard

A real-time dashboard that combines market data, fundamentals, and sentiment from Reddit, Twitter & News — powered by FastAPI, Celery, Redis, React & Recharts.

---

##  Features

- **Live updates via WebSockets** — push snapshots every 30 s from a Celery task  
- **Aggregated sentiment** from Reddit, Twitter (optional) and News with VADER + custom enhancements  
- **Price overlay** — historical OHLC plotted alongside sentiment trend & confidence band  
- **Fundamentals panel** — P/E, EPS & upcoming earnings fetched from Yahoo! Finance  
- **Caching & rate-limit handling** — Redis + exponential back-off keep you inside free-tier API quotas  

---

##  Architecture
┌────────────┐ ┌──────────────┐ ┌────────────┐
│ Frontend │ ↔ WS │ FastAPI │ ↔📦 Celery │
│ (React + │ │ Backend │ │ Worker │
│ Recharts) │ │ │ └────────────┘
└────────────┘ │ │ │
│ │ ↓ publishes
│ │ Redis Pub/Sub
└──────────────┘ ↑
▲ ▲ Redis KV
│ │
│ └─ /analyze JSON endpoint
│
Browser

---

##  Tech Stack

- **Backend**:  
  - [FastAPI](https://fastapi.tiangolo.com/) (REST + WebSockets)  
  - [Celery](https://docs.celeryq.dev/) (periodic polling)  
  - [Redis](https://redis.io/) (caching & pub/sub)  
- **Sentiment Analysis**:  
  - VADER (NLTK) + TF-IDF + Random Forest (custom `EnhancedSentimentAnalyzer`)  
  - Reddit via [PRAW](https://praw.readthedocs.io/)  
  - Twitter via [tweepy](https://docs.tweepy.org/)  
  - News via [NewsAPI](https://newsapi.org/)  
- **Data & Fundamentals**:  
  - [yfinance](https://pypi.org/project/yfinance/) for price & P/E, EPS, earnings dates  
- **Frontend**:  
  - [React](https://reactjs.org/) + [Vite](https://vitejs.dev/)  
  - [Recharts](https://recharts.org/) for charting  
- **Deployment**:  
  - [Render](https://render.com/) with a single `render.yaml`  

---

## Getting Started

### Prerequisites

- [Python 3.11+](https://www.python.org/)  
- [Node.js 18+ & npm](https://nodejs.org/)  
- [Redis](https://redis.io/) (local or remote)  
- **API Keys**:
  - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`  
  - `TWITTER_BEARER_TOKEN`  
  - `NEWS_API_KEY`  

### Clone & Install

```bash
git clone https://github.com/Rzhan16/multi_source_sentiment.git
cd multi_source_sentiment

# Backend Python deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend deps
npm --prefix frontend install
