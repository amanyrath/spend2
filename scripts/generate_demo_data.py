"""
Generate synthetic data for 3 demo users as specified in PRD.

Users:
1. Hannah Martinez - High Utilization persona
2. Sam Patel - Subscription-Heavy persona
3. Sarah Chen - Savings Builder persona
"""

import json
import uuid
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Set seed for reproducibility
random.seed(42)


def generate_user_id(name: str) -> str:
    """Generate user ID from name."""
    first_name = name.split()[0].lower()
    return f"user_{first_name}"


def generate_account_id(user_id: str, account_type: str, index: int = 0) -> str:
    """Generate account ID."""
    return f"{user_id}_{account_type}_{index}"


def generate_transaction_id() -> str:
    """Generate unique transaction ID."""
    return f"txn_{uuid.uuid4().hex[:12]}"


def generate_transactions_for_user(
    user_id: str,
    accounts: List[Dict],
    num_days: int = 90,
    persona: str = "general"
) -> List[Dict]:
    """Generate transactions for a user based on their persona."""
    transactions = []
    start_date = datetime.now() - timedelta(days=num_days)

    # Define subscription merchants based on persona
    subscriptions = []
    if persona == "high_utilization":
        subscriptions = [
            ("Netflix", 15.99),
            ("Spotify", 10.99),
            ("Planet Fitness", 24.99),
            ("Adobe Creative Cloud", 52.99)
        ]
    elif persona == "subscription_heavy":
        subscriptions = [
            ("Netflix", 15.99),
            ("Hulu", 14.99),
            ("Disney+", 13.99),
            ("Spotify", 10.99),
            ("Apple iCloud", 9.99),
            ("NYT Digital", 25.00),
            ("Peloton", 44.00),
            ("HelloFresh", 71.99)
        ]
    elif persona == "savings_builder":
        subscriptions = [
            ("Netflix", 15.99),
            ("Spotify", 10.99)
        ]

    # Get accounts
    checking = next((a for a in accounts if a["subtype"] == "checking"), None)
    savings = next((a for a in accounts if a["subtype"] == "savings"), None)
    credit_cards = [a for a in accounts if a["type"] == "credit"]

    # Generate daily transactions
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")

        # Payroll deposits (biweekly)
        if day % 14 == 0 and checking:
            if persona == "high_utilization":
                amount = 1750.00
            elif persona == "subscription_heavy":
                amount = 2370.00
            else:  # savings_builder
                amount = 2000.00

            transactions.append({
                "transaction_id": generate_transaction_id(),
                "account_id": checking["account_id"],
                "user_id": user_id,
                "date": date_str,
                "amount": amount,
                "merchant_name": "PAYROLL DEPOSIT",
                "category": ["Income", "Payroll"],
                "pending": False,
                "payment_channel": "other"
            })

        # Monthly subscriptions (on specific days)
        if day % 30 == 5:  # 5th of each month
            for merchant, sub_amount in subscriptions:
                account = credit_cards[0] if credit_cards else checking
                if account:
                    transactions.append({
                        "transaction_id": generate_transaction_id(),
                        "account_id": account["account_id"],
                        "user_id": user_id,
                        "date": date_str,
                        "amount": -sub_amount,
                        "merchant_name": merchant,
                        "category": ["Service", "Subscription"],
                        "pending": False,
                        "payment_channel": "online"
                    })

        # Rent/mortgage payment (1st of month)
        if day % 30 == 0 and checking:
            if persona == "high_utilization":
                amount = -1200.00
            elif persona == "subscription_heavy":
                amount = -1600.00
            else:
                amount = -1400.00

            transactions.append({
                "transaction_id": generate_transaction_id(),
                "account_id": checking["account_id"],
                "user_id": user_id,
                "date": date_str,
                "amount": amount,
                "merchant_name": "RENT PAYMENT",
                "category": ["Home", "Rent"],
                "pending": False,
                "payment_channel": "other"
            })

        # Credit card payments
        if day % 30 == 15 and credit_cards:
            for i, card in enumerate(credit_cards):
                if persona == "high_utilization":
                    # Minimum payment only
                    payment = -50.00 if i == 0 else 0
                elif persona == "savings_builder":
                    # Pay in full
                    payment = -card.get("balance", 0) * 0.1
                else:
                    # Partial payment
                    payment = -200.00 if i == 0 else 0

                if payment != 0 and checking:
                    transactions.append({
                        "transaction_id": generate_transaction_id(),
                        "account_id": checking["account_id"],
                        "user_id": user_id,
                        "date": date_str,
                        "amount": payment,
                        "merchant_name": f"Credit Card Payment - {card['mask']}",
                        "category": ["Payment", "Credit Card"],
                        "pending": False,
                        "payment_channel": "other"
                    })

        # Savings transfers
        if persona == "savings_builder" and day % 15 == 7 and checking and savings:
            transactions.append({
                "transaction_id": generate_transaction_id(),
                "account_id": checking["account_id"],
                "user_id": user_id,
                "date": date_str,
                "amount": -250.00,
                "merchant_name": "Transfer to Savings",
                "category": ["Transfer", "Internal"],
                "pending": False,
                "payment_channel": "other"
            })

            transactions.append({
                "transaction_id": generate_transaction_id(),
                "account_id": savings["account_id"],
                "user_id": user_id,
                "date": date_str,
                "amount": 250.00,
                "merchant_name": "Transfer from Checking",
                "category": ["Transfer", "Internal"],
                "pending": False,
                "payment_channel": "other"
            })

        # Random daily transactions
        num_transactions = random.randint(1, 4)
        for _ in range(num_transactions):
            # Choose account (mostly credit cards for purchases)
            if credit_cards and random.random() < 0.7:
                account = random.choice(credit_cards)
            else:
                account = checking

            if not account:
                continue

            # Random category
            categories = [
                (["Food and Drink", "Groceries"], "Whole Foods", -45.00, -120.00),
                (["Food and Drink", "Restaurants"], "Restaurant", -15.00, -65.00),
                (["Transportation", "Gas"], "Gas Station", -35.00, -70.00),
                (["Shopping", "General"], "Target", -25.00, -100.00),
                (["Shopping", "Clothing"], "Clothing Store", -40.00, -150.00),
            ]

            category, merchant_prefix, min_amt, max_amt = random.choice(categories)
            amount = random.uniform(min_amt, max_amt)
            merchant = f"{merchant_prefix} #{random.randint(100, 999)}"

            transactions.append({
                "transaction_id": generate_transaction_id(),
                "account_id": account["account_id"],
                "user_id": user_id,
                "date": date_str,
                "amount": amount,
                "merchant_name": merchant,
                "category": category,
                "pending": False,
                "payment_channel": "in store" if "Gas" not in merchant else "online"
            })

    return transactions


