import uuid

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.sql import func

from app.db.session import Base


class AccountRiskAssessment(Base):
    __tablename__ = "account_risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    analysis_run_id = Column(
        String(36), ForeignKey("analysis_runs.id"), nullable=False
    )
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(50), nullable=False, default="low")
    component_scores_json = Column(JSON, nullable=True)
    reason_codes_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TransactionRiskAssessment(Base):
    __tablename__ = "transaction_risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(
        String(36), ForeignKey("transactions.id"), nullable=False
    )
    analysis_run_id = Column(
        String(36), ForeignKey("analysis_runs.id"), nullable=False
    )
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(50), nullable=False, default="low")
    component_scores_json = Column(JSON, nullable=True)
    reason_codes_json = Column(JSON, nullable=True)
    detector_versions_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
