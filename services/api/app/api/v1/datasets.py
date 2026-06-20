from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.dataset import DatasetListResponse, DatasetResponse, UploadResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("sub", "")
    dataset = await DatasetService.upload_dataset(file, user_id, db)
    return UploadResponse(
        dataset_id=str(dataset.id),
        filename=dataset.original_filename,
        row_count=dataset.row_count,
    )


@router.get("", response_model=DatasetListResponse)
def list_datasets(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.dataset import Dataset as DatasetModel

    datasets = (
        db.query(DatasetModel)
        .order_by(DatasetModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(DatasetModel).count()
    return DatasetListResponse(
        items=[
            DatasetResponse(
                id=str(d.id),
                filename=d.filename,
                status=d.status,
                row_count=d.row_count,
                created_at=d.created_at,
            )
            for d in datasets
        ],
        total=total,
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.dataset import Dataset as DatasetModel

    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse(
        id=str(dataset.id),
        filename=dataset.filename,
        status=dataset.status,
        row_count=dataset.row_count,
        created_at=dataset.created_at,
    )


@router.post("/{dataset_id}/analyze")
def analyze_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = DatasetService.process_dataset(dataset_id, db)
    return {
        "message": "Analysis completed",
        "dataset_id": str(dataset.id),
        "status": dataset.status,
    }
