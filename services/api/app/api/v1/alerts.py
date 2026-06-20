from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.detection_event import DetectionEvent
from app.models.investigation import CaseEvidence, InvestigationCase
from app.schemas.alert import AlertListResponse, AlertResponse
from app.schemas.case import CaseCreate

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    total = db.query(DetectionEvent).count()
    alerts = (
        db.query(DetectionEvent)
        .order_by(DetectionEvent.created_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )
    return AlertListResponse(
        items=[
            AlertResponse(
                id=str(a.id),
                event_type=a.event_type,
                severity=a.severity,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                risk_score=a.risk_score,
                reason_codes=a.reason_codes_json or [],
                evidence=a.evidence_json or {},
                created_at=a.created_at,
            )
            for a in alerts
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(DetectionEvent).filter(DetectionEvent.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(
        id=str(alert.id),
        event_type=alert.event_type,
        severity=alert.severity,
        entity_type=alert.entity_type,
        entity_id=alert.entity_id,
        risk_score=alert.risk_score,
        reason_codes=alert.reason_codes_json or [],
        evidence=alert.evidence_json or {},
        created_at=alert.created_at,
    )


@router.post("/{alert_id}/create-case")
def create_case_from_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = db.query(DetectionEvent).filter(DetectionEvent.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    case = InvestigationCase(
        title=f"Case from alert: {alert.event_type}",
        severity=alert.severity,
        created_by=current_user.get("sub", ""),
        status="open",
        risk_score=alert.risk_score,
    )
    import uuid
    case.case_number = f"TG-{uuid.uuid4().hex[:8].upper()}"
    db.add(case)
    db.commit()
    db.refresh(case)

    evidence = CaseEvidence(
        case_id=case.id,
        event_id=alert.id,
        evidence_type="alert",
        description=f"Created from alert {alert.event_type} on {alert.entity_type}:{alert.entity_id}",
    )
    db.add(evidence)
    db.commit()

    return {
        "message": "Case created from alert",
        "case_id": str(case.id),
        "case_number": case.case_number,
    }
