from sqlalchemy.orm import Session

from app.models.analysis_run import AnalysisRun
from app.models.dataset import Dataset
from app.models.detection_event import DetectionEvent
from app.models.investigation import InvestigationCase
from app.models.transaction import Transaction
from app.schemas.dashboard import DashboardSummaryResponse


class DashboardService:

    @staticmethod
    def get_summary(db: Session, user_id: str | None = None) -> DashboardSummaryResponse:
        total_datasets = db.query(Dataset).count()
        total_transactions = db.query(Transaction).count()

        flagged_accounts = (
            db.query(DetectionEvent)
            .filter(DetectionEvent.entity_type == "account")
            .distinct(DetectionEvent.entity_id)
            .count()
        )

        active_cases = (
            db.query(InvestigationCase)
            .filter(InvestigationCase.status.in_(["open", "investigating"]))
            .count()
        )

        risk_distribution = {}
        from sqlalchemy import func as sa_func

        risk_counts = (
            db.query(
                DetectionEvent.severity,
                sa_func.count(DetectionEvent.id),
            )
            .group_by(DetectionEvent.severity)
            .all()
        )
        for severity, count in risk_counts:
            risk_distribution[severity] = count

        latest_alerts_raw = (
            db.query(DetectionEvent)
            .order_by(DetectionEvent.created_at.desc())
            .limit(10)
            .all()
        )
        latest_alerts = [
            {
                "id": str(a.id),
                "event_type": a.event_type,
                "severity": a.severity,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "risk_score": a.risk_score,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in latest_alerts_raw
        ]

        return DashboardSummaryResponse(
            total_transactions=total_transactions,
            total_datasets=total_datasets,
            flagged_accounts=flagged_accounts,
            active_cases=active_cases,
            risk_distribution=risk_distribution,
            latest_alerts=latest_alerts,
        )
