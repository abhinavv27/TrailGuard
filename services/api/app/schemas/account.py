from datetime import datetime

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: str
    external_account_ref: str
    masked_account_ref: str
    country: str | None = None
    risk_score: float = 0.0
    risk_level: str = "low"

    model_config = {"from_attributes": True}


class AccountTransactionResponse(BaseModel):
    transactions: list[dict] = []


class AccountRiskResponse(BaseModel):
    account: AccountResponse
    risk_assessment: dict | None = None
    reason_codes: list[str] = []


class AccountGraphResponse(BaseModel):
    nodes: list[dict] = []
    edges: list[dict] = []
