"""
Ingest generated data into Firebase Firestore.

Loads users, accounts, and transactions from JSON files into Firestore.
"""

import json
import os
import sys
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore


def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")

        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print(f"Initialized Firebase with service account: {service_account_path}")
        else:
            print(f"ERROR: Service account file not found: {service_account_path}")
            print("Please create a service account JSON file from Firebase Console:")
            print("  1. Go to Firebase Console > Project Settings > Service Accounts")
            print("  2. Click 'Generate New Private Key'")
            print("  3. Save as firebase-service-account.json")
            sys.exit(1)

    return firestore.client()


def load_json_file(filepath: str):
    """Load JSON data from file."""
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return []

    with open(filepath, "r") as f:
        return json.load(f)


def ingest_users(db, users):
    """Ingest users into Firestore."""
    print(f"\nIngesting {len(users)} users...")
    batch = db.batch()
    count = 0

    for user in users:
        user_id = user["user_id"]
        user_ref = db.collection("users").document(user_id)

        user_data = {
            "name": user["name"],
            "email": user.get("email", ""),
            "created_at": user.get("created_at", datetime.now().isoformat()),
            "income": user.get("income", 0)
        }

        batch.set(user_ref, user_data)
        count += 1

        if count % 100 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Committed {count} users...")

    if count % 100 != 0:
        batch.commit()

    print(f"✓ Ingested {count} users")


def ingest_accounts(db, accounts):
    """Ingest accounts into Firestore."""
    print(f"\nIngesting {len(accounts)} accounts...")
    batch = db.batch()
    count = 0

    for account in accounts:
        user_id = account["user_id"]
        account_id = account["account_id"]

        account_ref = db.collection("users").document(user_id).collection("accounts").document(account_id)

        account_data = {
            "type": account["type"],
            "subtype": account["subtype"],
            "balance": account.get("balance", 0.0),
            "limit": account.get("limit", 0.0),
            "mask": account["mask"]
        }

        batch.set(account_ref, account_data)
        count += 1

        if count % 100 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Committed {count} accounts...")

    if count % 100 != 0:
        batch.commit()

    print(f"✓ Ingested {count} accounts")


def ingest_transactions(db, transactions):
    """Ingest transactions into Firestore."""
    print(f"\nIngesting {len(transactions)} transactions...")
    batch = db.batch()
    count = 0

    for transaction in transactions:
        user_id = transaction["user_id"]
        transaction_id = transaction["transaction_id"]

        txn_ref = db.collection("users").document(user_id).collection("transactions").document(transaction_id)

        txn_data = {
            "account_id": transaction["account_id"],
            "date": transaction["date"],
            "amount": transaction["amount"],
            "merchant_name": transaction["merchant_name"],
            "category": transaction["category"],
            "pending": transaction.get("pending", False),
            "payment_channel": transaction.get("payment_channel", "other"),
            "iso_currency_code": transaction.get("iso_currency_code", "USD")
        }

        batch.set(txn_ref, txn_data)
        count += 1

        if count % 100 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  Committed {count} transactions...")

    if count % 100 != 0:
        batch.commit()

    print(f"✓ Ingested {count} transactions")


def main():
    """Main ingestion function."""
    print("=" * 60)
    print("Firebase Firestore Data Ingestion")
    print("=" * 60)

    # Initialize Firebase
    db = initialize_firebase()

    # Load data files
    print("\nLoading data files...")
    users = load_json_file("data/users.json")
    accounts = load_json_file("data/accounts.json")
    transactions = load_json_file("data/transactions.json")

    if not users:
        print("ERROR: No users found. Run generate_demo_data.py first.")
        sys.exit(1)

    # Ingest data
    ingest_users(db, users)
    ingest_accounts(db, accounts)
    ingest_transactions(db, transactions)

    print("\n" + "=" * 60)
    print("✓ Data ingestion complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Users: {len(users)}")
    print(f"  Accounts: {len(accounts)}")
    print(f"  Transactions: {len(transactions)}")


if __name__ == "__main__":
    main()
