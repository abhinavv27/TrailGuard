import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.sql import func

from app.db.session import Base


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    analysis_run_id = Column(
        String(36), ForeignKey("analysis_runs.id"), nullable=True
    )
    event_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False, default="medium")
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(255), nullable=False)
    risk_score = Column(Float, nullable=False, default=0.0)
    reason_codes_json = Column(JSON, nullable=True)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
