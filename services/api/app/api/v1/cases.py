from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.case import (
    CaseCreate,
    CaseDetailResponse,
    CaseNoteCreate,
    CaseNoteResponse,
    CaseResponse,
)
from app.reports.service import ReportService
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
def list_cases(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cases = CaseService.list_cases(db, skip=skip, limit=limit)
    return {
        "items": [
            CaseResponse(
                id=str(c.id),
                case_number=c.case_number,
                status=c.status,
                severity=c.severity,
                title=c.title,
                risk_score=c.risk_score,
                created_at=c.created_at,
            )
            for c in cases
        ],
        "total": len(cases),
    }


@router.post("", response_model=CaseResponse, status_code=201)
def create_case(
    data: CaseCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.get("sub", "")
    case = CaseService.create_case(data, user_id, db)
    return CaseResponse(
        id=str(case.id),
        case_number=case.case_number,
        status=case.status,
        severity=case.severity,
        title=case.title,
        risk_score=case.risk_score,
        created_at=case.created_at,
    )


@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseService.to_detail_response(case, db)


@router.patch("/{case_id}")
def update_case(
    case_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseService.update_case(case_id, updates, db)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "message": "Case updated",
        "case_id": case_id,
        "status": case.status,
    }


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=201)
def add_case_note(
    case_id: str,
    data: CaseNoteCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    user_id = current_user.get("sub", "")
    note = CaseService.add_note(case_id, user_id, data.content, db)
    return CaseNoteResponse(
        id=str(note.id),
        content=note.content,
        created_at=note.created_at,
    )


@router.post("/{case_id}/generate-report")
def generate_case_report(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    detail = CaseService.to_detail_response(case, db)
    case_data = {
        "case_number": detail.case_number,
        "status": detail.status,
        "severity": detail.severity,
        "title": detail.title,
        "risk_score": detail.risk_score,
        "created_at": detail.created_at.isoformat() if detail.created_at else None,
        "updated_at": detail.updated_at.isoformat() if detail.updated_at else None,
        "evidence": detail.evidence,
        "notes": detail.notes,
        "summary": f"Investigation case {detail.case_number}: {detail.title}",
    }
    report = ReportService.generate_report(case_data)
    return report


@router.get("/{case_id}/report")
def get_case_report(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(case_id, db)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    detail = CaseService.to_detail_response(case, db)
    case_data = {
        "case_number": detail.case_number,
        "status": detail.status,
        "severity": detail.severity,
        "title": detail.title,
        "risk_score": detail.risk_score,
        "created_at": detail.created_at.isoformat() if detail.created_at else None,
        "updated_at": detail.updated_at.isoformat() if detail.updated_at else None,
        "evidence": detail.evidence,
        "notes": detail.notes,
        "summary": f"Investigation case {detail.case_number}: {detail.title}",
    }
    report = ReportService.generate_report(case_data)
    return report
