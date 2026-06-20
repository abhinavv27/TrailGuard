from datetime import datetime

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
