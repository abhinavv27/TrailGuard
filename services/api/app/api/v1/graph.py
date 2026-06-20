from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.account import Account
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


@router.post("/explore", response_model=GraphExploreResponse)
def explore_graph(
    request: GraphExploreRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account_id = request.account_id
    hops = request.hops or 2
    if not account_id:
        return GraphExploreResponse(nodes=[], links=[])

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    visited = {str(account.id)}
    nodes = {
        str(account.id): GraphNode(
            id=str(account.id),
            label=account.masked_account_ref,
            type="account",
        )
    }
    edges = []
    current_level = {str(account.id)}

    for _ in range(hops):
        next_level = set()
        account_ids = list(current_level)
        txns = (
            db.query(Transaction)
            .filter(
                (Transaction.sender_account_id.in_(account_ids))
                | (Transaction.receiver_account_id.in_(account_ids))
            )
            .limit(500)
            .all()
        )

        for txn in txns:
            sid = str(txn.sender_account_id)
            rid = str(txn.receiver_account_id)

            if sid not in visited:
                s = db.query(Account).filter(Account.id == sid).first()
                nodes[sid] = GraphNode(
                    id=sid,
                    label=s.masked_account_ref if s else sid,
                    type="account",
                )
                next_level.add(sid)
            if rid not in visited:
                r = db.query(Account).filter(Account.id == rid).first()
                nodes[rid] = GraphNode(
                    id=rid,
                    label=r.masked_account_ref if r else rid,
                    type="account",
                )
                next_level.add(rid)

            edges.append(
                GraphEdge(
                    source=sid,
                    target=rid,
                    label=f"{txn.amount} {txn.currency or ''}",
                    metadata={
                        "transaction_id": str(txn.id),
                        "amount": txn.amount,
                        "currency": txn.currency,
                    },
                )
            )

        visited.update(next_level)
        current_level = next_level
        if not current_level:
            break

    return GraphExploreResponse(nodes=list(nodes.values()), links=edges)


@router.post("/trace-source", response_model=TraceResponse)
def trace_source(
    request: TraceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    nodes = {}
    edges = []
    visited = {request.account_id}
    current = {request.account_id}

    for _ in range(request.max_hops):
        next_level = set()
        txns = (
            db.query(Transaction)
            .filter(Transaction.receiver_account_id.in_(list(current)))
            .limit(500)
            .all()
        )
        for txn in txns:
            sid = str(txn.sender_account_id)
            rid = str(txn.receiver_account_id)
            if sid not in visited:
                s = db.query(Account).filter(Account.id == sid).first()
                nodes[sid] = GraphNode(
                    id=sid,
                    label=s.masked_account_ref if s else sid,
                    type="account",
                    metadata={"country": s.country} if s else {},
                )
                next_level.add(sid)
            if rid not in visited:
                r = db.query(Account).filter(Account.id == rid).first()
                nodes[rid] = GraphNode(
                    id=rid,
                    label=r.masked_account_ref if r else rid,
                    type="account",
                    metadata={"country": r.country} if r else {},
                )
                next_level.add(rid)
            edges.append(GraphEdge(source=sid, target=rid, label=f"{txn.amount}"))
        visited.update(next_level)
        current = next_level
        if not current:
            break

    if str(request.account_id) not in nodes:
        nodes[str(request.account_id)] = GraphNode(
            id=str(request.account_id),
            label=account.masked_account_ref,
            type="account",
        )

    return TraceResponse(path_nodes=list(nodes.values()), path_edges=edges)


@router.post("/trace-destination", response_model=TraceResponse)
def trace_destination(
    request: TraceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    nodes = {}
    edges = []
    visited = {request.account_id}
    current = {request.account_id}

    for _ in range(request.max_hops):
        next_level = set()
        txns = (
            db.query(Transaction)
            .filter(Transaction.sender_account_id.in_(list(current)))
            .limit(500)
            .all()
        )
        for txn in txns:
            sid = str(txn.sender_account_id)
            rid = str(txn.receiver_account_id)
            if sid not in visited:
                s = db.query(Account).filter(Account.id == sid).first()
                nodes[sid] = GraphNode(
                    id=sid,
                    label=s.masked_account_ref if s else sid,
                    type="account",
                    metadata={"country": s.country} if s else {},
                )
                next_level.add(sid)
            if rid not in visited:
                r = db.query(Account).filter(Account.id == rid).first()
                nodes[rid] = GraphNode(
                    id=rid,
                    label=r.masked_account_ref if r else rid,
                    type="account",
                    metadata={"country": r.country} if r else {},
                )
                next_level.add(rid)
            edges.append(GraphEdge(source=sid, target=rid, label=f"{txn.amount}"))
        visited.update(next_level)
        current = next_level
        if not current:
            break

    if str(request.account_id) not in nodes:
        nodes[str(request.account_id)] = GraphNode(
            id=str(request.account_id),
            label=account.masked_account_ref,
            type="account",
        )

    return TraceResponse(path_nodes=list(nodes.values()), path_edges=edges)
