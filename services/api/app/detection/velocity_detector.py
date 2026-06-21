"""Transaction velocity detection."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

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

        # Genuine velocity = many transactions clustered in a short window.
        # Find the busiest sliding window of velocity_window_hours and score it
        # against max_tx_per_hour. Comparing "1 recent tx" to a rate spread over
        # 30 days made every account look like a spike, which is why this used
        # to saturate at 1.0 for nearly everyone.
        timestamps.sort()
        window_sec = self.velocity_window_hours * 3600
        max_in_window = 1
        j = 0
        for i in range(len(timestamps)):
            while (timestamps[i] - timestamps[j]).total_seconds() > window_sec:
                j += 1
            max_in_window = max(max_in_window, i - j + 1)

        now = timestamps[-1]
        window_start = now - timedelta(hours=self.velocity_window_hours)
        recent_count = max_in_window
        tx_per_hour = max_in_window / max(self.velocity_window_hours, 0.1)
        velocity_score = min(tx_per_hour / self.max_tx_per_hour, 1.0)

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
