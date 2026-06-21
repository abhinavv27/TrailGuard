"""Regression tests for the graph API endpoints.

The seed path stores external_account_ref in the transaction FK columns while
alerts/UI reference accounts by their UUID. The graph endpoints must resolve an
account's transactions by either id, or a per-account/per-alert graph comes back
as a single isolated node (no money trail).
"""
from datetime import datetime, timedelta

from app.api.v1.graph import explore_graph, trace_source
from app.models.account import Account
from app.models.dataset import Dataset
from app.models.transaction import Transaction
from app.schemas.graph import GraphExploreRequest, TraceRequest


def _seed_ref_keyed_graph(db, user_id):
    """Build accounts (UUID ids) whose transactions are keyed by
    external_account_ref, mirroring the seed convention."""
    ds = Dataset(
        user_id=user_id, filename="seedconv.csv", original_filename="seedconv.csv",
        file_size=1, file_hash="h-seedconv", row_count=0, status="analyzed",
    )
    db.add(ds)
    db.flush()

    refs = ["HUB", "SRC-1", "SRC-2", "SRC-3", "DEST-1"]
    accts = {}
    for ref in refs:
        a = Account(dataset_id=ds.id, external_account_ref=ref,
                    masked_account_ref=ref, country="US", account_age_days=30)
        db.add(a)
        db.flush()
        accts[ref] = a

    base = datetime(2024, 1, 1, 9, 0, 0)
    # Seed convention: FK columns hold the external ref, NOT the UUID.
    edges = [("SRC-1", "HUB"), ("SRC-2", "HUB"), ("SRC-3", "HUB"), ("HUB", "DEST-1")]
    for i, (s, r) in enumerate(edges):
        db.add(Transaction(
            dataset_id=ds.id, external_transaction_ref=f"tx{i}",
            timestamp=base + timedelta(hours=i),
            sender_account_id=s, receiver_account_id=r,
            amount=1000.0 + i, currency="USD", channel="online",
        ))
    db.commit()
    return accts


def test_explore_resolves_account_by_uuid_against_ref_keyed_txns(db_session, demo_user):
    accts = _seed_ref_keyed_graph(db_session, demo_user.id)
    hub = accts["HUB"]

    # The UI passes the account UUID (as it appears on an alert).
    resp = explore_graph(
        GraphExploreRequest(account_id=str(hub.id), hops=2),
        current_user={},
        db=db_session,
    )

    # Before the fix this returned a single isolated node (UUID not in the
    # ref-keyed transactions). Now the hub's 4-transaction neighborhood renders.
    assert len(resp.nodes) >= 4, [n.id for n in resp.nodes]
    assert len(resp.links) >= 4
    hub_node = next((n for n in resp.nodes if n.id == "HUB"), None)
    assert hub_node is not None, "hub account missing from its own graph"


def test_trace_source_follows_upstream_for_ref_keyed_txns(db_session, demo_user):
    accts = _seed_ref_keyed_graph(db_session, demo_user.id)
    hub = accts["HUB"]

    resp = trace_source(
        TraceRequest(account_id=str(hub.id), max_hops=2),
        current_user={},
        db=db_session,
    )

    # The three sources feeding the hub should be traced upstream.
    assert len(resp.path_nodes) >= 4, [n.id for n in resp.path_nodes]
    assert len(resp.path_edges) >= 3
