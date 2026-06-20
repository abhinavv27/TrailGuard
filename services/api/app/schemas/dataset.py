from datetime import datetime

from pydantic import BaseModel


class DatasetResponse(BaseModel):
    id: str
    filename: str
    status: str
    row_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    items: list[DatasetResponse]
    total: int


class UploadResponse(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    errors: list[str] = []
