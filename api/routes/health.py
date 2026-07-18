from fastapi import APIRouter

from api.database import get_connection

router = APIRouter()


@router.get("/")
def health_check():
    """
    Simple liveness check.
    Also verifies DB access.
    """

    try:

        conn = get_connection()

        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            """
        ).fetchone()[0]

        conn.close()

        return {
            "status": "ok",
            "incidents_stored": count
        }

    except Exception as e:

        return {
            "status": "error",
            "detail": str(e)
        }