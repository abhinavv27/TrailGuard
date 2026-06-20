import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.db.session import Base


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(50), unique=True, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default="open",
    )
    severity = Column(
        String(50),
        nullable=False,
        default="medium",
    )
    title = Column(String(500), nullable=False)
    primary_account_id = Column(
        String(36), ForeignKey("accounts.id"), nullable=True
    )
    risk_score = Column(Float, default=0.0)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class CaseEvidence(Base):
    __tablename__ = "case_evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(
        String(36), ForeignKey("investigation_cases.id"), nullable=False
    )
    event_id = Column(
        String(36), ForeignKey("detection_events.id"), nullable=True
    )
    evidence_type = Column(String(100), nullable=False)
    description = Column(String(2000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(
        String(36), ForeignKey("investigation_cases.id"), nullable=False
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
