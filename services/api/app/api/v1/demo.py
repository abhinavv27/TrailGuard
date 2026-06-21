from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.analysis_run import AnalysisRun
from app.models.dataset import Dataset
from app.models.detection_event import DetectionEvent
from app.models.risk_assessment import AccountRiskAssessment
from app.models.transaction import Transaction

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/inject-scenario")
def inject_scenario(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=403, detail="Demo mode is disabled")

    import random
    import uuid
    from datetime import datetime, timedelta, timezone
    
    # Create a dummy dataset
    dataset = Dataset(
        user_id=current_user.get("sub", ""),
        filename="demo_scenario_injection.csv",
        original_filename="demo_scenario_injection.csv",
        file_size=1024,
        file_hash=uuid.uuid4().hex,
        row_count=20,
        status="analyzed",
    )
    db.add(dataset)
    db.flush()

    # Risk assessments and detection events require an analysis run (FK,
    # NOT NULL on assessments), so stand one up for the injected scenario.
    run = AnalysisRun(
        dataset_id=dataset.id,
        user_id=current_user.get("sub", ""),
        status="completed",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.flush()

    account_ids = []
    for i in range(5):
        account = Account(
            dataset_id=dataset.id,
            external_account_ref=f"DEMO-ACC-{i:04d}",
            masked_account_ref=f"****{i:04d}",
            country=random.choice(["US", "GB", "RU", "CN", "CH"]),
            account_age_days=random.randint(1, 365 * 3),
        )
        db.add(account)
        db.flush()
        account_ids.append(str(account.id))

    for _ in range(20):
        sender = random.choice(account_ids)
        receiver = random.choice([a for a in account_ids if a != sender])
        txn = Transaction(
            dataset_id=dataset.id,
            external_transaction_ref=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 720)),
            sender_account_id=sender,
            receiver_account_id=receiver,
            amount=round(random.uniform(100, 50000), 2),
            currency=random.choice(["USD", "EUR", "GBP"]),
            channel=random.choice(["wire", "ach", "crypto"]),
            sender_country=random.choice(["US", "GB", "RU", "CN", "CH"]),
            receiver_country=random.choice(["US", "GB", "RU", "CN", "CH"]),
            device_hash=uuid.uuid4().hex if random.random() > 0.5 else None,
            scenario=random.choice(["structuring", "rapid_movement", "high_velocity", None]),
        )
        db.add(txn)
    db.flush()

    for acc_id in account_ids:
        risk_score = round(random.uniform(0, 100), 2)
        assessment = AccountRiskAssessment(
            account_id=acc_id,
            analysis_run_id=run.id,
            risk_score=risk_score,
            risk_level="CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 30 else "LOW",
            component_scores_json={
                "velocity": round(random.uniform(0, 100), 2),
                "amount": round(random.uniform(0, 100), 2),
                "geography": round(random.uniform(0, 100), 2),
            },
            reason_codes_json=random.sample(
                ["HIGH_VELOCITY", "LARGE_AMOUNT", "GEOGRAPHIC_ANOMALY", "STRUCTURING_PATTERN", "NEW_ACCOUNT"],
                k=random.randint(1, 3),
            ),
        )
        db.add(assessment)
    db.flush()

    for acc_id in account_ids[:3]:
        event = DetectionEvent(
            dataset_id=dataset.id,
            analysis_run_id=run.id,
            event_type=random.choice(["structuring", "rapid_movement", "high_risk_geography"]),
            severity=random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            entity_type="account",
            entity_id=acc_id,
            risk_score=round(random.uniform(0, 100), 2),
            reason_codes_json=["DEMO_SCENARIO"],
            evidence_json={"source": "demo_injection"},
        )
        db.add(event)
    db.commit()

    return {
        "message": "Demo scenario injected",
        "accounts_created": len(account_ids),
        "transactions_created": 20,
    }
