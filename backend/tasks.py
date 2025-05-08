import os, json, datetime
from celery import Celery
from backend.models.unified_sentiment import get_unified_sentiment
from backend.cache import r

broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("tasks", broker=broker, backend=broker)

@celery.task
def poll_symbol(symbol: str, window: int = 5, include_twitter: bool = True):
    snap = get_unified_sentiment(symbol, window, include_twitter)
    snap["ts"] = str(datetime.datetime.utcnow())
    r.publish(f"stream:{symbol}", json.dumps(snap, default=str))
