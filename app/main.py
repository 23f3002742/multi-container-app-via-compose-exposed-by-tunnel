import os
from fastapi import FastAPI, HTTPException
from redis import Redis
from redis.exceptions import ConnectionError, RedisError

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


@app.post("/hit/{key}")
def hit(key: str):
    try:
        count = redis_client.incr(key)  # real Redis INCR
        return {"key": key, "count": count}
    except (ConnectionError, RedisError) as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/count/{key}")
def get_count(key: str):
    try:
        value = redis_client.get(key)
        count = int(value) if value is not None else 0
        return {"key": key, "count": count}
    except (ConnectionError, RedisError) as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/healthz")
def healthz():
    try:
        if redis_client.ping():
            return {"status": "ok", "redis": "up"}
        return {"status": "error", "redis": "down"}
    except (ConnectionError, RedisError):
        return {"status": "error", "redis": "down"}
