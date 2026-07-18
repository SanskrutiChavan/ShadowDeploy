from fastapi import FastAPI
from fastapi.responses import Response

from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from agent.metrics import refresh_metrics
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db
from api.routes import (
    incidents,
    stats,
    health
)

import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S"
)

app = FastAPI(
    title="ShadowDeploy API",
    description="AI-powered Kubernetes incident store",
    version="1.0.0",
)

# Allow browser / Grafana access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    incidents.router,
    prefix="/api/incidents",
    tags=["Incidents"]
)

app.include_router(
    stats.router,
    prefix="/api/stats",
    tags=["Stats"]
)

app.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)


@app.on_event("startup")
def startup():
    """
    Initialize database
    when API starts.
    """

    init_db()


@app.get("/")
def root():
    """
    Root endpoint.
    """

    return {
        "service": "ShadowDeploy",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }
@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.
    """

    refresh_metrics()

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )