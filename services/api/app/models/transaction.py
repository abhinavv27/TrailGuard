import uuid

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.sql import func

from app.db.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    external_transaction_ref = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    sender_account_id = Column(
        String(36), ForeignKey("accounts.id"), nullable=False
    )
    receiver_account_id = Column(
        String(36), ForeignKey("accounts.id"), nullable=False
    )
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=True)
    channel = Column(String(100), nullable=True)
    sender_country = Column(String(100), nullable=True)
    receiver_country = Column(String(100), nullable=True)
    device_hash = Column(String(64), nullable=True)
    ip_hash = Column(String(64), nullable=True)
    scenario = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_transactions_timestamp", Transaction.timestamp)
Index("ix_transactions_sender", Transaction.sender_account_id)
Index("ix_transactions_receiver", Transaction.receiver_account_id)
Index("ix_transactions_amount", Transaction.amount)
