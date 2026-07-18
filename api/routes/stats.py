from fastapi import APIRouter

from api.database import get_connection
from api.models import StatsResponse

router = APIRouter()


@router.get(
    "/",
    response_model=StatsResponse
)
def get_stats():
    """
    Aggregate stats
    for Grafana and dashboards.
    """

    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM incidents"
    ).fetchone()[0]

    open_i = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE resolved=0"
    ).fetchone()[0]

    resolved = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE resolved=1"
    ).fetchone()[0]

    sev_rows = conn.execute(
        """
        SELECT
            severity,
            COUNT(*) AS cnt
        FROM incidents
        GROUP BY severity
        """
    ).fetchall()

    by_severity = {
        row["severity"]: row["cnt"]
        for row in sev_rows
    }

    reason_rows = conn.execute(
        """
        SELECT
            failure_reason,
            COUNT(*) AS cnt
        FROM incidents
        GROUP BY failure_reason
        """
    ).fetchall()

    by_reason = {
        row["failure_reason"]: row["cnt"]
        for row in reason_rows
    }

    top_pod_row = conn.execute(
        """
        SELECT
            pod_name,
            COUNT(*) AS cnt
        FROM incidents
        GROUP BY pod_name
        ORDER BY cnt DESC
        LIMIT 1
        """
    ).fetchone()

    top_pod = (
        top_pod_row["pod_name"]
        if top_pod_row
        else None
    )

    conn.close()

    return StatsResponse(
        total_incidents=total,
        open_incidents=open_i,
        resolved_incidents=resolved,
        by_severity=by_severity,
        by_reason=by_reason,
        most_failing_pod=top_pod,
    )