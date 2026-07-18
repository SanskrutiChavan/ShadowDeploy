from fastapi import APIRouter, HTTPException
from typing import List

from api.database import (
    get_connection,
    save_incident
)
from api.models import (
    IncidentCreate,
    IncidentResponse
)

router = APIRouter()


@router.post("/", status_code=201)
def create_incident(
    incident: IncidentCreate
):
    """
    Called by the watcher
    to save a new incident.
    """

    data = {
        "pod": incident.pod_name,
        "namespace": incident.namespace,
        "reason": incident.failure_reason,
        "restarts": incident.restarts,
        "logs": incident.raw_logs,
        "analysis": {
            "root_cause": incident.root_cause,
            "severity": incident.severity,
            "fix": incident.fix,
            "rollback": incident.rollback_cmd,
            "prevention": incident.prevention,
            "raw": incident.raw_ai,
        }
    }

    new_id = save_incident(data)

    return {
        "id": new_id,
        "status": "saved"
    }


@router.get(
    "/",
    response_model=List[IncidentResponse]
)
def list_incidents(
    limit: int = 50,
    severity: str = None
):
    """
    List incidents.
    Newest first.
    """

    conn = get_connection()

    if severity:

        rows = conn.execute(
            """
            SELECT *
            FROM incidents
            WHERE severity=?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                severity.upper(),
                limit
            )
        ).fetchall()

    else:

        rows = conn.execute(
            """
            SELECT *
            FROM incidents
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


@router.get("/{incident_id}")
def get_incident(
    incident_id: int
):
    """
    Get a single incident.
    """

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM incidents
        WHERE id=?
        """,
        (incident_id,)
    ).fetchone()

    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return dict(row)


@router.patch("/{incident_id}/resolve")
def resolve_incident(
    incident_id: int
):
    """
    Mark incident as resolved.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE incidents
        SET
            resolved=1,
            resolved_at=datetime('now')
        WHERE id=?
        """,
        (incident_id,)
    )

    conn.commit()
    conn.close()

    return {
        "id": incident_id,
        "status": "resolved"
    }