from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    event_type: str
    severity: str
    entity_type: str
    entity_id: str
    risk_score: float
    reason_codes: list[str] = []
    evidence: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int
