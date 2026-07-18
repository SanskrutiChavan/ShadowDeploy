import sqlite3
import os
import logging

from config import DB_PATH

log = logging.getLogger("database")


def get_connection() -> sqlite3.Connection:
    """
    Return a SQLite connection with Row factory enabled.
    """

    os.makedirs(
        os.path.dirname(DB_PATH),
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    # Safe for concurrent reads
    conn.execute(
        "PRAGMA journal_mode=WAL"
    )

    return conn


def init_db():
    """
    Create tables if they don't exist.
    Called once at API startup.
    """

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pod_name        TEXT    NOT NULL,
            namespace       TEXT    NOT NULL DEFAULT 'default',
            failure_reason  TEXT    NOT NULL,
            root_cause      TEXT,
            severity        TEXT    DEFAULT 'UNKNOWN',
            fix             TEXT,
            rollback_cmd    TEXT,
            prevention      TEXT,
            raw_logs        TEXT,
            raw_ai          TEXT,
            restarts        INTEGER DEFAULT 0,
            resolved        INTEGER DEFAULT 0,
            created_at      TEXT    DEFAULT (datetime('now')),
            resolved_at     TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_incidents_severity
        ON incidents(severity)
        """
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_incidents_created
        ON incidents(created_at DESC)
        """
    )

    conn.commit()
    conn.close()

    log.info(
        f"Database ready at {DB_PATH}"
    )


def save_incident(data: dict) -> int:
    """
    Insert one incident row.
    Returns the new row id.
    """

    conn = get_connection()

    analysis = data.get(
        "analysis",
        {}
    )

    cur = conn.execute(
        """
        INSERT INTO incidents
        (
            pod_name,
            namespace,
            failure_reason,
            root_cause,
            severity,
            fix,
            rollback_cmd,
            prevention,
            raw_logs,
            raw_ai,
            restarts
        )
        VALUES
        (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
        """,
        (
            data.get(
                "pod",
                "unknown"
            ),
            data.get(
                "namespace",
                "default"
            ),
            data.get(
                "reason",
                "unknown"
            ),
            analysis.get(
                "root_cause",
                ""
            ),
            analysis.get(
                "severity",
                "UNKNOWN"
            ),
            analysis.get(
                "fix",
                ""
            ),
            analysis.get(
                "rollback",
                ""
            ),
            analysis.get(
                "prevention",
                ""
            ),
            data.get(
                "logs",
                ""
            )[:5000],
            analysis.get(
                "raw",
                ""
            )[:5000],
            data.get(
                "restarts",
                0
            ),
        )
    )

    conn.commit()

    new_id = cur.lastrowid

    conn.close()

    log.info(
        f"Saved incident #{new_id} "
        f"for {data.get('pod')}"
    )

    return new_id