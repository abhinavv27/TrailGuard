"""
Risk Engine - combines multiple detectors into a unified risk score.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

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
    # Thresholds calibrated to the blended primary-max scoring: a single clear
    # laundering pattern lands ~60-66, layering conduits ~55-59, and normal
    # high-volume accounts top out ~45. Alerts fire on HIGH/CRITICAL.
    if score >= 60:
        return "CRITICAL"
    if score >= 48:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


class RiskEngine:
    """
    Combines multiple detection signals into a unified risk assessment.
    Score composition:
      - 25% Mule detection (fan-in/fan-out funnel accounts)
      - 15% Layering detection (multi-hop money chains)
      - 15% Anomaly score (statistical outliers via Isolation Forest)
      - 15% Counterparty risk (sudden counterparty expansion)
      - 10% Cycle detection (circular flow patterns)
      - 10% Structuring detection (smurfing near-threshold deposits)
      - 10% Velocity detection (unusual transaction frequency)
    """

    def __init__(self):
        self.detectors = {}
        # Dataset-wide context, populated by prepare_dataset(). Detectors that
        # need the whole graph (layering) or whole dataset (anomaly) read from
        # here instead of their per-account transaction slice.
        self.reference_time = None
        self._anomalous_tx_ids = set()
        self._layering_results = {}
        self._cycle_results = {}
        self._load_detectors()

    def prepare_dataset(self, all_transactions: List[Dict]):
        """Compute dataset-wide context once before scoring individual accounts.

        Fixes two root-cause classes:
          - Wall-clock anchoring: derive a reference_time from the data's own
            max timestamp and push it to time-windowed detectors, so windows
            work for any dataset (not just data from the last few hours).
          - Per-account scoping: run anomaly across the FULL dataset (so
            Isolation Forest has enough samples) and layering across the FULL
            graph (so multi-hop chains are visible), then map results back to
            individual accounts.
        """
        # Reference time = the dataset's own "now".
        ref = None
        for tx in all_transactions:
            ts = self._parse_ts(tx.get("timestamp", ""))
            if ts and (ref is None or ts > ref):
                ref = ts
        self.reference_time = ref
        for detector in self.detectors.values():
            if hasattr(detector, "reference_time"):
                detector.reference_time = ref

        # Dataset-wide anomaly: flag anomalous transactions across everything.
        self._anomalous_tx_ids = set()
        anomaly = self.detectors.get("anomaly")
        if anomaly is not None and hasattr(anomaly, "flag_dataset"):
            try:
                self._anomalous_tx_ids = anomaly.flag_dataset(all_transactions)
            except Exception as e:
                logger.error(f"Dataset anomaly pass failed: {e}")

        # Whole-graph layering: find chains once and attribute to accounts.
        self._layering_results = {}
        layering = self.detectors.get("layering")
        if layering is not None and hasattr(layering, "analyze_dataset"):
            try:
                self._layering_results = layering.analyze_dataset(all_transactions)
            except Exception as e:
                logger.error(f"Dataset layering pass failed: {e}")

        # Whole-graph cycle detection: find circular flows once.
        self._cycle_results = {}
        cycle = self.detectors.get("cycle")
        if cycle is not None and hasattr(cycle, "analyze_dataset"):
            try:
                self._cycle_results = cycle.analyze_dataset(all_transactions)
            except Exception as e:
                logger.error(f"Dataset cycle pass failed: {e}")

    def _parse_ts(self, ts_str):
        if not ts_str:
            return None
        try:
            return datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(str(ts_str), "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                return None

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

    def _account_anomaly_result(self, transactions: List[Dict]) -> Optional[Dict]:
        """Anomaly score for one account, derived from the dataset-wide flags
        computed in prepare_dataset(). Falls back to a per-account pass when no
        dataset context was prepared (e.g. direct unit-test calls)."""
        if not self._anomalous_tx_ids:
            if self.reference_time is None and transactions:
                # No dataset prep happened; preserve old per-account behavior.
                return self.detectors["anomaly"].analyze("__account__", transactions)
            return None
        if not transactions:
            return None
        flagged = [tx for tx in transactions if tx.get("id") in self._anomalous_tx_ids]
        if not flagged:
            return None
        anomaly_ratio = len(flagged) / len(transactions)
        # Scale by absolute evidence: a single flagged transaction is weak
        # (otherwise every 1-tx victim account saturates to 1.0). Needs ~3
        # flagged transactions for full confidence.
        confidence = min(len(flagged) / 3, 1.0)
        score = min(anomaly_ratio * 1.5, 1.0) * confidence
        return {
            "score": round(score, 4),
            "reason_codes": [
                {
                    "code": "STATISTICAL_ANOMALY",
                    "description": f"{len(flagged)} of {len(transactions)} transactions flagged as statistical outliers (dataset-wide Isolation Forest).",
                    "severity": round(score, 2),
                    "source_transaction_ids": [tx.get("id", "") for tx in flagged][:10],
                }
            ],
            "source_transaction_ids": [tx.get("id", "") for tx in flagged][:20],
            "version": getattr(self.detectors.get("anomaly"), "version", "1.3.0"),
        }

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
                if name == "anomaly":
                    result = self._account_anomaly_result(transactions)
                elif name == "layering":
                    result = self._layering_results.get(account_id)
                elif name == "cycle":
                    result = self._cycle_results.get(account_id)
                else:
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
        weighted_sum = sum(
            component_scores.get(k, 0) * w for k, w in weights.items()
        )

        # A single decisive fraud pattern should produce a high score on its
        # own; a pure weighted average buries strong evidence (e.g. a clear
        # structuring case at 0.9 would only contribute 0.09). "Primary"
        # detectors capture a concrete laundering behaviour and can drive risk
        # alone; supporting detectors (velocity/anomaly/counterparty) only
        # corroborate. Final score blends the strongest primary signal with the
        # corroborating weighted sum.
        PRIMARY = ("mule", "layering", "cycle", "structuring")
        max_primary = max((component_scores.get(k, 0) for k in PRIMARY), default=0)
        raw_score = 0.65 * max_primary + 0.35 * weighted_sum
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
