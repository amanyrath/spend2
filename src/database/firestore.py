"""Firestore database utilities for SpendSense."""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore


def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")

        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # Try to initialize with default credentials (for Cloud Run)
            firebase_admin.initialize_app()

    return firestore.client()


def get_user_transactions(user_id: str, time_window_days: int = 180) -> List[Dict[str, Any]]:
    """Get user transactions from Firestore."""
    db = initialize_firebase()
    transactions_ref = db.collection("users").document(user_id).collection("transactions")

    transactions = []
    for doc in transactions_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(1000).stream():
        txn_data = doc.to_dict()
        txn_data["transaction_id"] = doc.id
        txn_data["user_id"] = user_id
        transactions.append(txn_data)

    return transactions


def get_user_accounts(user_id: str) -> List[Dict[str, Any]]:
    """Get user accounts from Firestore."""
    db = initialize_firebase()
    accounts_ref = db.collection("users").document(user_id).collection("accounts")

    accounts = []
    for doc in accounts_ref.stream():
        account_data = doc.to_dict()
        account_data["account_id"] = doc.id
        account_data["user_id"] = user_id
        accounts.append(account_data)

    return accounts


def store_feature(user_id: str, time_window: str, signal_type: str, signal_data: Dict[str, Any]):
    """Store computed feature in Firestore."""
    db = initialize_firebase()
    features_ref = db.collection("users").document(user_id).collection("computed_features")

    # Create unique ID based on time_window and signal_type
    feature_id = f"{time_window}_{signal_type}"
    feature_ref = features_ref.document(feature_id)

    feature_data = {
        "user_id": user_id,
        "time_window": time_window,
        "signal_type": signal_type,
        "signal_data": signal_data,
        "computed_at": datetime.now().isoformat()
    }

    feature_ref.set(feature_data)


def get_user_features(user_id: str, time_window: str) -> Dict[str, Any]:
    """Get computed features for a user."""
    db = initialize_firebase()
    features_ref = db.collection("users").document(user_id).collection("computed_features")

    features_query = features_ref.where("time_window", "==", time_window)

    features = {}
    for doc in features_query.stream():
        feature_data = doc.to_dict()
        signal_type = feature_data.get("signal_type")
        features[signal_type] = feature_data.get("signal_data", {})

    return features


def store_persona(user_id: str, time_window: str, persona: str, criteria_met: List[str]):
    """Store persona assignment in Firestore."""
    db = initialize_firebase()
    personas_ref = db.collection("users").document(user_id).collection("persona_assignments")

    # Create unique ID based on time_window
    persona_id = f"persona_{time_window}"
    persona_ref = personas_ref.document(persona_id)

    persona_data = {
        "user_id": user_id,
        "time_window": time_window,
        "persona": persona,
        "criteria_met": criteria_met,
        "assigned_at": datetime.now().isoformat()
    }

    persona_ref.set(persona_data)


def get_persona_assignment(user_id: str, time_window: str) -> Optional[Dict[str, Any]]:
    """Get persona assignment for a user."""
    db = initialize_firebase()
    personas_ref = db.collection("users").document(user_id).collection("persona_assignments")

    persona_query = personas_ref.where("time_window", "==", time_window).limit(1)

    for doc in persona_query.stream():
        return doc.to_dict()

    return None


def store_recommendation(user_id: str, recommendation: Dict[str, Any]):
    """Store recommendation in Firestore."""
    db = initialize_firebase()
    recommendations_ref = db.collection("users").document(user_id).collection("recommendations")

    recommendation_id = recommendation.get("recommendation_id")
    rec_ref = recommendations_ref.document(recommendation_id)

    rec_ref.set(recommendation)


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users from Firestore."""
    db = initialize_firebase()
    users_ref = db.collection("users")

    users = []
    for doc in users_ref.stream():
        user_data = doc.to_dict()
        user_data["user_id"] = doc.id
        users.append(user_data)

    return users
