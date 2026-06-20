#!/usr/bin/env python3
"""Synthetic data generator for TrailGuard AI.
Generates deterministic transaction data with seeded suspicious scenarios.

Usage:
    python data/generators/generate_synthetic_data.py

Output:
    data/synthetic/sample_transactions.csv
    data/synthetic/sample_transactions.xlsx
"""
import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "synthetic")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHANNELS = ["online", "branch", "atm", "wire", "mobile"]
COUNTRIES = ["US", "GB", "DE", "FR", "JP", "AU", "CA", "SG", "AE", "CH"]
CURRENCIES = ["USD", "GBP", "EUR", "JPY", "AUD", "CAD", "SGD", "AED", "CHF"]
BASE_TIME = datetime(2026, 5, 15, 0, 0, 0)

columns = [
    "transaction_id", "timestamp", "sender_account_id", "receiver_account_id",
    "amount", "currency", "channel", "sender_country", "receiver_country",
    "device_id", "ip_hash", "sender_account_age_days", "receiver_account_age_days",
    "scenario"
]

def generate_normal_accounts(count=150):
    accounts = []
    for i in range(count):
        age = random.randint(30, 3650)
        accounts.append({
            "id": f"ACC-NORMAL-{i:04d}",
            "country": random.choice(COUNTRIES),
            "age_days": age,
        })
    return accounts

def generate_scenario_accounts():
    return {
        # Scenario A - Mule Ring
        "victims": [{"id": f"VICTIM-{i:03d}", "country": "US", "age_days": random.randint(100, 2000)} for i in range(1, 13)],
        "mule": {"id": "MULE-AX7", "country": "US", "age_days": 14},
        "exits": [{"id": f"EXIT-{i:02d}", "country": random.choice(["US", "GB", "AE"]), "age_days": random.randint(60, 500)} for i in range(1, 5)],

        # Scenario B - Layering
        "layer_a": {"id": "LAYER-A", "country": "GB", "age_days": 120},
        "layer_b": {"id": "LAYER-B", "country": "GB", "age_days": 90},
        "layer_c": {"id": "LAYER-C", "country": "DE", "age_days": 45},
        "layer_d": {"id": "LAYER-D", "country": "DE", "age_days": 30},
        "layer_exit": {"id": "EXIT-L", "country": "CH", "age_days": 200},

        # Scenario C - Circular Flow
        "cycle_a": {"id": "CYCLE-A", "country": "JP", "age_days": 180},
        "cycle_b": {"id": "CYCLE-B", "country": "JP", "age_days": 150},
        "cycle_c": {"id": "CYCLE-C", "country": "JP", "age_days": 60},

        # Scenario D - Structuring
        "structurer": {"id": "STRUCT-01", "country": "US", "age_days": 365},
        "struct_recv": {"id": "STRUCT-RECV-01", "country": "US", "age_days": 400},

        # Scenario E - New account high velocity
        "new_acc": {"id": "NEW-HV-01", "country": "SG", "age_days": 2},
        "new_acc_recv1": {"id": "NEW-RECV-01", "country": "SG", "age_days": 500},
        "new_acc_recv2": {"id": "NEW-RECV-02", "country": "SG", "age_days": 600},
        "new_acc_recv3": {"id": "NEW-RECV-03", "country": "SG", "age_days": 700},
    }

