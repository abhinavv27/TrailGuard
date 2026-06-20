import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class GraphMetrics(Base):
    __tablename__ = "graph_metrics"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False, index=True)
    analysis_run_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=True)
    betweenness_centrality = Column(Float, default=0)
    in_degree_centrality = Column(Float, default=0)
    out_degree_centrality = Column(Float, default=0)
    in_degree = Column(Float, default=0)
    out_degree = Column(Float, default=0)
    in_total_value = Column(Float, default=0)
    out_total_value = Column(Float, default=0)
    in_unique_counterparties = Column(Float, default=0)
    out_unique_counterparties = Column(Float, default=0)
    in_cycle = Column(String(5), default="false")
    cycle_count = Column(Float, default=0)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
