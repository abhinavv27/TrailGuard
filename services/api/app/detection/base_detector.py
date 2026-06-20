"""Base class for all detectors."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseDetector(ABC):
    """Abstract base for all detection modules."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Return detector version string."""
        pass

    @abstractmethod
    def analyze(self, account_id: str, transactions: List[Dict], db_session=None) -> Optional[Dict]:
        """
        Analyze an account and return detection results.
        Returns dict with: score (0-1), reason_codes (list), source_transaction_ids (list)
        """
        pass
