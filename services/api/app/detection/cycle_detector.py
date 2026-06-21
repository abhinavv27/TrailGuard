"""Circular flow detection."""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class CycleDetector(BaseDetector):
    """
    Detects circular transaction patterns where funds cycle through
    a set of accounts (e.g., A->B->C->A).
    """

    version = "1.1.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_cycle_window_hours = self.config.get(
            "max_cycle_window_hours", 48
        )

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions or len(transactions) < 3:
            return None

        cycles = self._find_cycles_involving(account_id, transactions)
        if not cycles:
            return None

        max_cycle_length = max(len(c) for c in cycles)
        amount_similarity = self._compute_amount_similarity(cycles, transactions)
        time_compression = self._compute_time_compression(cycles)

        score = min(
            0.35 * min(max_cycle_length / 5, 1.0)
            + 0.35 * amount_similarity
            + 0.30 * time_compression,
            1.0,
        )

        reason_codes = []
        source_tx_ids = []

        for cycle in cycles[:2]:
            cycle_accounts = list(dict.fromkeys(cycle))
            time_span = self._cycle_time_span(cycle, transactions)
            tx_ids_for_cycle = self._get_tx_ids_for_cycle(
                cycle, transactions
            )
            source_tx_ids.extend(tx_ids_for_cycle)

            reason_codes.append(
                {
                    "code": "CIRCULAR_FLOW",
                    "description": f"Circular transfer pattern detected: {cycle_accounts} within {time_span}.",
                    "severity": round(min(len(cycle) / 5, 1.0), 2),
                    "source_transaction_ids": tx_ids_for_cycle,
                }
            )

        return {
            "score": round(score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": list(set(source_tx_ids)),
            "version": self.version,
        }

    def analyze_dataset(self, all_transactions: List[Dict]) -> Dict[str, Dict]:
        """Find circular flows across the WHOLE graph in one pass and attribute
        each cycle to its member accounts. A cycle (A->B->C->A) spans multiple
        accounts, so per-account transaction slices can never see it.
        RiskEngine calls this once and looks up each account's result.
        """
        import networkx as nx

        edges_by_pair = defaultdict(list)
        G = nx.DiGraph()
        for tx in all_transactions:
            s = tx.get("sender_account_id", "")
            r = tx.get("receiver_account_id", "")
            ts = self._parse_ts(tx.get("timestamp", ""))
            if s and r and ts and s != r:
                edges_by_pair[(s, r)].append(
                    {"ts": ts, "amount": tx.get("amount", 0) or 0, "tx_id": tx.get("id", "")}
                )
                G.add_edge(s, r)

        try:
            raw_cycles = list(nx.simple_cycles(G, length_bound=6))
        except Exception as e:
            logger.error(f"simple_cycles failed: {e}")
            raw_cycles = []

        account_tx_counts: Dict[str, int] = defaultdict(int)
        for tx in all_transactions:
            s = tx.get("sender_account_id", "")
            r = tx.get("receiver_account_id", "")
            if s:
                account_tx_counts[s] += 1
            if r and r != s:
                account_tx_counts[r] += 1

        per_account: Dict[str, List[List[Dict]]] = defaultdict(list)
        for cyc in raw_cycles:
            if len(cyc) < 3:  # need A->B->C->A; 2-node back-and-forth is not layering
                continue
            pairs = [(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))]
            chosen = []
            ok = True
            for p in pairs:
                cands = edges_by_pair.get(p, [])
                if not cands:
                    ok = False
                    break
                chosen.append(min(cands, key=lambda e: e["ts"]))
            if not ok:
                continue
            tss = [e["ts"] for e in chosen]
            if (max(tss) - min(tss)).total_seconds() > self.max_cycle_window_hours * 3600:
                continue
            for acct in cyc:
                per_account[acct].append(chosen)

        results: Dict[str, Dict] = {}
        for acct, cyclist in per_account.items():
            scored = self._score_cycle_edges(acct, cyclist, account_tx_counts)
            if scored:
                results[acct] = scored
        return results

    def _score_cycle_edges(
        self,
        account_id: str,
        cyclist: List[List[Dict]],
        account_tx_counts: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict]:
        if not cyclist:
            return None
        best = max(cyclist, key=len)
        max_cycle_length = len(best)
        amounts = [e["amount"] for e in best if e["amount"] > 0]
        amount_similarity = (min(amounts) / max(amounts)) if len(amounts) >= 2 else 0.0
        tss = [e["ts"] for e in best]
        span_h = (max(tss) - min(tss)).total_seconds() / 3600 if len(tss) >= 2 else 0
        time_compression = max(0.0, 1 - span_h / self.max_cycle_window_hours)

        score = min(
            0.35 * min(max_cycle_length / 5, 1.0)
            + 0.35 * amount_similarity
            + 0.30 * time_compression,
            1.0,
        )

        # Dedication: a dedicated cycle conduit's only activity is the loop;
        # a busy normal account caught in an incidental cycle is suppressed.
        if account_tx_counts:
            cyc_tx_ids = set()
            for cyc in cyclist:
                for e in cyc:
                    if e.get("tx_id"):
                        cyc_tx_ids.add(e["tx_id"])
            total = account_tx_counts.get(account_id, 0)
            dedication = len(cyc_tx_ids) / total if total else 0.0
            score *= min(dedication, 1.0)

        tx_ids = [e["tx_id"] for e in best if e.get("tx_id")]
        reason_codes = [
            {
                "code": "CIRCULAR_FLOW",
                "description": f"Account is part of a {max_cycle_length}-account circular transfer completing in {int(span_h)}h.",
                "severity": round(min(max_cycle_length / 5, 1.0), 2),
                "source_transaction_ids": tx_ids,
            }
        ]
        return {
            "score": round(score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": tx_ids,
            "version": self.version,
        }

    def _find_cycles_involving(
        self, account_id: str, transactions: List[Dict]
    ) -> List[List[str]]:
        """Find cycles that include the given account_id."""
        adjacency = defaultdict(list)
        tx_map = {}

        for tx in transactions:
            sender = tx.get("sender_account_id", "")
            receiver = tx.get("receiver_account_id", "")
            ts = self._parse_ts(tx.get("timestamp", ""))
            if sender and receiver and ts:
                adjacency[sender].append(
                    {
                        "receiver": receiver,
                        "timestamp": ts,
                        "tx_id": tx.get("id", ""),
                    }
                )
                tx_map[tx.get("id", "")] = tx

        cycles = []

        def dfs(current: str, start: str, path: List[str], visited: set, depth: int):
            if depth > 6:
                return
            if current == start and depth >= 3:
                cycles.append(list(path))
                return

            visited.add(current)
            for edge in adjacency.get(current, []):
                next_node = edge["receiver"]
                if next_node in visited and next_node != start:
                    continue
                path.append(next_node)
                dfs(next_node, start, path, visited, depth + 1)
                path.pop()
            visited.discard(current)

        first_edges = adjacency.get(account_id, [])
        for edge in first_edges:
            path = [account_id, edge["receiver"]]
            visited = {account_id}
            dfs(edge["receiver"], account_id, path, visited, 2)
            path.pop()

        return cycles

    def _compute_amount_similarity(
        self, cycles: List[List[str]], transactions: List[Dict]
    ) -> float:
        """Score based on how similar amounts are in the cycle."""
        if not cycles:
            return 0

        amounts = []
        for tx in transactions:
            amounts.append(tx.get("amount", 0))

        if not amounts:
            return 0

        mean_amt = sum(amounts) / len(amounts)
        if mean_amt == 0:
            return 0

        deviations = [abs(a - mean_amt) / mean_amt for a in amounts]
        avg_deviation = sum(deviations) / len(deviations)
        return max(0, 1 - avg_deviation)

    def _compute_time_compression(self, cycles: List[List[str]]) -> float:
        """Score based on how quickly the cycle completes."""
        if not cycles:
            return 0
        # Placeholder logic - return mid-range score
        return 0.5

    def _cycle_time_span(
        self, cycle: List[str], transactions: List[Dict]
    ) -> str:
        timestamps = []
        for tx in transactions:
            sender = tx.get("sender_account_id", "")
            receiver = tx.get("receiver_account_id", "")
            for i in range(len(cycle) - 1):
                if sender == cycle[i] and receiver == cycle[i + 1]:
                    ts = self._parse_ts(tx.get("timestamp", ""))
                    if ts:
                        timestamps.append(ts)

        if len(timestamps) >= 2:
            delta = max(timestamps) - min(timestamps)
            hours = delta.total_seconds() / 3600
            if hours < 1:
                return f"{int(delta.total_seconds() // 60)}m"
            return f"{int(hours)}h"
        return "N/A"

    def _get_tx_ids_for_cycle(
        self, cycle: List[str], transactions: List[Dict]
    ) -> List[str]:
        tx_ids = []
        for i in range(len(cycle) - 1):
            for tx in transactions:
                if (
                    tx.get("sender_account_id", "") == cycle[i]
                    and tx.get("receiver_account_id", "") == cycle[i + 1]
                ):
                    tx_ids.append(tx.get("id", ""))
                    break
        return tx_ids

    def _parse_ts(self, ts_str: str) -> Optional[datetime]:
        if not ts_str:
            return None
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                return None
