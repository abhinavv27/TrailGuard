"""Build NetworkX graphs from transaction data and compute metrics."""
from typing import Dict, List

import networkx as nx


class GraphBuilder:
    """Builds and analyzes transaction graphs."""

    def __init__(self):
        self._cycles_cache = None

    def build_graph(self, transactions: List[Dict]) -> nx.DiGraph:
        """Build a directed graph from transaction list."""
        G = nx.DiGraph()
        for tx in transactions:
            sender = tx.get("sender_account_id", "")
            receiver = tx.get("receiver_account_id", "")
            G.add_edge(
                sender,
                receiver,
                amount=tx.get("amount", 0),
                timestamp=str(tx.get("timestamp", "")),
                transaction_id=tx.get("id", ""),
                currency=tx.get("currency", "USD"),
                channel=tx.get("channel", ""),
            )
        return G

    def compute_centrality(self, G: nx.DiGraph) -> Dict[str, float]:
        """Compute various centrality measures."""
        try:
            betweenness = nx.betweenness_centrality(G, weight="amount")
            in_degree = dict(G.in_degree())
            out_degree = dict(G.out_degree())
            max_degree = max(len(G), 1)
            return {
                "betweenness": betweenness,
                "in_degree": {
                    k: v / max_degree for k, v in in_degree.items()
                },
                "out_degree": {
                    k: v / max_degree for k, v in out_degree.items()
                },
            }
        except Exception:
            return {
                "betweenness": {},
                "in_degree": {},
                "out_degree": {},
            }

    def find_cycles(self, G: nx.DiGraph) -> List[List[str]]:
        """Find all simple cycles in the graph."""
        if self._cycles_cache is not None:
            return self._cycles_cache
        try:
            cycles = list(nx.simple_cycles(G, length_bound=5))
            self._cycles_cache = cycles
            return cycles
        except nx.NetworkXNoCycle:
            self._cycles_cache = []
            return []

    def trace_source(
        self, G: nx.DiGraph, account_id: str, max_hops: int = 3
    ) -> List[Dict]:
        """Trace funds backward to find source accounts."""
        nodes = []
        edges = []
        visited = set()

        def dfs(node, depth):
            if depth > max_hops or node in visited:
                return
            visited.add(node)
            nodes.append(
                {"id": node, "depth": depth, "direction": "source"}
            )
            for pred in G.predecessors(node):
                edge_data = G.get_edge_data(pred, node)
                edges.append(
                    {
                        "source": pred,
                        "target": node,
                        "amount": edge_data.get("amount", 0),
                        "timestamp": edge_data.get("timestamp", ""),
                    }
                )
                dfs(pred, depth + 1)

        dfs(account_id, 0)
        return {"nodes": nodes, "edges": edges}

    def trace_destination(
        self, G: nx.DiGraph, account_id: str, max_hops: int = 3
    ) -> List[Dict]:
        """Trace funds forward to find destination accounts."""
        nodes = []
        edges = []
        visited = set()

        def dfs(node, depth):
            if depth > max_hops or node in visited:
                return
            visited.add(node)
            nodes.append(
                {
                    "id": node,
                    "depth": depth,
                    "direction": "destination",
                }
            )
            for succ in G.successors(node):
                edge_data = G.get_edge_data(node, succ)
                edges.append(
                    {
                        "source": node,
                        "target": succ,
                        "amount": edge_data.get("amount", 0),
                        "timestamp": edge_data.get("timestamp", ""),
                    }
                )
                dfs(succ, depth + 1)

        dfs(account_id, 0)
        return {"nodes": nodes, "edges": edges}

    def get_account_metrics(
        self, G: nx.DiGraph, account_id: str
    ) -> Dict:
        """Get graph metrics for a specific account."""
        if account_id not in G:
            return {
                "in_total": 0,
                "out_total": 0,
                "in_degree": 0,
                "out_degree": 0,
                "in_unique_counterparties": 0,
                "out_unique_counterparties": 0,
                "in_cycle": False,
                "cycle_count": 0,
            }
        in_edges = list(G.in_edges(account_id, data=True))
        out_edges = list(G.out_edges(account_id, data=True))
        in_total = sum(e[2].get("amount", 0) for e in in_edges)
        out_total = sum(e[2].get("amount", 0) for e in out_edges)

        in_degree = G.in_degree(account_id)
        out_degree = G.out_degree(account_id)

        cycles = self.find_cycles(G)
        in_cycle = any(account_id in cycle for cycle in cycles)

        return {
            "in_total": in_total,
            "out_total": out_total,
            "in_degree": in_degree,
            "out_degree": out_degree,
            "in_unique_counterparties": len(
                [e[0] for e in in_edges]
            ),
            "out_unique_counterparties": len(
                [e[1] for e in out_edges]
            ),
            "in_cycle": in_cycle,
            "cycle_count": len(cycles),
        }
