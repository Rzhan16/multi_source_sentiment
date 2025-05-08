# backend/main.py
import os, json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ─── env + domain code ───────────────────────────────────────────────
load_dotenv()

from backend.models.unified_sentiment import get_unified_sentiment
from backend.models.fundamentals      import FundamentalsFetcher

fund_fetcher = FundamentalsFetcher()

# ─── FastAPI instance + CORS ─────────────────────────────────────────
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# 1) JSON REST endpoint  ─ /analyze  (same data your React front-end needs)
# --------------------------------------------------------------------
@app.post("/analyze")
async def analyze(request: Request):
    """
    Body JSON:
    {
      "stock_symbol": "AAPL",
      "window": 5,
      "twitter": true
    }
    """
    body = await request.json()
    sym             = body.get("stock_symbol", "").upper()
    window          = int(body.get("window", 5))
    include_twitter = bool(body.get("twitter", True))

    try:
        unified      = get_unified_sentiment(sym, window, include_twitter)
        fundamentals = {"pe": unified["pe"], "eps": unified["eps"]}

        # correlation: sentiment(t) vs return(t+1)
        hist    = unified["stock_history"]
        returns = hist["Close"].pct_change().shift(-1)
        corr    = float(unified["daily_sentiment"].corr(returns) or 0)

        return JSONResponse({
            "fundamentals": fundamentals,
            "sentiment": {
                "average_sentiment": unified["average_sentiment"],
                "trend"            : unified["trend"],
                "corr"             : corr,
                "sources"          : unified["sources"],
                # include series so the React chart can plot them
                "daily_sentiment"  : unified["daily_sentiment"].to_dict(),
                "rolling_mean"     : unified["rolling_mean"].to_dict(),
                "ci_lower"         : unified["ci_lower"].to_dict(),
                "ci_upper"         : unified["ci_upper"].to_dict(),
                "stock_history"    : unified["stock_history"]["Close"].to_dict()
            },
            "current_price": unified["current_price"],
            "currency"     : unified["currency"]
        })

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

# --------------------------------------------------------------------
# 2) OPTIONAL: WebSocket stream (you can wire this in later steps)
# --------------------------------------------------------------------
import redis, asyncio
from typing import DefaultDict
from collections import defaultdict

r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
SUBS: DefaultDict[str, set[WebSocket]] = defaultdict(set)

@app.websocket("/ws/{symbol}")
async def stream_sentiment(ws: WebSocket, symbol: str):
    """
    Streams JSON snapshots published to Redis channel `stream:<symbol>`.
    The Celery task in backend/tasks.py pushes updates every 30 s.
    """
    await ws.accept()
    SUBS[symbol].add(ws)

    pubsub = r.pubsub()
    pubsub.subscribe(f"stream:{symbol}")

    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await ws.send_text(msg["data"].decode("utf-8"))
    except WebSocketDisconnect:
        SUBS[symbol].discard(ws)
        pubsub.close()

# --------------------------------------------------------------------
# 3) Dev entry-point  (use uvicorn, not Flask’s built-in server)
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
async def root():
    return {"status": "ok", "msg": "Stock-Sentiment API"}
