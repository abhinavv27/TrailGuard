"""Tests for the graph builder."""
from app.graph.builder import GraphBuilder


def test_build_graph():
    builder = GraphBuilder()
    transactions = [
        {"sender_account_id": "A", "receiver_account_id": "B", "amount": 100, "timestamp": "2026-05-15T10:00:00", "id": "tx1", "currency": "USD", "channel": "wire"},
        {"sender_account_id": "B", "receiver_account_id": "C", "amount": 200, "timestamp": "2026-05-15T11:00:00", "id": "tx2", "currency": "USD", "channel": "wire"},
    ]
    G = builder.build_graph(transactions)
    assert len(G.nodes()) == 3
    assert len(G.edges()) == 2

def test_trace_source():
    builder = GraphBuilder()
    transactions = [
        {"sender_account_id": "A", "receiver_account_id": "B", "amount": 100, "timestamp": "2026-05-15T10:00:00", "id": "tx1", "currency": "USD", "channel": "wire"},
        {"sender_account_id": "B", "receiver_account_id": "C", "amount": 200, "timestamp": "2026-05-15T11:00:00", "id": "tx2", "currency": "USD", "channel": "wire"},
    ]
    G = builder.build_graph(transactions)
    result = builder.trace_source(G, "C", max_hops=2)
    assert len(result["nodes"]) == 3  # C, B, A
    assert len(result["edges"]) == 2

def test_trace_destination():
    builder = GraphBuilder()
    transactions = [
        {"sender_account_id": "A", "receiver_account_id": "B", "amount": 100, "timestamp": "2026-05-15T10:00:00", "id": "tx1", "currency": "USD", "channel": "wire"},
        {"sender_account_id": "B", "receiver_account_id": "C", "amount": 200, "timestamp": "2026-05-15T11:00:00", "id": "tx2", "currency": "USD", "channel": "wire"},
    ]
    G = builder.build_graph(transactions)
    result = builder.trace_destination(G, "A", max_hops=2)
    assert len(result["nodes"]) == 3  # A, B, C
    assert len(result["edges"]) == 2

def test_get_account_metrics():
    builder = GraphBuilder()
    transactions = [
        {"sender_account_id": "A", "receiver_account_id": "B", "amount": 100, "timestamp": "2026-05-15T10:00:00", "id": "tx1", "currency": "USD", "channel": "wire"},
        {"sender_account_id": "A", "receiver_account_id": "C", "amount": 200, "timestamp": "2026-05-15T11:00:00", "id": "tx2", "currency": "USD", "channel": "wire"},
        {"sender_account_id": "B", "receiver_account_id": "A", "amount": 50, "timestamp": "2026-05-15T12:00:00", "id": "tx3", "currency": "USD", "channel": "wire"},
    ]
    G = builder.build_graph(transactions)
    metrics = builder.get_account_metrics(G, "A")
    assert metrics["out_degree"] == 2
    assert metrics["in_degree"] == 1
