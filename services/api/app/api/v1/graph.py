from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.risk_assessment import AccountRiskAssessment
from app.models.transaction import Transaction
from app.schemas.graph import (
    GraphEdge,
    GraphExploreRequest,
    GraphExploreResponse,
    GraphNode,
    TraceRequest,
    TraceResponse,
)

router = APIRouter(prefix="/graph", tags=["graph"])


# Transactions reference an account by whichever id ingest stored: the upload
# path uses Account.id (UUID), the seed path uses external_account_ref. These
# helpers resolve an account (and build a node) from either, so the graph
# renders the real money trail regardless of which convention a dataset used.

def _resolve_account(db: Session, key: str):
    return (
        db.query(Account)
        .filter(or_(Account.id == key, Account.external_account_ref == key))
        .first()
    )


def _account_keys(account: Account) -> set:
    """Every id a transaction might use to reference this account."""
    return {str(account.id), str(account.external_account_ref)}


def _risk_for(db: Session, account: Account, cache: dict) -> str:
    if account.id in cache:
        return cache[account.id]
    ra = (
        db.query(AccountRiskAssessment)
        .filter(AccountRiskAssessment.account_id == account.id)
        .order_by(AccountRiskAssessment.created_at.desc())
        .first()
    )
    risk = ra.risk_level.lower() if ra and ra.risk_level else ""
    cache[account.id] = risk
    return risk


def _node(db: Session, key: str, cache: dict) -> GraphNode:
    account = _resolve_account(db, key)
    if not account:
        return GraphNode(id=key, label=key, type="account")
    return GraphNode(
        id=key,
        label=account.masked_account_ref or account.external_account_ref or key,
        type="account",
        risk=_risk_for(db, account, cache),
        metadata={"country": account.country},
    )


def _edge(txn: Transaction) -> GraphEdge:
    return GraphEdge(
        source=str(txn.sender_account_id),
        target=str(txn.receiver_account_id),
        label=f"{txn.amount} {txn.currency or ''}".strip(),
        type="suspicious" if txn.scenario else "normal",
        metadata={
            "transaction_id": str(txn.id),
            "amount": txn.amount,
            "currency": txn.currency,
        },
    )


def _expand(db: Session, start_keys: set, hops: int, direction: str):
    """BFS over the transaction graph in transaction-key space.

    direction: "both" (neighborhood), "source" (upstream senders),
    or "destination" (downstream receivers).
    """
    cache: dict = {}
    nodes: dict = {}
    edges = []
    visited = set(start_keys)
    current = set(start_keys)

    for _ in range(hops):
        if not current:
            break
        keys = list(current)
        if direction == "source":
            q = Transaction.receiver_account_id.in_(keys)
        elif direction == "destination":
            q = Transaction.sender_account_id.in_(keys)
        else:
            q = or_(
                Transaction.sender_account_id.in_(keys),
                Transaction.receiver_account_id.in_(keys),
            )
        txns = db.query(Transaction).filter(q).limit(500).all()

        next_level = set()
        for txn in txns:
            sid = str(txn.sender_account_id)
            rid = str(txn.receiver_account_id)
            if sid not in nodes:
                nodes[sid] = _node(db, sid, cache)
            if rid not in nodes:
                nodes[rid] = _node(db, rid, cache)
            edges.append(_edge(txn))
            for k in (sid, rid):
                if k not in visited:
                    next_level.add(k)
        visited |= next_level
        current = next_level

    return nodes, edges, cache


@router.post("/explore", response_model=GraphExploreResponse)
def explore_graph(
    request: GraphExploreRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account_id = request.account_id
    hops = request.hops or 2

    if not account_id:
        # Global graph exploration: most recent transactions.
        cache: dict = {}
        nodes: dict = {}
        edges = []
        txns = (
            db.query(Transaction)
            .order_by(Transaction.timestamp.desc())
            .limit(request.max_nodes or 50)
            .all()
        )
        for txn in txns:
            sid = str(txn.sender_account_id)
            rid = str(txn.receiver_account_id)
            if sid not in nodes:
                nodes[sid] = _node(db, sid, cache)
            if rid not in nodes:
                nodes[rid] = _node(db, rid, cache)
            edges.append(_edge(txn))
        return GraphExploreResponse(nodes=list(nodes.values()), links=edges)

    account = _resolve_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    nodes, edges, cache = _expand(db, _account_keys(account), hops, "both")
    if not nodes:
        # Isolated account: still return it as a single node.
        key = str(account.external_account_ref)
        nodes = {key: _node(db, key, cache)}
    return GraphExploreResponse(nodes=list(nodes.values()), links=edges)


@router.post("/trace-source", response_model=TraceResponse)
def trace_source(
    request: TraceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = _resolve_account(db, request.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    nodes, edges, cache = _expand(
        db, _account_keys(account), request.max_hops, "source"
    )
    if str(account.id) not in nodes and str(account.external_account_ref) not in nodes:
        key = str(account.external_account_ref)
        nodes[key] = _node(db, key, cache)
    return TraceResponse(path_nodes=list(nodes.values()), path_edges=edges)


@router.post("/trace-destination", response_model=TraceResponse)
def trace_destination(
    request: TraceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = _resolve_account(db, request.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    nodes, edges, cache = _expand(
        db, _account_keys(account), request.max_hops, "destination"
    )
    if str(account.id) not in nodes and str(account.external_account_ref) not in nodes:
        key = str(account.external_account_ref)
        nodes[key] = _node(db, key, cache)
    return TraceResponse(path_nodes=list(nodes.values()), path_edges=edges)
