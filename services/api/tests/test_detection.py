"""Tests for the detection engine."""
from app.detection.cycle_detector import CycleDetector
from app.detection.engine import RiskEngine, determine_risk_level
from app.detection.layering_detector import LayeringDetector
from app.detection.mule_detector import MuleDetector
from app.detection.structuring_detector import StructuringDetector


def test_determine_risk_level():
    # Thresholds calibrated to blended primary-max scoring: CRITICAL>=60,
    # HIGH>=48, MEDIUM>=35.
    assert determine_risk_level(0) == "LOW"
    assert determine_risk_level(20) == "LOW"
    assert determine_risk_level(35) == "MEDIUM"
    assert determine_risk_level(47) == "MEDIUM"
    assert determine_risk_level(48) == "HIGH"
    assert determine_risk_level(59) == "HIGH"
    assert determine_risk_level(60) == "CRITICAL"
    assert determine_risk_level(100) == "CRITICAL"

def test_risk_engine_initializes():
    engine = RiskEngine()
    assert engine.detectors is not None
    assert len(engine.detectors) > 0

def test_mule_detector():
    detector = MuleDetector()
    transactions = [
        {"id": f"tx{i}", "sender_account_id": f"sender{i}", "receiver_account_id": "MULE-TEST",
         "amount": 1000, "timestamp": "2026-05-15T10:00:00", "currency": "USD"}
        for i in range(15)
    ]
    result = detector.analyze("MULE-TEST", transactions)
    assert result is not None
    assert result["score"] > 0
    assert len(result["reason_codes"]) > 0

def test_mule_detector_clean_account():
    detector = MuleDetector()
    transactions = [
        {"id": f"tx{i}", "sender_account_id": "ALICE", "receiver_account_id": "BOB",
         "amount": 100, "timestamp": f"2026-05-{i+1:02d}T10:00:00", "currency": "USD"}
        for i in range(3)
    ]
    result = detector.analyze("ALICE", transactions)
    # Alice is mostly a sender with few transactions - should be low risk
    assert result["score"] < 0.5

def test_cycle_detector():
    detector = CycleDetector()
    transactions = [
        {"id": "tx1", "sender_account_id": "A", "receiver_account_id": "B",
         "amount": 10000, "timestamp": "2026-05-15T10:00:00"},
        {"id": "tx2", "sender_account_id": "B", "receiver_account_id": "C",
         "amount": 10000, "timestamp": "2026-05-15T12:00:00"},
        {"id": "tx3", "sender_account_id": "C", "receiver_account_id": "A",
         "amount": 10000, "timestamp": "2026-05-15T14:00:00"},
    ]
    result = detector.analyze("A", transactions)
    assert result is not None

def test_layering_detector():
    detector = LayeringDetector()
    transactions = [
        {"id": "tx1", "sender_account_id": "A", "receiver_account_id": "B",
         "amount": 50000, "timestamp": "2026-05-15T09:00:00"},
        {"id": "tx2", "sender_account_id": "B", "receiver_account_id": "C",
         "amount": 48000, "timestamp": "2026-05-15T11:00:00"},
        {"id": "tx3", "sender_account_id": "C", "receiver_account_id": "D",
         "amount": 47000, "timestamp": "2026-05-15T14:00:00"},
        {"id": "tx4", "sender_account_id": "D", "receiver_account_id": "E",
         "amount": 46000, "timestamp": "2026-05-15T16:00:00"},
    ]
    result = detector.analyze("A", transactions)
    assert result is not None

def test_structuring_detector():
    detector = StructuringDetector()
    transactions = [
        {"id": f"tx{i}", "sender_account_id": "STRUCT-TEST", "receiver_account_id": "RECV",
         "amount": 9500, "timestamp": f"2026-05-15T{8 + i}:00:00"}
        for i in range(8)
    ]
    result = detector.analyze("STRUCT-TEST", transactions)
    assert result is not None
    assert result["score"] > 0
