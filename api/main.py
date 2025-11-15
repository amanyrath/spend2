"""
FastAPI server for SpendSense MVP.

Provides endpoints for consumer and operator dashboards with Firebase Firestore backend.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

# Initialize FastAPI app
app = FastAPI(title="SpendSense API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin
def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        # Try to load service account from file
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")

        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # Use default credentials (for Cloud Run / Firebase Functions)
            firebase_admin.initialize_app()

initialize_firebase()
db = firestore.client()


# Pydantic models for request/response
class ChatRequest(BaseModel):
    user_id: str
    message: str
    transaction_window_days: int = 30


class ChatResponse(BaseModel):
    data: Dict[str, Any]
    meta: Dict[str, str]


class ConsentRequest(BaseModel):
    user_id: str
    granted: bool


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


# Consumer endpoints
@app.get("/api/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile with consent status."""
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user_doc.to_dict()

        # Get consent status
        consent_ref = user_ref.collection("consent_records").order_by("granted_at", direction=firestore.Query.DESCENDING).limit(1)
        consent_docs = list(consent_ref.stream())

        consent_granted = False
        consent_timestamp = None

        if consent_docs:
            consent_data = consent_docs[0].to_dict()
            consent_granted = consent_data.get("revoked_at") is None
            consent_timestamp = consent_data.get("granted_at")

        return {
            "user_id": user_id,
            "name": user_data.get("name"),
            "created_at": user_data.get("created_at"),
            "consent_granted": consent_granted,
            "consent_timestamp": consent_timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/accounts")
async def get_user_accounts(user_id: str):
    """Get list of user's accounts."""
    try:
        accounts_ref = db.collection("users").document(user_id).collection("accounts")
        accounts = []

        for doc in accounts_ref.stream():
            account_data = doc.to_dict()
            account_data["account_id"] = doc.id
            accounts.append(account_data)

        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/transactions")
async def get_user_transactions(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """Get user's transaction list with filters."""
    try:
        transactions_ref = db.collection("users").document(user_id).collection("transactions")

        # Build query
        query = transactions_ref.order_by("date", direction=firestore.Query.DESCENDING)

        # Apply filters
        if date_from:
            query = query.where("date", ">=", date_from)
        if date_to:
            query = query.where("date", "<=", date_to)
        if category:
            query = query.where("category", "array_contains", category)

        # Get transactions
        transactions = []
        for doc in query.limit(limit).offset(offset).stream():
            transaction_data = doc.to_dict()
            transaction_data["transaction_id"] = doc.id
            transactions.append(transaction_data)

        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/insights")
async def get_user_insights(user_id: str, time_window: str = "30d"):
    """Get computed insights and charts data."""
    try:
        # Get computed features
        features_ref = db.collection("users").document(user_id).collection("computed_features")
        features_query = features_ref.where("time_window", "==", time_window)

        features = {}
        for doc in features_query.stream():
            feature_data = doc.to_dict()
            signal_type = feature_data.get("signal_type")
            features[signal_type] = feature_data.get("signal_data", {})

        # Get transactions for charts
        transactions_ref = db.collection("users").document(user_id).collection("transactions")
        transactions = []

        for doc in transactions_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(100).stream():
            transactions.append(doc.to_dict())

        return {
            "features": features,
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/recommendations")
async def get_user_recommendations(user_id: str, time_window: str = "30d"):
    """Get education content and partner offers."""
    try:
        recommendations_ref = db.collection("users").document(user_id).collection("recommendations")
        recommendations = []

        for doc in recommendations_ref.order_by("shown_at", direction=firestore.Query.DESCENDING).limit(10).stream():
            rec_data = doc.to_dict()
            rec_data["recommendation_id"] = doc.id
            recommendations.append(rec_data)

        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/consent")
async def update_consent(user_id: str, consent: ConsentRequest):
    """Grant or revoke user consent."""
    try:
        user_ref = db.collection("users").document(user_id)
        consent_ref = user_ref.collection("consent_records").document()

        consent_data = {
            "user_id": user_id,
            "granted_at": firestore.SERVER_TIMESTAMP if consent.granted else None,
            "revoked_at": firestore.SERVER_TIMESTAMP if not consent.granted else None,
            "version": "1.0",
            "ip_address": "unknown"  # Would get from request in production
        }

        consent_ref.set(consent_data)

        return {"success": True, "consent_granted": consent.granted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with AI agent about financial data."""
    try:
        # Get user's transactions
        transactions_ref = db.collection("users").document(request.user_id).collection("transactions")
        transactions = []

        for doc in transactions_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(50).stream():
            transactions.append(doc.to_dict())

        # Get user's features
        features_ref = db.collection("users").document(request.user_id).collection("computed_features")
        features = {}

        for doc in features_ref.stream():
            feature_data = doc.to_dict()
            signal_type = feature_data.get("signal_type")
            features[signal_type] = feature_data.get("signal_data", {})

        # Simple response for now (would integrate with OpenAI in production)
        response_text = f"Based on your recent transactions, I can see you have {len(transactions)} transactions. "

        if "credit_utilization" in features:
            util = features["credit_utilization"].get("total_utilization", 0)
            response_text += f"Your credit utilization is {util:.1f}%. "

        return {
            "data": {
                "response": response_text,
                "citations": []
            },
            "meta": {
                "user_id": request.user_id,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Operator endpoints
@app.get("/api/operator/users")
async def get_all_users():
    """Get list of all users for operator dashboard."""
    try:
        users_ref = db.collection("users")
        users = []

        for user_doc in users_ref.stream():
            user_data = user_doc.to_dict()
            user_id = user_doc.id

            # Get persona assignment
            persona_ref = db.collection("users").document(user_id).collection("persona_assignments")
            persona_query = persona_ref.where("time_window", "==", "30d").limit(1)
            persona_docs = list(persona_query.stream())

            primary_persona = "unknown"
            if persona_docs:
                primary_persona = persona_docs[0].to_dict().get("persona", "unknown")

            users.append({
                "user_id": user_id,
                "name": user_data.get("name"),
                "email": user_data.get("email", ""),
                "persona_30d": primary_persona,
                "created_at": user_data.get("created_at")
            })

        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/operator/users/{user_id}")
async def get_user_detail(user_id: str):
    """Get detailed user information for operator."""
    try:
        # Get user profile
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user_doc.to_dict()

        # Get persona assignments
        personas = {}
        persona_ref = user_ref.collection("persona_assignments")
        for doc in persona_ref.stream():
            persona_data = doc.to_dict()
            time_window = persona_data.get("time_window")
            personas[time_window] = persona_data

        return {
            "user_id": user_id,
            "name": user_data.get("name"),
            "created_at": user_data.get("created_at"),
            "personas": personas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/operator/users/{user_id}/signals")
async def get_user_signals(user_id: str, time_window: str = "30d"):
    """Get user's behavioral signals."""
    try:
        features_ref = db.collection("users").document(user_id).collection("computed_features")
        features_query = features_ref.where("time_window", "==", time_window)

        signals = {}
        for doc in features_query.stream():
            feature_data = doc.to_dict()
            signal_type = feature_data.get("signal_type")
            signals[signal_type] = feature_data.get("signal_data", {})

        return {
            "user_id": user_id,
            "time_window": time_window,
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/operator/users/{user_id}/traces")
async def get_decision_traces(user_id: str):
    """Get decision traces for user's recommendations."""
    try:
        recommendations_ref = db.collection("users").document(user_id).collection("recommendations")
        traces = []

        for doc in recommendations_ref.stream():
            rec_data = doc.to_dict()
            traces.append({
                "recommendation_id": doc.id,
                "type": rec_data.get("type"),
                "title": rec_data.get("title"),
                "shown_at": rec_data.get("shown_at"),
                "decision_trace": rec_data.get("decision_trace", {})
            })

        return {"traces": traces}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
