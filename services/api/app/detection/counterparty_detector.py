"""Sudden counterparty expansion detector."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class CounterpartyDetector(BaseDetector):
    """
    Detects sudden expansion in the number of unique counterparties
    an account transacts with within a short time window.
    """

    version = "1.0.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.expansion_window_days = self.config.get(
            "expansion_window_days", 7
        )
        self.baseline_days = self.config.get("baseline_days", 60)
        self.min_new_counterparties = self.config.get(
            "min_new_counterparties", 5
        )
        # Anchor windows to the dataset clock; set by RiskEngine.prepare_dataset().
        self.reference_time = None

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions or len(transactions) < self.min_new_counterparties:
            return None

        now = self.reference_time or datetime.utcnow()
        expansion_start = now - timedelta(days=self.expansion_window_days)
        baseline_start = now - timedelta(days=self.baseline_days)

        recent_counterparties = set()
        baseline_counterparties = set()
        recent_tx_ids = []

        for tx in transactions:
            ts = self._parse_ts(tx.get("timestamp", ""))
            if not ts:
                continue

            counterparty = tx.get("sender_account_id", "")
            if tx.get("receiver_account_id") == account_id:
                counterparty = tx.get("sender_account_id", "")
            elif tx.get("sender_account_id") == account_id:
                counterparty = tx.get("receiver_account_id", "")

            if not counterparty or counterparty == account_id:
                continue

            if ts >= expansion_start:
                recent_counterparties.add(counterparty)
                recent_tx_ids.append(tx.get("id", ""))
            elif ts >= baseline_start:
                baseline_counterparties.add(counterparty)

        new_counterparties = recent_counterparties - baseline_counterparties
        new_count = len(new_counterparties)

        if new_count < self.min_new_counterparties:
            return None

        all_counterparties = baseline_counterparties | recent_counterparties
        if not all_counterparties:
            return None

        expansion_ratio = new_count / max(len(all_counterparties), 1)
        baseline_daily_rate = len(baseline_counterparties) / max(
            self.baseline_days, 1
        )
        recent_daily_rate = new_count / max(self.expansion_window_days, 1)

        rate_multiplier = 0
        if baseline_daily_rate > 0:
            rate_multiplier = min(recent_daily_rate / baseline_daily_rate, 5) / 5

        score = min(
            0.4 * expansion_ratio
            + 0.3 * min(new_count / 20, 1.0)
            + 0.3 * rate_multiplier,
            1.0,
        )

        reason_codes = [
            {
                "code": "COUNTERPARTY_EXPANSION",
                "description": f"Sudden counterparty expansion: {new_count} new unique counterparties in {self.expansion_window_days}d.",
                "severity": round(score, 2),
                "source_transaction_ids": recent_tx_ids[:10],
            }
        ]

        return {
            "score": round(score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": recent_tx_ids[:20],
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
