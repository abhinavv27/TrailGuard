"""Database seeding script for TrailGuard AI."""
import os
import sys
from datetime import datetime

# Add the api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.account import Account
from app.models.dataset import Dataset
from app.models.transaction import Transaction
from app.models.user import User

DEMO_USERS = [
    {"email": "admin@trailguard.ai", "password": "admin1234", "display_name": "Admin User", "role": "admin"},
    {"email": "analyst@trailguard.ai", "password": "demo1234", "display_name": "Analyst User", "role": "analyst"},
]

def seed_database():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed users
        for user_data in DEMO_USERS:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    display_name=user_data["display_name"],
                    role=user_data["role"],
                )
                db.add(user)
                print(f"  Created user: {user_data['email']}")
            else:
                print(f"  User exists: {user_data['email']}")

        db.flush()
        # Datasets are owned by the admin user
        owner = db.query(User).filter(User.email == DEMO_USERS[0]["email"]).first()

        # Try to seed synthetic data
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "data", "synthetic", "sample_transactions.csv")
        if os.path.exists(csv_path):
            print(f"Loading synthetic data from {csv_path}...")
            import csv
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                tx_count = 0
                seen_refs = set()  # autoflush=False, so dedup accounts in-memory
                for row in reader:
                    # Check if dataset exists
                    dataset = db.query(Dataset).filter(Dataset.filename == "synthetic_seed").first()
                    if not dataset:
                        dataset = Dataset(
                            user_id=owner.id,
                            filename="synthetic_seed",
                            original_filename="sample_transactions.csv",
                            file_size=os.path.getsize(csv_path),
                            file_hash="synthetic_seed",
                            row_count=0,
                            status="uploaded",
                        )
                        db.add(dataset)
                        db.flush()

                    # Create account refs
                    for acc_ref in [row["sender_account_id"], row["receiver_account_id"]]:
                        if acc_ref not in seen_refs:
                            seen_refs.add(acc_ref)
                            account = Account(
                                dataset_id=dataset.id,
                                external_account_ref=acc_ref,
                                masked_account_ref=acc_ref[:4] + "****" + acc_ref[-4:] if len(acc_ref) > 8 else acc_ref,
                                country=row.get("sender_country", "US"),
                                account_age_days=int(row.get("sender_account_age_days", 365)),
                            )
                            db.add(account)

                    # Create transaction
                    tx = Transaction(
                        dataset_id=dataset.id,
                        external_transaction_ref=row["transaction_id"],
                        timestamp=datetime.fromisoformat(row["timestamp"]) if "T" in row.get("timestamp", "") else datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
                        sender_account_id=row["sender_account_id"],
                        receiver_account_id=row["receiver_account_id"],
                        amount=float(row["amount"]),
                        currency=row.get("currency", "USD"),
                        channel=row.get("channel", "online"),
                        sender_country=row.get("sender_country", "US"),
                        receiver_country=row.get("receiver_country", "US"),
                        device_hash=row.get("device_id", ""),
                        ip_hash=row.get("ip_hash", ""),
                        scenario=row.get("scenario", ""),
                    )
                    db.add(tx)
                    tx_count += 1
                    if tx_count % 500 == 0:
                        print(f"  Loaded {tx_count} transactions...")

                if dataset:
                    dataset.row_count = tx_count
                    dataset.status = "analyzed"

            print(f"  Loaded {tx_count} synthetic transactions")
        else:
            print(f"  Synthetic data not found at {csv_path} (optional, can generate later)")

        db.commit()
        print("\nDatabase seeded successfully!")
        print("Demo credentials:")
        for u in DEMO_USERS:
            print(f"  {u['email']} / {u['password']} ({u['role']})")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
