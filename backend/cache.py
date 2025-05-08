import os, json, functools, redis

r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def cached(ttl: int = 90 * 60):      # default 90 min
    def wrap(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            key = f"{fn.__name__}:{json.dumps([args, kwargs], sort_keys=True)}"
            if (val := r.get(key)) is not None:
                return json.loads(val)
            val = fn(*args, **kwargs)
            r.setex(key, ttl, json.dumps(val, default=str))
            return val
        return inner
    return wrap
