from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.analysis_run import AnalysisRun

router = APIRouter(prefix="/analysis-runs", tags=["analysis-runs"])


@router.get("/{run_id}")
def get_analysis_run(
    run_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return {
        "id": run.id,
        "dataset_id": run.dataset_id,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "error_message": run.error_message,
        "metrics": run.metrics_json,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }
