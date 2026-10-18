"""Small Flask API used as the demo workload for the CI/CD + GitOps pipeline."""
import os
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")

# In-memory store: fine for a demo. Replace with a DB later if you want a bonus.
TASKS = []

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


@app.before_request
def start_timer():
    g.start_time = time.perf_counter()


@app.after_request
def record_metrics(response):
    # Use the route pattern (not the raw path) to keep label cardinality low.
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    if endpoint != "/metrics":
        elapsed = time.perf_counter() - g.get("start_time", time.perf_counter())
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()
    return response


@app.route("/")
def index():
    return jsonify(message="DevOps demo API", version=APP_VERSION)


@app.route("/health")
def health():
    """Used by Kubernetes liveness and readiness probes."""
    return jsonify(status="ok"), 200


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    return jsonify(TASKS)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="title is required"), 400
    task = {"id": len(TASKS) + 1, "title": title, "done": False}
    TASKS.append(task)
    return jsonify(task), 201


@app.route("/api/error")
def trigger_error():
    """Deliberately returns a 500 so you can demo error-rate alerts in Grafana."""
    return jsonify(error="simulated failure"), 500


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
