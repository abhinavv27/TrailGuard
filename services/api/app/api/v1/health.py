from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/ready", response_model=HealthResponse)
def readiness_check():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="ready" if db_ok else "degraded",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )
