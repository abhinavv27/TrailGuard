"""
Risk Engine - combines multiple detectors into a unified risk score.
"""
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ReasonCode:
    code: str
    description: str
    severity: float  # 0.0 to 1.0
    source_transaction_ids: List[str] = field(default_factory=list)


@dataclass
class RiskResult:
    entity_id: str
    entity_type: str  # 'account' or 'transaction'
    risk_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    component_scores: Dict[str, float] = field(default_factory=dict)
    reason_codes: List[Dict[str, Any]] = field(default_factory=list)
    source_transaction_ids: List[str] = field(default_factory=list)
    detector_versions: Dict[str, str] = field(default_factory=dict)
    analysis_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


def determine_risk_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


class RiskEngine:
    """
    Combines multiple detection signals into a unified risk assessment.
    Score composition:
      - 30% Anomaly score (statistical outliers)
      - 30% AML pattern severity (known fraud patterns)
      - 25% Graph/network risk (connections to other risky entities)
      - 15% Temporal/velocity risk (unusual timing patterns)
    """

    def __init__(self):
        self.detectors = {}
        self._load_detectors()

    def _load_detectors(self):
        """Register all available detectors."""
        try:
            from app.detection.anomaly_scorer import AnomalyScorer
            from app.detection.counterparty_detector import CounterpartyDetector
            from app.detection.cycle_detector import CycleDetector
            from app.detection.layering_detector import LayeringDetector
            from app.detection.mule_detector import MuleDetector
            from app.detection.structuring_detector import StructuringDetector
            from app.detection.velocity_detector import VelocityDetector

            self.detectors = {
                "mule": MuleDetector(),
                "layering": LayeringDetector(),
                "cycle": CycleDetector(),
                "structuring": StructuringDetector(),
                "velocity": VelocityDetector(),
                "anomaly": AnomalyScorer(),
                "counterparty": CounterpartyDetector(),
            }
            logger.info(f"Loaded {len(self.detectors)} detectors")
        except Exception as e:
            logger.error(f"Failed to load detectors: {e}")

    def analyze_account(
        self, account_id: str, transactions: List[Dict], db_session=None
    ) -> RiskResult:
        """Run all detectors on an account and produce a unified risk score."""
        component_scores = {}
        all_reason_codes = []
        all_source_tx_ids = set()
        detector_versions = {}

        for name, detector in self.detectors.items():
            try:
                result = detector.analyze(account_id, transactions, db_session)
                if result:
                    component_scores[name] = result.get("score", 0)
                    all_reason_codes.extend(result.get("reason_codes", []))
                    all_source_tx_ids.update(result.get("source_transaction_ids", []))
                    detector_versions[name] = result.get("version", "1.0")
            except Exception as e:
                logger.error(
                    f"Detector {name} failed for account {account_id}: {e}"
                )
                component_scores[name] = 0

        weights = {
            "mule": 0.25,
            "layering": 0.15,
            "cycle": 0.10,
            "structuring": 0.10,
            "velocity": 0.10,
            "anomaly": 0.15,
            "counterparty": 0.15,
        }
        raw_score = sum(
            component_scores.get(k, 0) * w for k, w in weights.items()
        )
        risk_score = round(min(raw_score * 100, 100), 2)
        risk_level = determine_risk_level(risk_score)

        return RiskResult(
            entity_id=account_id,
            entity_type="account",
            risk_score=risk_score,
            risk_level=risk_level,
            component_scores={
                k: round(v * 100, 2) for k, v in component_scores.items()
            },
            reason_codes=[self._reason_to_dict(rc) for rc in all_reason_codes],
            source_transaction_ids=list(all_source_tx_ids),
            detector_versions=detector_versions,
        )

    def analyze_transaction(
        self, transaction: Dict, account_context: Optional[Dict] = None
    ) -> RiskResult:
        """Analyze a single transaction."""
        score = 0
        reason_codes = []

        if transaction.get("amount", 0) > 50000:
            score += 0.3
            reason_codes.append(
                ReasonCode(
                    code="HIGH_VALUE",
                    description=f"High-value transfer: {transaction.get('amount')}",
                    severity=0.3,
                    source_transaction_ids=[transaction.get("id", "")],
                )
            )
        if transaction.get("sender_country") != transaction.get(
            "receiver_country"
        ):
            score += 0.1
            reason_codes.append(
                ReasonCode(
                    code="CROSS_BORDER",
                    description="Cross-border transaction",
                    severity=0.1,
                    source_transaction_ids=[transaction.get("id", "")],
                )
            )
        if account_context and account_context.get("account_age_days", 365) < 7:
            score += 0.2
            reason_codes.append(
                ReasonCode(
                    code="NEW_ACCOUNT",
                    description="Transaction involves a recently created account",
                    severity=0.2,
                    source_transaction_ids=[transaction.get("id", "")],
                )
            )

        risk_score = round(min(score * 100, 100), 2)
        return RiskResult(
            entity_id=transaction.get("id", ""),
            entity_type="transaction",
            risk_score=risk_score,
            risk_level=determine_risk_level(risk_score),
            component_scores={"base": score * 100},
            reason_codes=[self._reason_to_dict(rc) for rc in reason_codes],
            source_transaction_ids=[transaction.get("id", "")],
            detector_versions={"base": "1.0"},
        )

    def _reason_to_dict(self, rc) -> Dict:
        if isinstance(rc, dict):
            return rc
        return {
            "code": rc.code,
            "description": rc.description,
            "severity": rc.severity,
            "source_transaction_ids": rc.source_transaction_ids,
        }

    def get_detector_versions(self) -> Dict[str, str]:
        return {
            name: getattr(d, "version", "1.0")
            for name, d in self.detectors.items()
        }
