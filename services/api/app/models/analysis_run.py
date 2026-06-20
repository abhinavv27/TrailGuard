import uuid

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.sql import func

from app.db.session import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="pending",
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String(2000), nullable=True)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
