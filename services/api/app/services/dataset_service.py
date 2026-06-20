import hashlib
import uuid
from io import BytesIO, StringIO

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.dataset import Dataset


class DatasetService:

    REQUIRED_COLUMNS = {
        "transaction_id",
        "timestamp",
        "sender_account_id",
        "receiver_account_id",
        "amount",
        "currency",
        "channel",
        "sender_country",
        "receiver_country",
        "device_id",
        "ip_hash",
        "sender_account_age_days",
        "receiver_account_age_days",
    }

    OPTIONAL_COLUMNS = {
        "merchant_category",
        "reference",
        "scenario",
        "label",
    }

    @staticmethod
    def _compute_file_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> list[str]:
        errors = []
        missing = DatasetService.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
        if df.empty:
            errors.append("File is empty")
        return errors

    @staticmethod
    async def upload_dataset(
        file: UploadFile, user_id: str, db: Session
    ) -> Dataset:
        from datetime import datetime
        from app.models.account import Account
        from app.models.transaction import Transaction

        content = await file.read()
        file_hash = DatasetService._compute_file_hash(content)

        if len(content) > settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {settings.UPLOAD_MAX_SIZE_MB}MB limit",
            )

        try:
            if file.filename and file.filename.endswith(".xlsx"):
                df = pd.read_excel(BytesIO(content))
            else:
                df = pd.read_csv(StringIO(content.decode("utf-8")))
            errors = DatasetService.validate_columns(df)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse file: {e}",
            )

        dataset = Dataset(
            user_id=user_id,
            filename=file.filename or "upload",
            original_filename=file.filename or "upload",
            file_size=len(content),
            file_hash=file_hash,
            row_count=len(df),
            status="uploaded",
        )
        db.add(dataset)
        db.flush()

        account_cache = {}
        for _, row in df.iterrows():
            for col, age_col in [("sender_account_id", "sender_account_age_days"), ("receiver_account_id", "receiver_account_age_days")]:
                ref = str(row[col])
                if ref not in account_cache:
                    account = Account(
                        dataset_id=dataset.id,
                        external_account_ref=ref,
                        masked_account_ref=ref[:4] + "****" + ref[-4:] if len(ref) > 8 else ref,
                        country=str(row.get("sender_country" if "sender" in col else "receiver_country", "US")),
                        account_age_days=int(row.get(age_col, 365)),
                    )
                    db.add(account)
                    db.flush()
                    account_cache[ref] = account.id

        tx_count = 0
        for _, row in df.iterrows():
            ts_str = str(row["timestamp"])
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                try:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    ts = datetime.utcnow()

            tx = Transaction(
                dataset_id=dataset.id,
                external_transaction_ref=str(row.get("transaction_id", f"tx-{tx_count}")),
                timestamp=ts,
                sender_account_id=account_cache.get(str(row["sender_account_id"]), ""),
                receiver_account_id=account_cache.get(str(row["receiver_account_id"]), ""),
                amount=float(row["amount"]),
                currency=str(row.get("currency", "USD")),
                channel=str(row.get("channel", "online")),
                sender_country=str(row.get("sender_country", "US")),
                receiver_country=str(row.get("receiver_country", "US")),
                device_hash=str(row.get("device_id", "")),
                ip_hash=str(row.get("ip_hash", "")),
                scenario=str(row.get("scenario", "")),
            )
            db.add(tx)
            tx_count += 1

        dataset.row_count = tx_count
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def process_dataset(dataset_id: str, db: Session) -> Dataset:
        from datetime import datetime, timezone
        from app.detection.engine import RiskEngine
        from app.models.account import Account
        from app.models.transaction import Transaction
        from app.models.analysis_run import AnalysisRun
        from app.models.risk_assessment import AccountRiskAssessment
        from app.models.detection_event import DetectionEvent
        from app.models.graph_metrics import GraphMetrics
        from app.graph.builder import GraphBuilder

        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        dataset.status = "processing"
        db.commit()

        run = AnalysisRun(
            dataset_id=dataset_id,
            user_id=None,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.flush()

        try:
            transactions = db.query(Transaction).filter(
                Transaction.dataset_id == dataset_id
            ).all()

            accounts = db.query(Account).filter(
                Account.dataset_id == dataset_id
            ).all()

            engine = RiskEngine()
            builder = GraphBuilder()
            tx_dicts_all = [{
                "id": str(t.id), "amount": t.amount, "timestamp": str(t.timestamp),
                "sender_account_id": str(t.sender_account_id),
                "receiver_account_id": str(t.receiver_account_id),
                "currency": t.currency, "channel": t.channel,
            } for t in transactions]
            G = builder.build_graph(tx_dicts_all)

            alert_count = 0
            for account in accounts:
                account_txs = [t for t in transactions if
                              str(t.sender_account_id) == str(account.id) or
                              str(t.receiver_account_id) == str(account.id)]
                tx_dicts = [{
                    "id": str(t.id), "amount": t.amount, "timestamp": str(t.timestamp),
                    "sender_account_id": str(t.sender_account_id),
                    "receiver_account_id": str(t.receiver_account_id),
                    "currency": t.currency, "channel": t.channel,
                } for t in account_txs]

                result = engine.analyze_account(str(account.id), tx_dicts, db)

                assessment = AccountRiskAssessment(
                    account_id=account.id,
                    analysis_run_id=run.id,
                    risk_score=result.risk_score,
                    risk_level=result.risk_level,
                    component_scores_json=result.component_scores,
                    reason_codes_json={"reasons": result.reason_codes},
                )
                db.add(assessment)

                if result.risk_level in ("HIGH", "CRITICAL"):
                    alert_count += 1
                    event = DetectionEvent(
                        dataset_id=dataset_id,
                        analysis_run_id=run.id,
                        event_type="risk_alert",
                        severity=result.risk_level,
                        entity_type="account",
                        entity_id=str(account.id),
                        risk_score=result.risk_score,
                        reason_codes_json={"reasons": result.reason_codes},
                        evidence_json={"component_scores": result.component_scores},
                    )
                    db.add(event)

                m = builder.get_account_metrics(G, str(account.id))
                gm = GraphMetrics(
                    account_id=account.id,
                    analysis_run_id=run.id,
                    betweenness_centrality=m.get("betweenness", 0),
                    in_degree=m.get("in_degree", 0),
                    out_degree=m.get("out_degree", 0),
                    in_total_value=m.get("in_total", 0),
                    out_total_value=m.get("out_total", 0),
                    in_unique_counterparties=m.get("in_unique_counterparties", 0),
                    out_unique_counterparties=m.get("out_unique_counterparties", 0),
                    in_cycle=str(m.get("in_cycle", False)).lower(),
                    cycle_count=m.get("cycle_count", 0),
                )
                db.add(gm)

            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            run.metrics_json = {
                "total_accounts": len(accounts),
                "total_transactions": len(transactions),
                "alerts_generated": alert_count,
            }
            dataset.status = "analyzed"
            db.commit()
            db.refresh(dataset)
        except Exception as e:
            dataset.status = "error"
            dataset.error_message = str(e)
            run.status = "failed"
            run.error_message = str(e)
            db.commit()

        return dataset
