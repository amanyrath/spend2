"""
Compute features and assign personas for all users in Firestore.

This script:
1. Gets all users from Firestore
2. Computes behavioral signals for each user
3. Assigns personas based on signals
4. Generates recommendations
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.firestore import (
    initialize_firebase,
    get_all_users,
    get_user_transactions,
    get_user_accounts,
    store_feature,
    store_persona,
    store_recommendation
)


def compute_subscription_signals(transactions, time_window_days=180):
    """Detect recurring subscription merchants."""
    from collections import defaultdict

    # Group transactions by merchant
    merchant_transactions = defaultdict(list)
    for txn in transactions:
        if txn["amount"] < 0:  # Only debits
            merchant = txn["merchant_name"]
            merchant_transactions[merchant].append(txn)

    # Find recurring merchants
    recurring_merchants = []
    for merchant, txns in merchant_transactions.items():
        if len(txns) >= 3:
            # Check if amounts are consistent
            amounts = [abs(t["amount"]) for t in txns]
            avg_amount = sum(amounts) / len(amounts)

            if all(abs(amt - avg_amount) < 5.0 for amt in amounts):  # Within $5
                recurring_merchants.append({
                    "merchant": merchant,
                    "amount": avg_amount,
                    "frequency": "monthly",
                    "count": len(txns)
                })

    monthly_recurring = sum(m["amount"] for m in recurring_merchants)
    total_spend = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    subscription_share = monthly_recurring / total_spend if total_spend > 0 else 0

    return {
        "recurring_merchants": recurring_merchants,
        "monthly_recurring": monthly_recurring,
        "subscription_share": subscription_share
    }


def compute_credit_signals(accounts):
    """Compute credit utilization signals."""
    credit_accounts = [a for a in accounts if a["type"] == "credit"]

    if not credit_accounts:
        return {}

    total_balance = sum(a.get("balance", 0) for a in credit_accounts)
    total_limit = sum(a.get("limit", 0) for a in credit_accounts)

    total_utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0

    accounts_detail = []
    for account in credit_accounts:
        balance = account.get("balance", 0)
        limit = account.get("limit", 0)
        utilization = (balance / limit * 100) if limit > 0 else 0

        accounts_detail.append({
            "account_id": account["account_id"],
            "utilization": utilization,
            "balance": balance,
            "limit": limit,
            "mask": account.get("mask", "")
        })

    return {
        "total_utilization": total_utilization,
        "accounts": accounts_detail,
        "interest_charged": 0,  # Would need transaction analysis
        "minimum_payment_only": total_utilization > 60,  # Simplified
        "is_overdue": False
    }


def compute_savings_signals(accounts, transactions):
    """Compute savings behavior signals."""
    savings_accounts = [a for a in accounts if a.get("subtype") == "savings"]

    if not savings_accounts:
        return {}

    total_savings = sum(a.get("balance", 0) for a in savings_accounts)

    # Calculate net inflow to savings
    savings_txns = [t for t in transactions if any(
        t.get("account_id") == a["account_id"] for a in savings_accounts
    )]

    deposits = sum(t["amount"] for t in savings_txns if t["amount"] > 0)
    withdrawals = sum(abs(t["amount"]) for t in savings_txns if t["amount"] < 0)
    net_inflow = deposits - withdrawals

    # Estimate monthly expenses
    checking_txns = [t for t in transactions if t.get("subtype") != "savings" and t["amount"] < 0]
    total_expenses = sum(abs(t["amount"]) for t in checking_txns)
    avg_monthly_expenses = total_expenses / 3  # Assuming 90 days

    emergency_fund_coverage = total_savings / avg_monthly_expenses if avg_monthly_expenses > 0 else 0

    return {
        "total_savings": total_savings,
        "net_inflow": net_inflow,
        "growth_rate": 0.05,  # Simplified
        "emergency_fund_coverage": emergency_fund_coverage,
        "coverage_level": "good" if emergency_fund_coverage >= 3 else "building"
    }


def compute_income_signals(transactions):
    """Compute income stability signals."""
    # Find payroll deposits
    payroll_txns = [t for t in transactions if t["amount"] > 0 and "PAYROLL" in t.get("merchant_name", "").upper()]

    if not payroll_txns:
        return {}

    amounts = [t["amount"] for t in payroll_txns]
    avg_paycheck = sum(amounts) / len(amounts) if amounts else 0

    return {
        "frequency": "biweekly",
        "avg_paycheck": avg_paycheck,
        "irregular_frequency": False,
        "cash_flow_buffer": 1.5
    }


def assign_persona(features):
    """Assign persona based on computed features."""
    credit_signals = features.get("credit_utilization", {})
    subscription_signals = features.get("subscriptions", {})
    savings_signals = features.get("savings_behavior", {})

    # Priority 1: High Utilization
    utilization = credit_signals.get("total_utilization", 0)
    if utilization >= 50:
        return "high_utilization", [f"credit_utilization >= 50% ({utilization:.1f}%)"]

    # Priority 2: Subscription-Heavy
    recurring_count = len(subscription_signals.get("recurring_merchants", []))
    monthly_recurring = subscription_signals.get("monthly_recurring", 0)
    if recurring_count >= 3 and monthly_recurring >= 50:
        return "subscription_heavy", [f"recurring_merchants >= 3 ({recurring_count})", f"monthly_recurring >= $50 (${monthly_recurring:.2f})"]

    # Priority 3: Savings Builder
    coverage = savings_signals.get("emergency_fund_coverage", 0)
    if coverage >= 3 and utilization < 30:
        return "savings_builder", [f"emergency_fund_coverage >= 3 months ({coverage:.1f})", f"credit_utilization < 30% ({utilization:.1f}%)"]

    # Default
    return "general_wellness", ["No specific persona criteria met"]


def generate_simple_recommendations(user_id, persona, features):
    """Generate simple recommendations based on persona."""
    recommendations = []

    if persona == "high_utilization":
        credit_signals = features.get("credit_utilization", {})
        utilization = credit_signals.get("total_utilization", 0)
        accounts = credit_signals.get("accounts", [])

        card_detail = ""
        if accounts:
            first_card = accounts[0]
            card_detail = f"your card ending in {first_card['mask']} is at {first_card['utilization']:.1f}% utilization"

        recommendations.append({
            "recommendation_id": f"rec_{user_id}_credit_util",
            "user_id": user_id,
            "type": "education",
            "content_id": "edu_credit_util_101",
            "title": "Understanding Credit Utilization",
            "rationale": f"We're showing you this because {card_detail}. Bringing this below 30% could improve your credit score.",
            "decision_trace": {
                "persona_match": persona,
                "signals_used": [{"signal": "credit_utilization", "value": utilization}],
                "timestamp": datetime.now().isoformat()
            },
            "shown_at": datetime.now().isoformat()
        })

    elif persona == "subscription_heavy":
        subscription_signals = features.get("subscriptions", {})
        recurring_merchants = subscription_signals.get("recurring_merchants", [])
        monthly_total = subscription_signals.get("monthly_recurring", 0)

        recommendations.append({
            "recommendation_id": f"rec_{user_id}_subscriptions",
            "user_id": user_id,
            "type": "education",
            "content_id": "edu_subscription_audit",
            "title": "The $200 Question: Are You Using All Your Subscriptions?",
            "rationale": f"We're showing you this because you have {len(recurring_merchants)} active subscriptions totaling ${monthly_total:.2f}/month. A quick audit could save you money.",
            "decision_trace": {
                "persona_match": persona,
                "signals_used": [{"signal": "subscription_count", "value": len(recurring_merchants)}],
                "timestamp": datetime.now().isoformat()
            },
            "shown_at": datetime.now().isoformat()
        })

    elif persona == "savings_builder":
        savings_signals = features.get("savings_behavior", {})
        coverage = savings_signals.get("emergency_fund_coverage", 0)

        recommendations.append({
            "recommendation_id": f"rec_{user_id}_savings",
            "user_id": user_id,
            "type": "education",
            "content_id": "edu_investment_ready",
            "title": "From Savings to Investing: When Are You Ready?",
            "rationale": f"We're showing you this because you have {coverage:.1f} months of expenses saved. You might be ready to explore investment options.",
            "decision_trace": {
                "persona_match": persona,
                "signals_used": [{"signal": "emergency_fund_coverage", "value": coverage}],
                "timestamp": datetime.now().isoformat()
            },
            "shown_at": datetime.now().isoformat()
        })

    return recommendations


def process_user(user_id, user_name):
    """Process a single user: compute features, assign persona, generate recommendations."""
    print(f"\nProcessing user: {user_name} ({user_id})")

    # Get user data
    transactions = get_user_transactions(user_id)
    accounts = get_user_accounts(user_id)

    print(f"  Found {len(transactions)} transactions, {len(accounts)} accounts")

    # Compute features
    time_window = "30d"

    # Subscription signals
    subscription_signals = compute_subscription_signals(transactions)
    store_feature(user_id, time_window, "subscriptions", subscription_signals)
    print(f"  ✓ Computed subscription signals: {len(subscription_signals.get('recurring_merchants', []))} recurring merchants")

    # Credit signals
    credit_signals = compute_credit_signals(accounts)
    if credit_signals:
        store_feature(user_id, time_window, "credit_utilization", credit_signals)
        print(f"  ✓ Computed credit signals: {credit_signals.get('total_utilization', 0):.1f}% utilization")

    # Savings signals
    savings_signals = compute_savings_signals(accounts, transactions)
    if savings_signals:
        store_feature(user_id, time_window, "savings_behavior", savings_signals)
        print(f"  ✓ Computed savings signals: ${savings_signals.get('total_savings', 0):.2f}")

    # Income signals
    income_signals = compute_income_signals(transactions)
    if income_signals:
        store_feature(user_id, time_window, "income_stability", income_signals)
        print(f"  ✓ Computed income signals")

    # Assign persona
    features = {
        "subscriptions": subscription_signals,
        "credit_utilization": credit_signals,
        "savings_behavior": savings_signals,
        "income_stability": income_signals
    }

    persona, criteria = assign_persona(features)
    store_persona(user_id, time_window, persona, criteria)
    print(f"  ✓ Assigned persona: {persona}")

    # Generate recommendations
    recommendations = generate_simple_recommendations(user_id, persona, features)
    for rec in recommendations:
        store_recommendation(user_id, rec)
    print(f"  ✓ Generated {len(recommendations)} recommendations")


def main():
    """Main function to process all users."""
    print("=" * 60)
    print("SpendSense Feature Computation & Recommendation Generation")
    print("=" * 60)

    # Initialize Firebase
    initialize_firebase()

    # Get all users
    users = get_all_users()
    print(f"\nFound {len(users)} users in Firestore")

    # Process each user
    for user in users:
        user_id = user["user_id"]
        user_name = user.get("name", "Unknown")
        process_user(user_id, user_name)

    print("\n" + "=" * 60)
    print("✓ Processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
