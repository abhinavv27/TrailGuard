"""Multi-hop layering detection."""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

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
        # Max transaction footprint for an account to be treated as a layering
        # "conduit" (throwaway pass-through). Above this it is a normal,
        # high-volume account and excluded from chain search.
        self.conduit_max_tx = self.config.get("conduit_max_tx", 10)

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
        return self._score_chains(chains)

    def analyze_dataset(self, all_transactions: List[Dict]) -> Dict[str, Dict]:
        """Find layering chains across the WHOLE transaction graph in a single
        pass, then attribute each chain to the accounts that participate in it.

        Layering is inherently cross-account (A->B->C->D); a single account's
        transaction slice does not contain the downstream hops, so per-account
        analysis can never see the chain. RiskEngine calls this once and looks
        up each account's result.
        """
        # Total transaction footprint per account.
        account_tx_counts: Dict[str, int] = defaultdict(int)
        for tx in all_transactions:
            s = tx.get("sender_account_id", "")
            r = tx.get("receiver_account_id", "")
            if s:
                account_tx_counts[s] += 1
            if r and r != s:
                account_tx_counts[r] += 1

        # Restrict the chain search to low-footprint "conduit" accounts. Real
        # layering is built from throwaway pass-through accounts; high-volume
        # accounts are legitimate businesses. This both finds the real chain
        # (which would otherwise be drowned out) and stops the DFS exploding on
        # the dense normal-account subgraph.
        def is_conduit(acct):
            return 0 < account_tx_counts.get(acct, 0) <= self.conduit_max_tx

        adjacency = defaultdict(list)
        for tx in all_transactions:
            sender = tx.get("sender_account_id", "")
            receiver = tx.get("receiver_account_id", "")
            ts = self._parse_ts(tx.get("timestamp", ""))
            if sender and receiver and ts and is_conduit(sender) and is_conduit(receiver):
                adjacency[sender].append(tx)

        global_chains: Dict[str, List[Dict]] = {}
        MAX_CHAINS = 20000

        def dfs(current: str, chain: List[Dict], depth: int, visited: set):
            if len(global_chains) >= MAX_CHAINS or depth > 6:
                return
            if depth >= self.min_chain_length:
                chain_key = "->".join(
                    [str(chain[0].get("sender_account_id", ""))]
                    + [str(t.get("receiver_account_id", "")) for t in chain]
                )
                global_chains.setdefault(chain_key, list(chain))
            if current in visited:
                return
            visited.add(current)
            for next_tx in adjacency.get(current, []):
                chain.append(next_tx)
                if self._chain_within_window(chain):
                    dfs(next_tx.get("receiver_account_id", ""), chain, depth + 1, visited)
                chain.pop()
            visited.discard(current)

        for start in list(adjacency.keys()):
            if len(global_chains) >= MAX_CHAINS:
                break
            dfs(start, [], 0, set())

        # Attribute a chain to each pass-through intermediary (received then
        # forwarded onward). Discrimination comes from "dedication" at scoring
        # time, not an amount filter: this synthetic data does not preserve
        # amounts across hops, and a hard amount gate both missed real chains
        # and flagged coincidental ones.
        per_account: Dict[str, Dict[str, List[Dict]]] = defaultdict(dict)
        for key, chain in global_chains.items():
            for k in range(len(chain) - 1):
                intermediary = chain[k + 1].get("sender_account_id", "")
                if intermediary:
                    per_account[intermediary][key] = chain

        results: Dict[str, Dict] = {}
        for acct, chains in per_account.items():
            scored = self._score_chains(chains, acct, account_tx_counts)
            if scored:
                results[acct] = scored
        return results

    def _score_chains(
        self,
        chains: Dict[str, List[Dict]],
        account_id: str = "",
        account_tx_counts: Optional[Dict[str, int]] = None,
    ) -> Optional[Dict]:
        if not chains:
            return None

        chain_length = max(len(c) for c in chains.values()) if chains else 0
        speed_factor = self._compute_speed_factor(chains)
        amount_similarity = max(
            (self._chain_amount_similarity(c) for c in chains.values()), default=0.0
        )

        score = min(
            0.4 * min(chain_length / 5, 1.0)
            + 0.3 * speed_factor
            + 0.3 * amount_similarity,
            1.0,
        )

        # Dedication = fraction of the account's whole activity that is this
        # chain. A dedicated throwaway conduit (its only txs are the layering
        # hops) scores ~1.0; a busy normal account that sits on an incidental
        # path scores near 0 and is suppressed. This is what separates planted
        # layering from coincidental paths in a dense graph.
        if account_id and account_tx_counts:
            chain_tx_ids = set()
            for chain in chains.values():
                for tx in chain:
                    if (
                        tx.get("sender_account_id") == account_id
                        or tx.get("receiver_account_id") == account_id
                    ):
                        chain_tx_ids.add(tx.get("id", ""))
            total = account_tx_counts.get(account_id, 0)
            dedication = len(chain_tx_ids) / total if total else 0.0
            score *= min(dedication, 1.0)

        reason_codes = []
        source_tx_ids = []

        if score > 0:
            for chain_key, chain in chains.items():
                if len(chain) >= self.min_chain_length:
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

    def _chain_amount_similarity(self, chain: List[Dict]) -> float:
        """Average amount preservation across consecutive hops (1.0 = the exact
        same amount forwarded at every hop, the laundering ideal)."""
        if len(chain) < 2:
            return 0.0
        ratios = []
        for i in range(1, len(chain)):
            a = chain[i - 1].get("amount", 0) or 0
            b = chain[i].get("amount", 0) or 0
            if a > 0 and b > 0:
                ratios.append(min(a, b) / max(a, b))
        return sum(ratios) / len(ratios) if ratios else 0.0

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
