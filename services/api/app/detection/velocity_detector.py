"""Transaction velocity detection."""
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class VelocityDetector(BaseDetector):
    """
    Detects unusual transaction velocity:
    - High transfer frequency in short time
    - Sudden spike in activity relative to baseline
    """

    version = "1.0.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.velocity_window_hours = self.config.get(
            "velocity_window_hours", 1
        )
        self.baseline_days = self.config.get("baseline_days", 30)
        self.max_tx_per_hour = self.config.get("max_tx_per_hour", 10)

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions or len(transactions) < 3:
            return None

        timestamps = [
            self._parse_ts(tx.get("timestamp", ""))
            for tx in transactions
            if self._parse_ts(tx.get("timestamp", ""))
        ]

        if len(timestamps) < 3:
            return None

        now = max(timestamps)
        window_start = now - timedelta(hours=self.velocity_window_hours)
        recent_txs = [ts for ts in timestamps if ts >= window_start]
        recent_count = len(recent_txs)

        tx_per_hour = recent_count / max(self.velocity_window_hours, 0.1)

        baseline_txs = [
            ts
            for ts in timestamps
            if ts >= now - timedelta(days=self.baseline_days)
            and ts < window_start
        ]

        if baseline_txs:
            baseline_hours = self.baseline_days * 24
            baseline_rate = len(baseline_txs) / max(baseline_hours, 1)
        else:
            baseline_rate = tx_per_hour

        std_dev = 0
        if baseline_rate > 0 and baseline_txs:
            hourly_counts = defaultdict(int)
            for ts in baseline_txs:
                hour_key = ts.replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour_key] += 1
            if hourly_counts:
                counts = list(hourly_counts.values())
                mean = sum(counts) / len(counts)
                variance = sum((c - mean) ** 2 for c in counts) / len(counts)
                std_dev = math.sqrt(variance)

        velocity_score = 0
        if baseline_rate > 0:
            spike_ratio = tx_per_hour / max(baseline_rate, 0.01)
            velocity_score = min(spike_ratio / 5, 1.0)
        else:
            velocity_score = min(tx_per_hour / self.max_tx_per_hour, 1.0)

        if std_dev > 0:
            deviation_factor = (tx_per_hour - baseline_rate) / max(std_dev, 0.01)
            velocity_score = min(
                velocity_score + 0.3 * min(deviation_factor / 3, 1.0), 1.0
            )

        reason_codes = []
        source_tx_ids = []

        if velocity_score > 0.2:
            recent_tx_ids = [
                tx.get("id", "")
                for tx in transactions
                if self._parse_ts(tx.get("timestamp", "")) is not None
                and self._parse_ts(tx.get("timestamp", "")) >= window_start
            ][:10]
            source_tx_ids.extend(recent_tx_ids)

            time_str = (
                f"{self.velocity_window_hours}h"
                if self.velocity_window_hours >= 1
                else f"{int(self.velocity_window_hours * 60)}m"
            )
            reason_codes.append(
                {
                    "code": "HIGH_VELOCITY",
                    "description": f"Unusually high transfer velocity: {recent_count} transactions in {time_str}.",
                    "severity": round(velocity_score, 2),
                    "source_transaction_ids": recent_tx_ids,
                }
            )

        return {
            "score": round(velocity_score, 4),
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
