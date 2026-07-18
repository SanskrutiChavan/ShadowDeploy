from prometheus_client import (
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

import sqlite3
import logging

from config import DB_PATH

log = logging.getLogger("metrics")


# ── Prometheus Metrics ────────────────────────────────────

incidents_total = Gauge(
    "shadowdeploy_incidents_total",
    "Total number of incidents detected",
)

incidents_open = Gauge(
    "shadowdeploy_incidents_open",
    "Number of unresolved incidents",
)

incidents_by_severity = Gauge(
    "shadowdeploy_incidents_by_severity",
    "Incidents grouped by severity",
    ["severity"],
)

incidents_by_reason = Gauge(
    "shadowdeploy_incidents_by_reason",
    "Incidents grouped by Kubernetes failure reason",
    ["reason"],
)

pod_restarts = Gauge(
    "shadowdeploy_pod_restarts_total",
    "Total pod restarts across incidents",
)


def refresh_metrics():
    """
    Refresh all Prometheus gauges from SQLite.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        total = conn.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]

        open_incidents = conn.execute(
            "SELECT COUNT(*) FROM incidents WHERE resolved = 0"
        ).fetchone()[0]

        incidents_total.set(total)
        incidents_open.set(open_incidents)

        # Severity counts
        rows = conn.execute(
            """
            SELECT severity,
                   COUNT(*) AS cnt
            FROM incidents
            GROUP BY severity
            """
        )

        for row in rows:
            incidents_by_severity.labels(
                severity=row["severity"]
            ).set(row["cnt"])

        # Failure reason counts
        rows = conn.execute(
            """
            SELECT failure_reason,
                   COUNT(*) AS cnt
            FROM incidents
            GROUP BY failure_reason
            """
        )

        for row in rows:
            incidents_by_reason.labels(
                reason=row["failure_reason"]
            ).set(row["cnt"])

        # Total restarts
        restart_total = conn.execute(
            """
            SELECT COALESCE(
                SUM(restarts),
                0
            )
            FROM incidents
            """
        ).fetchone()[0]

        pod_restarts.set(restart_total)

        conn.close()

    except Exception as e:
        log.error(
            f"Metrics refresh failed: {e}"
        )