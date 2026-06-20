"""Multi-hop layering detection."""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class LayeringDetector(BaseDetector):
    """
    Detects multi-hop layering patterns where funds move through
    multiple accounts in quick succession (A->B->C).
    """

    version = "1.2.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_chain_gap_hours = self.config.get("max_chain_gap_hours", 24)
        self.min_chain_length = self.config.get("min_chain_length", 3)

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions or len(transactions) < self.min_chain_length:
            return None

        chains = self._find_layering_chains(account_id, transactions)
        if not chains:
            return None

        total_chains = sum(len(c) for c in chains.values())
        chain_length = max(len(c) for c in chains.values()) if chains else 0
        speed_factor = self._compute_speed_factor(chains)

        score = min(
            0.4 * min(chain_length / 5, 1.0)
            + 0.3 * speed_factor
            + 0.3 * min(total_chains / 10, 1.0),
            1.0,
        )

        reason_codes = []
        source_tx_ids = []

        if score > 0:
            for chain_key, chain in chains.items():
                if len(chain) >= self.min_chain_length:
                    accounts_involved = [tx.get("receiver_account_id", "") for tx in chain]
                    time_span = self._chain_time_span(chain)
                    tx_ids = [tx.get("id", "") for tx in chain]
                    source_tx_ids.extend(tx_ids)

                    reason_codes.append(
                        {
                            "code": "MULTI_HOP_LAYERING",
                            "description": f"Funds moved through {len(chain)} accounts in {time_span} via multi-hop chain.",
                            "severity": round(min(len(chain) / 6, 1.0), 2),
                            "source_transaction_ids": tx_ids,
                        }
                    )

        return {
            "score": round(score, 4),
            "reason_codes": reason_codes[:3],
            "source_transaction_ids": list(set(source_tx_ids))[:20],
            "version": self.version,
        }

    def _find_layering_chains(
        self, account_id: str, transactions: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Find chains where funds pass through multiple accounts."""
        adjacency = defaultdict(list)
        for tx in transactions:
            sender = tx.get("sender_account_id", "")
            receiver = tx.get("receiver_account_id", "")
            ts = self._parse_ts(tx.get("timestamp", ""))
            if sender and receiver and ts:
                adjacency[sender].append(tx)

        chains = {}
        visited = set()

        def dfs(current: str, chain: List[Dict], depth: int):
            if depth > 6:
                return
            if depth >= self.min_chain_length:
                chain_key = "->".join(
                    [str(chain[0].get("sender_account_id", ""))]
                    + [str(t.get("receiver_account_id", "")) for t in chain]
                )
                if chain_key not in chains:
                    chains[chain_key] = list(chain)

            if current in visited:
                return

            visited.add(current)
            for next_tx in adjacency.get(current, []):
                chain.append(next_tx)
                next_receiver = next_tx.get("receiver_account_id", "")
                if self._chain_within_window(chain):
                    dfs(next_receiver, chain, depth + 1)
                chain.pop()
            visited.discard(current)

        dfs(account_id, [], 0)
        return chains

    def _chain_within_window(self, chain: List[Dict]) -> bool:
        if len(chain) < 2:
            return True
        first_ts = self._parse_ts(chain[0].get("timestamp", ""))
        last_ts = self._parse_ts(chain[-1].get("timestamp", ""))
        if first_ts and last_ts:
            return (last_ts - first_ts).total_seconds() < self.max_chain_gap_hours * 3600
        return True

    def _chain_time_span(self, chain: List[Dict]) -> str:
        if len(chain) < 2:
            return "N/A"
        first_ts = self._parse_ts(chain[0].get("timestamp", ""))
        last_ts = self._parse_ts(chain[-1].get("timestamp", ""))
        if first_ts and last_ts:
            delta = last_ts - first_ts
            hours = delta.total_seconds() / 3600
            if hours < 1:
                return f"{int(delta.total_seconds() // 60)}m"
            return f"{int(hours)}h"
        return "N/A"

    def _compute_speed_factor(self, chains: Dict[str, List[Dict]]) -> float:
        if not chains:
            return 0
        gaps = []
        for chain in chains.values():
            for i in range(1, len(chain)):
                prev_ts = self._parse_ts(chain[i - 1].get("timestamp", ""))
                curr_ts = self._parse_ts(chain[i].get("timestamp", ""))
                if prev_ts and curr_ts:
                    gaps.append((curr_ts - prev_ts).total_seconds() / 3600)
        if not gaps:
            return 0
        avg_gap = sum(gaps) / len(gaps)
        return max(0, 1 - avg_gap / self.max_chain_gap_hours)

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