def generate_transactions(accounts, scenario_accounts):
    transactions = []
    tx_id = 1

    def make_tx(sender, receiver, amount, timestamp, channel, currency, scenario=""):
        nonlocal tx_id
        tx = {
            "transaction_id": f"TX-{tx_id:06d}",
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            "sender_account_id": sender["id"],
            "receiver_account_id": receiver["id"],
            "amount": round(amount, 2),
            "currency": currency,
            "channel": channel,
            "sender_country": sender["country"],
            "receiver_country": receiver["country"],
            "device_id": f"DEV-{random.randint(1000, 9999)}",
            "ip_hash": f"hash_{random.getrandbits(64):016x}",
            "sender_account_age_days": sender["age_days"],
            "receiver_account_age_days": receiver["age_days"],
            "scenario": scenario,
        }
        tx_id += 1
        return tx

    # Normal transactions
    for _ in range(2500):
        sender = random.choice(accounts)
        receiver = random.choice([a for a in accounts if a["id"] != sender["id"]])
        ts = BASE_TIME + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        amount = round(random.uniform(10, 25000), 2)
        tx = make_tx(sender, receiver, amount, ts, random.choice(CHANNELS), random.choice(CURRENCIES))
        transactions.append(tx)

    # Scenario A - Mule Ring
    victims = scenario_accounts["victims"]
    mule = scenario_accounts["mule"]
    exits = scenario_accounts["exits"]
    for i, victim in enumerate(victims):
        ts = BASE_TIME + timedelta(days=random.randint(0, 5), hours=random.randint(9, 17))
        tx = make_tx(victim, mule, random.uniform(500, 15000), ts, "wire", "USD", "SCENARIO_A")
        transactions.insert(0, tx)
        # Rapid forward to exits
        fwd_ts = ts + timedelta(minutes=random.randint(1, 25))
        exit_acc = random.choice(exits)
        fwd_tx = make_tx(mule, exit_acc, round(tx["amount"] * random.uniform(0.8, 0.95), 2), fwd_ts, "wire", "USD", "SCENARIO_A")
        transactions.insert(1, fwd_tx)

    # Scenario B - Layering
    layer_chain = [
        scenario_accounts["layer_a"], scenario_accounts["layer_b"],
        scenario_accounts["layer_c"], scenario_accounts["layer_d"],
        scenario_accounts["layer_exit"],
    ]
    base_ts = BASE_TIME + timedelta(days=10, hours=9)
    for i in range(len(layer_chain) - 1):
        ts = base_ts + timedelta(hours=i * 2, minutes=random.randint(10, 50))
        amount = round(random.uniform(5000, 50000) / (2 if i > 0 else 1), 2)
        tx = make_tx(layer_chain[i], layer_chain[i+1], amount, ts, "online", "GBP", "SCENARIO_B")
        transactions.append(tx)

    # Scenario C - Circular Flow
    cycle = [scenario_accounts["cycle_a"], scenario_accounts["cycle_b"], scenario_accounts["cycle_c"]]
    base_ts = BASE_TIME + timedelta(days=15, hours=14)
    for i in range(3):
        ts = base_ts + timedelta(hours=i * 3)
        amt = round(random.uniform(8000, 12000), 2)
        sender = cycle[i]
        receiver = cycle[(i + 1) % 3]
        tx = make_tx(sender, receiver, amt, ts, "wire", "JPY", "SCENARIO_C")
        transactions.append(tx)

    # Scenario D - Structuring
    struct = scenario_accounts["structurer"]
    struct_recv = scenario_accounts["struct_recv"]
    base_ts = BASE_TIME + timedelta(days=20, hours=10)
    total_struct = 0
    for i in range(15):
        ts = base_ts + timedelta(hours=random.randint(0, 8), minutes=random.randint(0, 59))
        amt = round(random.uniform(7000, 9999), 2)
        total_struct += amt
        tx = make_tx(struct, struct_recv, amt, ts, "atm", "USD", "SCENARIO_D")
        transactions.append(tx)

    # Scenario E - New account high velocity
    new_acc = scenario_accounts["new_acc"]
    receivers = [
        scenario_accounts["new_acc_recv1"],
        scenario_accounts["new_acc_recv2"],
        scenario_accounts["new_acc_recv3"],
    ]
    base_ts = BASE_TIME + timedelta(days=25, hours=8)
    for i in range(20):
        ts = base_ts + timedelta(hours=random.randint(0, 4), minutes=random.randint(0, 59))
        recv = random.choice(receivers)
        tx = make_tx(new_acc, recv, random.uniform(10000, 45000), ts, "wire", "SGD", "SCENARIO_E")
        transactions.append(tx)

    return transactions

def write_csv(transactions):
    path = os.path.join(OUTPUT_DIR, "sample_transactions.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(transactions)
    print(f"CSV written: {path} ({len(transactions)} rows)")

def write_xlsx(transactions):
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(columns)
        for tx in transactions:
            ws.append([tx[c] for c in columns])
        path = os.path.join(OUTPUT_DIR, "sample_transactions.xlsx")
        wb.save(path)
        print(f"XLSX written: {path}")
    except ImportError:
        print("openpyxl not available, skipping XLSX")

if __name__ == "__main__":
    print("Generating synthetic data...")
    normal_accounts = generate_normal_accounts(200)
    scenario_accounts = generate_scenario_accounts()
    all_accounts = normal_accounts + [v for v in scenario_accounts.values() if isinstance(v, dict)]
    for victims in [v for v in scenario_accounts.values() if isinstance(v, list)]:
        all_accounts.extend(victims)

    transactions = generate_transactions(normal_accounts, scenario_accounts)
    write_csv(transactions)
    write_xlsx(transactions)
    print(f"Total accounts: {len(all_accounts)}")
    print("Done!")
