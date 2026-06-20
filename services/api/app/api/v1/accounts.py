from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.risk_assessment import AccountRiskAssessment
from app.models.transaction import Transaction
from app.schemas.account import (
    AccountGraphResponse,
    AccountResponse,
    AccountRiskResponse,
    AccountTransactionResponse,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    assessment = (
        db.query(AccountRiskAssessment)
        .filter(AccountRiskAssessment.account_id == account_id)
        .order_by(AccountRiskAssessment.created_at.desc())
        .first()
    )

    return AccountResponse(
        id=str(account.id),
        external_account_ref=account.external_account_ref,
        masked_account_ref=account.masked_account_ref,
        country=account.country,
        risk_score=assessment.risk_score if assessment else 0.0,
        risk_level=assessment.risk_level if assessment else "low",
    )


@router.get("/{account_id}/transactions", response_model=AccountTransactionResponse)
def get_account_transactions(
    account_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_account_id == account_id)
            | (Transaction.receiver_account_id == account_id)
        )
        .order_by(Transaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return AccountTransactionResponse(
        transactions=[
            {
                "id": str(t.id),
                "external_ref": t.external_transaction_ref,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "amount": t.amount,
                "currency": t.currency,
                "channel": t.channel,
                "sender_account_id": str(t.sender_account_id),
                "receiver_account_id": str(t.receiver_account_id),
                "scenario": t.scenario,
            }
            for t in transactions
        ]
    )


@router.get("/{account_id}/risk", response_model=AccountRiskResponse)
def get_account_risk(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    assessment = (
        db.query(AccountRiskAssessment)
        .filter(AccountRiskAssessment.account_id == account_id)
        .order_by(AccountRiskAssessment.created_at.desc())
        .first()
    )

    return AccountRiskResponse(
        account=AccountResponse(
            id=str(account.id),
            external_account_ref=account.external_account_ref,
            masked_account_ref=account.masked_account_ref,
            country=account.country,
            risk_score=assessment.risk_score if assessment else 0.0,
            risk_level=assessment.risk_level if assessment else "low",
        ),
        risk_assessment={
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "component_scores": assessment.component_scores_json,
            "created_at": assessment.created_at.isoformat() if assessment else None,
        }
        if assessment
        else None,
        reason_codes=assessment.reason_codes_json if assessment else [],
    )


@router.get("/{account_id}/graph", response_model=AccountGraphResponse)
def get_account_graph(
    account_id: str,
    hops: int = 1,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_account_id == account_id)
            | (Transaction.receiver_account_id == account_id)
        )
        .limit(100)
        .all()
    )

    nodes = {str(account.id): {"id": str(account.id), "label": account.masked_account_ref, "type": "account"}}
    edges = []

    for txn in transactions:
        sender_id = str(txn.sender_account_id)
        receiver_id = str(txn.receiver_account_id)
        if sender_id not in nodes:
            sender = db.query(Account).filter(Account.id == sender_id).first()
            nodes[sender_id] = {
                "id": sender_id,
                "label": sender.masked_account_ref if sender else sender_id,
                "type": "account",
            }
        if receiver_id not in nodes:
            receiver = db.query(Account).filter(Account.id == receiver_id).first()
            nodes[receiver_id] = {
                "id": receiver_id,
                "label": receiver.masked_account_ref if receiver else receiver_id,
                "type": "account",
            }
        edges.append({
            "source": sender_id,
            "target": receiver_id,
            "label": f"{txn.amount} {txn.currency or ''}",
            "metadata": {
                "transaction_id": str(txn.id),
                "amount": txn.amount,
                "currency": txn.currency,
                "timestamp": txn.timestamp.isoformat() if txn.timestamp else None,
                "scenario": txn.scenario,
            },
        })

    return AccountGraphResponse(
        nodes=list(nodes.values()),
        edges=edges,
    )
