from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IncidentCreate(BaseModel):
    """
    Shape of data the watcher POSTs
    to save an incident.
    """

    pod_name: str
    namespace: str = "default"
    failure_reason: str

    root_cause: str = ""
    severity: str = "UNKNOWN"

    fix: str = ""
    rollback_cmd: str = ""
    prevention: str = ""

    raw_logs: str = ""
    raw_ai: str = ""

    restarts: int = 0


class IncidentResponse(BaseModel):
    """
    Shape of an incident returned
    by GET endpoints.
    """

    id: int

    pod_name: str
    namespace: str
    failure_reason: str

    root_cause: Optional[str] = None
    severity: str

    fix: Optional[str] = None
    rollback_cmd: Optional[str] = None
    prevention: Optional[str] = None

    restarts: int
    resolved: int

    created_at: str
    resolved_at: Optional[str] = None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """
    Aggregate counts.
    Used by Grafana dashboard.
    """

    total_incidents: int
    open_incidents: int
    resolved_incidents: int

    by_severity: dict
    by_reason: dict

    most_failing_pod: Optional[str] = None