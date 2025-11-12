"""Fetch 100 records from Firestore collection.

This script uses Firebase Admin SDK with service account credentials
to fetch records from a specified collection.
"""

import os
import json
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from root .env file
load_dotenv(dotenv_path='.env')

# Try to import firebase-admin
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    HAS_FIREBASE_ADMIN = True
except ImportError:
    HAS_FIREBASE_ADMIN = False
    print("Warning: firebase-admin not installed. Install with: pip install firebase-admin")


def initialize_firebase():
    """Initialize Firebase Admin SDK using service account credentials."""
    if not HAS_FIREBASE_ADMIN:
        raise ImportError("firebase-admin is required. Install with: pip install firebase-admin")
    
    # Check if Firebase app is already initialized
    try:
        app = firebase_admin.get_app()
        return app
    except ValueError:
        # App not initialized, initialize it
        pass
    
    # Get service account key path from environment variable or use default
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH') or 'firebase-service-account.json'
    
    if not os.path.exists(service_account_path):
        raise FileNotFoundError(
            f"Service account key file not found: {service_account_path}\n"
            f"Please set FIREBASE_SERVICE_ACCOUNT_PATH environment variable or place the file at {service_account_path}"
        )
    
    # Initialize Firebase with service account credentials
    cred = credentials.Certificate(service_account_path)
    app = firebase_admin.initialize_app(cred)
    
    return app


def fetch_100_records(collection_name: str) -> List[Dict[str, Any]]:
    """Fetch 100 records from a Firestore collection.
    
    Args:
        collection_name: Name of the Firestore collection to query
        
    Returns:
        List of dictionaries, each containing document id and data
    """
    if not HAS_FIREBASE_ADMIN:
        raise ImportError("firebase-admin is required")
    
    # Initialize Firebase
    initialize_firebase()
    
    # Get Firestore client
    db = firestore.client()
    
    # Query collection with limit of 100
    collection_ref = db.collection(collection_name)
    docs = collection_ref.limit(100).stream()
    
    records = []
    for doc in docs:
        record = {
            'id': doc.id,
            **doc.to_dict()
        }
        records.append(record)
    
    print(f"Fetched {len(records)} records from collection: {collection_name}")
    return records


def main():
    """Main function to run as a script."""
    if len(sys.argv) < 2:
        collection_name = 'users'  # Default collection
        print(f"No collection name provided, using default: {collection_name}")
    else:
        collection_name = sys.argv[1]
    
    try:
        records = fetch_100_records(collection_name)
        
        # Print results as JSON
        print("\nRecords:")
        print(json.dumps(records, indent=2, default=str))
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())