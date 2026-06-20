"""Graph service - wraps GraphBuilder for API use."""
import logging
from typing import Any, Dict, List, Optional

import networkx as nx

from app.graph.builder import GraphBuilder

logger = logging.getLogger(__name__)


class GraphService:
    """High-level graph analysis service for API consumption."""

    def __init__(self):
        self.builder = GraphBuilder()

    def analyze_transactions(
        self, transactions: List[Dict]
    ) -> Dict[str, Any]:
        """Full graph analysis of a transaction set."""
        G = self.builder.build_graph(transactions)
        centrality = self.builder.compute_centrality(G)
        cycles = self.builder.find_cycles(G)

        account_metrics = {}
        all_accounts = set()
        for tx in transactions:
            all_accounts.add(tx.get("sender_account_id", ""))
            all_accounts.add(tx.get("receiver_account_id", ""))

        for acc in all_accounts:
            if acc:
                account_metrics[acc] = self.builder.get_account_metrics(
                    G, acc
                )

        return {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "density": nx.density(G),
            "is_connected": nx.is_weakly_connected(G)
            if G.number_of_nodes() > 0
            else False,
            "centrality": centrality,
            "cycles": [
                {"length": len(c), "accounts": c} for c in cycles
            ],
            "account_metrics": account_metrics,
        }

    def trace_transaction_flow(
        self,
        transactions: List[Dict],
        account_id: str,
        max_hops: int = 3,
        direction: str = "both",
    ) -> Dict[str, Any]:
        """Trace funds to/from an account."""
        G = self.builder.build_graph(transactions)
        result = {"account_id": account_id, "max_hops": max_hops}

        if direction in ("source", "both"):
            result["source_trace"] = self.builder.trace_source(
                G, account_id, max_hops
            )

        if direction in ("destination", "both"):
            result["destination_trace"] = self.builder.trace_destination(
                G, account_id, max_hops
            )

        result["account_metrics"] = self.builder.get_account_metrics(
            G, account_id
        )

        return result

    def get_centrality_ranking(
        self, transactions: List[Dict], top_n: int = 10
    ) -> Dict[str, Any]:
        """Get top-N accounts by betweenness centrality."""
        G = self.builder.build_graph(transactions)
        centrality = self.builder.compute_centrality(G)
        betweenness = centrality.get("betweenness", {})

        ranked = sorted(
            betweenness.items(), key=lambda x: x[1], reverse=True
        )[:top_n]

        return {
            "ranking": [
                {"account_id": acc, "betweenness": round(score, 6)}
                for acc, score in ranked
            ],
            "top_n": top_n,
        }

    def detect_communities(
        self, transactions: List[Dict]
    ) -> List[List[str]]:
        """Detect communities in the transaction graph."""
        G = self.builder.build_graph(transactions)
        UG = G.to_undirected()

        try:
            from networkx.algorithms.community import greedy_modularity_communities

            communities = list(greedy_modularity_communities(UG))
            return [sorted(list(c)) for c in communities]
        except ImportError:
            logger.warning(
                "Community detection not available; need networkx>=2.5"
            )
            return []
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return []
