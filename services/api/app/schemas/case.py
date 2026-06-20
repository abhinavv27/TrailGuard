from datetime import datetime

from pydantic import BaseModel


class CaseCreate(BaseModel):
    title: str
    primary_account_id: str | None = None
    severity: str = "medium"


class CaseResponse(BaseModel):
    id: str
    case_number: str
    status: str
    severity: str
    title: str
    risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseDetailResponse(BaseModel):
    id: str
    case_number: str
    status: str
    severity: str
    title: str
    primary_account_id: str | None = None
    risk_score: float
    created_by: str | None = None
    assigned_to: str | None = None
    evidence: list[dict] = []
    notes: list[dict] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CaseNoteCreate(BaseModel):
    content: str


class CaseNoteResponse(BaseModel):
    id: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
