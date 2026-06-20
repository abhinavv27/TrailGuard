import uuid

from sqlalchemy.orm import Session

from app.models.investigation import CaseEvidence, CaseNote, InvestigationCase
from app.schemas.case import CaseCreate, CaseDetailResponse, CaseNoteResponse


class CaseService:

    @staticmethod
    def create_case(data: CaseCreate, user_id: str, db: Session) -> InvestigationCase:
        case = InvestigationCase(
            title=data.title,
            primary_account_id=data.primary_account_id,
            severity=data.severity,
            created_by=user_id,
            status="open",
        )
        case_number = f"TG-{uuid.uuid4().hex[:8].upper()}"
        while db.query(InvestigationCase).filter(
            InvestigationCase.case_number == case_number
        ).first():
            case_number = f"TG-{uuid.uuid4().hex[:8].upper()}"
        case.case_number = case_number
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_case(case_id: str, db: Session) -> InvestigationCase | None:
        return db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()

    @staticmethod
    def list_cases(
        db: Session, skip: int = 0, limit: int = 20
    ) -> list[InvestigationCase]:
        return (
            db.query(InvestigationCase)
            .order_by(InvestigationCase.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_case(
        case_id: str, updates: dict, db: Session
    ) -> InvestigationCase | None:
        case = CaseService.get_case(case_id, db)
        if not case:
            return None
        for key, value in updates.items():
            if hasattr(case, key):
                setattr(case, key, value)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def add_note(
        case_id: str, user_id: str, content: str, db: Session
    ) -> CaseNote:
        note = CaseNote(case_id=case_id, user_id=user_id, content=content)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_notes(case_id: str, db: Session) -> list[CaseNote]:
        return (
            db.query(CaseNote)
            .filter(CaseNote.case_id == case_id)
            .order_by(CaseNote.created_at.desc())
            .all()
        )

    @staticmethod
    def add_evidence(
        case_id: str,
        event_id: str | None,
        evidence_type: str,
        description: str | None,
        db: Session,
    ) -> CaseEvidence:
        evidence = CaseEvidence(
            case_id=case_id,
            event_id=event_id,
            evidence_type=evidence_type,
            description=description,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def get_evidence(case_id: str, db: Session) -> list[CaseEvidence]:
        return (
            db.query(CaseEvidence)
            .filter(CaseEvidence.case_id == case_id)
            .all()
        )

    @staticmethod
    def to_detail_response(
        case: InvestigationCase, db: Session
    ) -> CaseDetailResponse:
        evidence = CaseService.get_evidence(str(case.id), db)
        notes = CaseService.get_notes(str(case.id), db)
        return CaseDetailResponse(
            id=str(case.id),
            case_number=case.case_number,
            status=case.status,
            severity=case.severity,
            title=case.title,
            primary_account_id=str(case.primary_account_id) if case.primary_account_id else None,
            risk_score=case.risk_score,
            created_by=str(case.created_by) if case.created_by else None,
            assigned_to=str(case.assigned_to) if case.assigned_to else None,
            evidence=[{"id": str(e.id), "type": e.evidence_type, "description": e.description} for e in evidence],
            notes=[{"id": str(n.id), "content": n.content, "created_at": n.created_at.isoformat()} for n in notes],
            created_at=case.created_at,
            updated_at=case.updated_at,
        )
