"""Regression tests for the CSV-upload ingest + analysis path.

These cover two bugs the upload path had that the seeded demo path masked:
1. process_dataset() looked accounts up by external_account_ref while the
   uploaded transactions/graph are keyed by the account UUID, so no
   transactions were ever associated with an account (zero alerts, zero
   graph metrics) for uploaded datasets.
2. upload_dataset() computed validate_columns() but discarded the result, so
   a file missing required columns was not rejected with a clean 400.
"""
from datetime import datetime, timedelta
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile


def test_process_dataset_associates_uuid_keyed_transactions(db_session, demo_user):
    """Uploaded transactions are keyed by Account.id (UUID). Analysis must
    associate them with their accounts; before the fix every account saw an
    empty transaction list and all graph metrics came back zero."""
    from app.models.account import Account
    from app.models.dataset import Dataset
    from app.models.graph_metrics import GraphMetrics
    from app.models.risk_assessment import AccountRiskAssessment
    from app.models.transaction import Transaction
    from app.services.dataset_service import DatasetService

    ds = Dataset(
        user_id=demo_user.id,
        filename="up.csv",
        original_filename="up.csv",
        file_size=1,
        file_hash="hash-upload",
        row_count=0,
        status="uploaded",
    )
    db_session.add(ds)
    db_session.flush()

    # Upload convention (mirrors DatasetService.upload_dataset): the
    # transaction FK stores the account UUID, not the external ref.
    refs = ["ACCT-ALPHA", "ACCT-BRAVO", "ACCT-CHARLIE", "ACCT-DELTA"]
    ids = {}
    for ref in refs:
        acct = Account(
            dataset_id=ds.id,
            external_account_ref=ref,
            masked_account_ref=ref,
            country="US",
            account_age_days=365,
        )
        db_session.add(acct)
        db_session.flush()
        ids[ref] = acct.id  # UUID, differs from external_account_ref

    base = datetime(2024, 1, 1, 9, 0, 0)
    edges = [
        ("ACCT-ALPHA", "ACCT-BRAVO"), ("ACCT-BRAVO", "ACCT-CHARLIE"),
        ("ACCT-CHARLIE", "ACCT-ALPHA"), ("ACCT-ALPHA", "ACCT-BRAVO"),
        ("ACCT-BRAVO", "ACCT-DELTA"), ("ACCT-DELTA", "ACCT-ALPHA"),
        ("ACCT-ALPHA", "ACCT-CHARLIE"), ("ACCT-CHARLIE", "ACCT-DELTA"),
        ("ACCT-DELTA", "ACCT-BRAVO"),
    ]
    for i, (s, r) in enumerate(edges):
        db_session.add(Transaction(
            dataset_id=ds.id,
            external_transaction_ref=f"tx{i}",
            timestamp=base + timedelta(hours=i),
            sender_account_id=ids[s],
            receiver_account_id=ids[r],
            amount=1000.0 + i,
            currency="USD",
            channel="online",
        ))
    db_session.commit()

    DatasetService.process_dataset(ds.id, db_session)

    db_session.refresh(ds)
    assert ds.status == "analyzed", ds.error_message

    # One assessment per account means the loop ran to completion.
    assert db_session.query(AccountRiskAssessment).count() == len(refs)

    # The smoking gun: with the keying bug every account's transactions were
    # looked up under the wrong identifier, so all graph degrees were zero.
    metrics = db_session.query(GraphMetrics).all()
    total_degree = sum((m.in_degree or 0) + (m.out_degree or 0) for m in metrics)
    assert total_degree > 0, (
        "process_dataset did not associate any transactions with accounts "
        "(graph metrics all zero) — upload-path account keying is broken"
    )


async def test_upload_rejects_missing_required_columns(db_session, demo_user):
    """A file missing required columns must be rejected with a clean 400,
    not silently accepted (and then crash deeper with a KeyError)."""
    from app.services.dataset_service import DatasetService

    bad = b"foo,bar\n1,2\n3,4\n"
    file = UploadFile(filename="bad.csv", file=BytesIO(bad))

    with pytest.raises(HTTPException) as exc:
        await DatasetService.upload_dataset(file, demo_user.id, db_session)

    assert exc.value.status_code == 400
    assert "Missing required columns" in exc.value.detail


async def test_upload_accepts_valid_file(db_session, demo_user):
    """A well-formed file with all required columns still ingests cleanly
    (guards against the validation refactor rejecting good uploads)."""
    from app.models.account import Account
    from app.models.transaction import Transaction
    from app.services.dataset_service import DatasetService

    header = (
        "transaction_id,timestamp,sender_account_id,receiver_account_id,amount,"
        "currency,channel,sender_country,receiver_country,device_id,ip_hash,"
        "sender_account_age_days,receiver_account_age_days"
    )
    rows = [
        "t1,2024-01-01 09:00:00,ACC-A,ACC-B,1000,USD,online,US,US,d1,h1,400,300",
        "t2,2024-01-01 10:00:00,ACC-B,ACC-C,500,USD,online,US,US,d2,h2,300,200",
    ]
    good = ("\n".join([header, *rows]) + "\n").encode("utf-8")
    file = UploadFile(filename="good.csv", file=BytesIO(good))

    dataset = await DatasetService.upload_dataset(file, demo_user.id, db_session)

    assert dataset.row_count == 2
    assert db_session.query(Transaction).filter(
        Transaction.dataset_id == dataset.id
    ).count() == 2
    # 3 distinct account refs across the two rows
    assert db_session.query(Account).filter(
        Account.dataset_id == dataset.id
    ).count() == 3
