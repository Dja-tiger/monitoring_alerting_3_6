import os
import random
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

APP_NAME = os.getenv("APP_NAME", "chat-demo")

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["app", "method", "path", "code"],
)
REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "Request latency",
    ["app", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

app = FastAPI(title="Demo chat service with RED metrics")


def record_metrics(path: str, method: str, status_code: int, duration: float) -> None:
    REQUEST_COUNTER.labels(app=APP_NAME, method=method, path=path, code=status_code).inc()
    REQUEST_DURATION.labels(app=APP_NAME, path=path).observe(duration)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response: Response
    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start
        record_metrics(request.url.path, request.method, 500, duration)
        raise
    duration = time.perf_counter() - start
    record_metrics(request.url.path, request.method, response.status_code, duration)
    return response


@app.get("/")
async def root() -> dict:
    return {"message": "chat backend ok"}


@app.get("/healthz")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/simulate")
async def simulate(load_ms: int = 100, error_rate: float = 0.0) -> dict:
    """
    Simulate workload for manual testing.
    - load_ms: sleep duration per request to influence latency.
    - error_rate: 0..1 probability of raising a 500 error.
    """
    if error_rate > 0 and random.random() < error_rate:
        # mimic an internal error
        raise RuntimeError("simulated failure")
    time.sleep(load_ms / 1000)
    return {"load_ms": load_ms, "error_rate": error_rate}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
