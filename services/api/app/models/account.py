import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.session import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    external_account_ref = Column(String(255), nullable=False)
    masked_account_ref = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True)
    account_age_days = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
