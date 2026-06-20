from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("investigation_cases.id"), nullable=False)
    report_type = Column(String(50), nullable=False, server_default="investigation")
    format = Column(String(10), nullable=False, server_default="json")
    report_data_json = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Float, nullable=False, server_default="0")
    generated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("InvestigationCase", backref="reports")
