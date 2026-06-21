"""Structuring/smurfing detection."""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)


class StructuringDetector(BaseDetector):
    """
    Detects structuring/smurfing patterns where large amounts are split
    into multiple smaller transfers just below a reporting threshold.
    """

    version = "1.0.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.threshold = self.config.get("threshold", 10000)
        self.time_window_hours = self.config.get("time_window_hours", 24)
        self.min_near_threshold = self.config.get("min_near_threshold", 3)

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions:
            return None

        near_threshold = [
            tx
            for tx in transactions
            if tx.get("amount", 0) < self.threshold
            and tx.get("amount", 0) >= self.threshold * 0.8
        ]

        if len(near_threshold) < self.min_near_threshold:
            return None

        windows = self._find_structuring_windows(near_threshold)
        if not windows:
            return None

        best_window = max(windows, key=lambda w: len(w))
        window_tx_count = len(best_window)
        window_total = sum(tx.get("amount", 0) for tx in best_window)
        window_time = self._window_time_span(best_window)

        score = min(
            0.35 * min(window_tx_count / 10, 1.0)
            + 0.35 * min(window_total / (self.threshold * 3), 1.0)
            + 0.30 * self._time_compression_score(best_window),
            1.0,
        )

        tx_ids = [tx.get("id", "") for tx in best_window]
        reason_codes = [
            {
                "code": "STRUCTURING",
                "description": f"{window_tx_count} transfers just below ${self.threshold} threshold within {window_time} (total: ${round(window_total, 2)}).",
                "severity": round(score, 2),
                "source_transaction_ids": tx_ids,
            }
        ]

        return {
            "score": round(score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": tx_ids,
            "version": self.version,
        }

    def _find_structuring_windows(
        self, near_threshold: List[Dict]
    ) -> List[List[Dict]]:
        """Group near-threshold transactions into time windows."""
        sorted_tx = sorted(
            near_threshold,
            key=lambda tx: self._parse_ts(tx.get("timestamp", "")) or datetime.min,
        )

        windows = []
        current_window = []

        for tx in sorted_tx:
            ts = self._parse_ts(tx.get("timestamp", ""))
            if not ts:
                continue

            if not current_window:
                current_window.append(tx)
            else:
                window_start = self._parse_ts(
                    current_window[0].get("timestamp", "")
                )
                if window_start and (ts - window_start).total_seconds() <= self.time_window_hours * 3600:
                    current_window.append(tx)
                else:
                    if len(current_window) >= self.min_near_threshold:
                        windows.append(current_window)
                    current_window = [tx]

        if len(current_window) >= self.min_near_threshold:
            windows.append(current_window)

        return windows

    def _window_time_span(self, window: List[Dict]) -> str:
        timestamps = [
            self._parse_ts(tx.get("timestamp", ""))
            for tx in window
            if self._parse_ts(tx.get("timestamp", ""))
        ]
        if len(timestamps) >= 2:
            delta = max(timestamps) - min(timestamps)
            hours = delta.total_seconds() / 3600
            if hours < 1:
                return f"{int(delta.total_seconds() // 60)}m"
            return f"{int(hours)}h"
        return "N/A"

    def _time_compression_score(self, window: List[Dict]) -> float:
        timestamps = [
            self._parse_ts(tx.get("timestamp", ""))
            for tx in window
            if self._parse_ts(tx.get("timestamp", ""))
        ]
        if len(timestamps) < 2:
            return 0
        delta = max(timestamps) - min(timestamps)
        if delta.total_seconds() == 0:
            return 1.0
        hours = delta.total_seconds() / 3600
        return max(0, 1 - hours / self.time_window_hours)

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
