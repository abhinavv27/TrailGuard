"""Mule/funnel account detection."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class MuleDetector(BaseDetector):
    """
    Detects mule/funnel account patterns:
    - High incoming sender diversity
    - Rapid forwarding of received funds
    - High outgoing recipient diversity
    - Short holding times
    - New accounts with high-value movement
    """

    version = "2.1.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.rapid_forward_window = self.config.get(
            "rapid_forward_window_hours", 24
        )
        self.short_holding_hours = self.config.get("short_holding_hours", 2)

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions:
            return None

        now = datetime.utcnow()
        incoming = [tx for tx in transactions if tx.get("receiver_account_id") == account_id]
        outgoing = [tx for tx in transactions if tx.get("sender_account_id") == account_id]

        if not incoming:
            return {
                "score": 0,
                "reason_codes": [],
                "source_transaction_ids": [],
                "version": self.version,
            }

        unique_senders = set(tx.get("sender_account_id") for tx in incoming)
        incoming_diversity = min(len(unique_senders) / 20, 1.0)

        incoming_total = sum(tx.get("amount", 0) for tx in incoming)
        outgoing_total = sum(tx.get("amount", 0) for tx in outgoing)

        rapid_forward_score = 0
        if incoming_total > 0:
            recent_outgoing = [
                tx
                for tx in outgoing
                if tx.get("timestamp")
                and (
                    now - self._parse_ts(tx["timestamp"])
                ).total_seconds()
                < self.rapid_forward_window * 3600
            ]
            outgoing_recent_total = sum(tx.get("amount", 0) for tx in recent_outgoing)
            forwarding_ratio = outgoing_recent_total / incoming_total
            rapid_forward_score = min(forwarding_ratio, 1.0)

        unique_recipients = set(tx.get("receiver_account_id") for tx in outgoing)
        outgoing_diversity = min(len(unique_recipients) / 15, 1.0)

        short_holding_score = 0
        if incoming and outgoing:
            holding_times = []
            for in_tx in incoming:
                in_ts = self._parse_ts(in_tx.get("timestamp", ""))
                if not in_ts:
                    continue
                for out_tx in outgoing:
                    out_ts = self._parse_ts(out_tx.get("timestamp", ""))
                    if not out_ts:
                        continue
                    if out_ts > in_ts:
                        delta = (out_ts - in_ts).total_seconds() / 3600
                        if delta < self.short_holding_hours:
                            holding_times.append(delta)
            if holding_times:
                avg_holding = sum(holding_times) / len(holding_times)
                short_holding_score = max(
                    0, 1 - avg_holding / self.short_holding_hours
                )

        account_age_days = None
        for tx in transactions:
            ts = self._parse_ts(tx.get("timestamp", ""))
            if ts:
                age = (now - ts).days
                if age is not None and (account_age_days is None or age < account_age_days):
                    account_age_days = age
        if account_age_days is None:
            account_age_days = 365

        new_account_score = 0
        if account_age_days < 30 and incoming_total > 10000:
            new_account_score = min(1.0, (30 - account_age_days) / 30)

        graph_centrality_score = 0  # Placeholder for NetworkX integration

        mule_score = (
            0.25 * incoming_diversity
            + 0.25 * rapid_forward_score
            + 0.15 * outgoing_diversity
            + 0.15 * short_holding_score
            + 0.10 * new_account_score
            + 0.10 * graph_centrality_score
        )

        reason_codes = []
        source_tx_ids = []

        if incoming_diversity > 0.3:
            tx_ids = [tx.get("id", "") for tx in incoming[:5]]
            source_tx_ids.extend(tx_ids)
            reason_codes.append(
                {
                    "code": "INCOMING_DIVERSITY",
                    "description": f"Received funds from {len(unique_senders)} unrelated accounts.",
                    "severity": round(incoming_diversity, 2),
                    "source_transaction_ids": tx_ids,
                }
            )

        if rapid_forward_score > 0.3:
            tx_ids = [tx.get("id", "") for tx in recent_outgoing[:5]]
            source_tx_ids.extend(tx_ids)
            reason_codes.append(
                {
                    "code": "RAPID_FORWARDING",
                    "description": f"Forwarded {round(forwarding_ratio * 100)}% of received funds within {self.rapid_forward_window}h.",
                    "severity": round(rapid_forward_score, 2),
                    "source_transaction_ids": tx_ids,
                }
            )

        if outgoing_diversity > 0.3:
            tx_ids = [tx.get("id", "") for tx in outgoing[:5]]
            source_tx_ids.extend(tx_ids)
            reason_codes.append(
                {
                    "code": "OUTGOING_DIVERSITY",
                    "description": f"Sent value to {len(unique_recipients)} downstream accounts.",
                    "severity": round(outgoing_diversity, 2),
                    "source_transaction_ids": tx_ids,
                }
            )

        if new_account_score > 0:
            tx_ids = [tx.get("id", "") for tx in incoming[:3]]
            source_tx_ids.extend(tx_ids)
            reason_codes.append(
                {
                    "code": "NEW_ACCOUNT_MULE",
                    "description": f"Account is {account_age_days} days old with high-value movement.",
                    "severity": round(new_account_score, 2),
                    "source_transaction_ids": tx_ids,
                }
            )

        return {
            "score": round(mule_score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": list(set(source_tx_ids)),
            "version": self.version,
        }

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