def generate_demo_users() -> Dict[str, Any]:
    """Generate all demo users with their data."""
    users = []
    all_accounts = []
    all_transactions = []

    # User 1: Hannah Martinez - High Utilization
    hannah_id = generate_user_id("Hannah Martinez")
    users.append({
        "user_id": hannah_id,
        "name": "Hannah Martinez",
        "email": "hannah@demo.com",
        "created_at": datetime.now().isoformat(),
        "income": 48000
    })

    hannah_accounts = [
        {
            "account_id": generate_account_id(hannah_id, "checking"),
            "user_id": hannah_id,
            "type": "depository",
            "subtype": "checking",
            "balance": 850.00,
            "mask": "1234"
        },
        {
            "account_id": generate_account_id(hannah_id, "savings"),
            "user_id": hannah_id,
            "type": "depository",
            "subtype": "savings",
            "balance": 1200.00,
            "mask": "5678"
        },
        {
            "account_id": generate_account_id(hannah_id, "credit", 0),
            "user_id": hannah_id,
            "type": "credit",
            "subtype": "credit card",
            "balance": 3400.00,
            "limit": 5000.00,
            "mask": "4523"
        }
    ]

    all_accounts.extend(hannah_accounts)
    all_transactions.extend(generate_transactions_for_user(
        hannah_id, hannah_accounts, persona="high_utilization"
    ))

    # User 2: Sam Patel - Subscription-Heavy
    sam_id = generate_user_id("Sam Patel")
    users.append({
        "user_id": sam_id,
        "name": "Sam Patel",
        "email": "sam@demo.com",
        "created_at": datetime.now().isoformat(),
        "income": 65000
    })

    sam_accounts = [
        {
            "account_id": generate_account_id(sam_id, "checking"),
            "user_id": sam_id,
            "type": "depository",
            "subtype": "checking",
            "balance": 2400.00,
            "mask": "2345"
        },
        {
            "account_id": generate_account_id(sam_id, "savings"),
            "user_id": sam_id,
            "type": "depository",
            "subtype": "savings",
            "balance": 5000.00,
            "mask": "6789"
        },
        {
            "account_id": generate_account_id(sam_id, "credit", 0),
            "user_id": sam_id,
            "type": "credit",
            "subtype": "credit card",
            "balance": 800.00,
            "limit": 8000.00,
            "mask": "7890"
        }
    ]

    all_accounts.extend(sam_accounts)
    all_transactions.extend(generate_transactions_for_user(
        sam_id, sam_accounts, persona="subscription_heavy"
    ))

    # User 3: Sarah Chen - Savings Builder
    sarah_id = generate_user_id("Sarah Chen")
    users.append({
        "user_id": sarah_id,
        "name": "Sarah Chen",
        "email": "sarah@demo.com",
        "created_at": datetime.now().isoformat(),
        "income": 55000
    })

    sarah_accounts = [
        {
            "account_id": generate_account_id(sarah_id, "checking"),
            "user_id": sarah_id,
            "type": "depository",
            "subtype": "checking",
            "balance": 3200.00,
            "mask": "3456"
        },
        {
            "account_id": generate_account_id(sarah_id, "savings"),
            "user_id": sarah_id,
            "type": "depository",
            "subtype": "savings",
            "balance": 8500.00,
            "mask": "7891"
        },
        {
            "account_id": generate_account_id(sarah_id, "credit", 0),
            "user_id": sarah_id,
            "type": "credit",
            "subtype": "credit card",
            "balance": 400.00,
            "limit": 3000.00,
            "mask": "8901"
        }
    ]

    all_accounts.extend(sarah_accounts)
    all_transactions.extend(generate_transactions_for_user(
        sarah_id, sarah_accounts, persona="savings_builder"
    ))

    return {
        "users": users,
        "accounts": all_accounts,
        "transactions": all_transactions
    }


def main():
    """Generate and save demo data."""
    print("Generating demo data for 3 users...")
    data = generate_demo_users()

    # Save to JSON files
    with open("data/users.json", "w") as f:
        json.dump(data["users"], f, indent=2)
    print(f"Generated {len(data['users'])} users")

    with open("data/accounts.json", "w") as f:
        json.dump(data["accounts"], f, indent=2)
    print(f"Generated {len(data['accounts'])} accounts")

    with open("data/transactions.json", "w") as f:
        json.dump(data["transactions"], f, indent=2)
    print(f"Generated {len(data['transactions'])} transactions")

    print("\nDemo data generation complete!")
    print("\nUsers created:")
    for user in data["users"]:
        print(f"  - {user['name']} ({user['user_id']}): {user['email']}")


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    main()
