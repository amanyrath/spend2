#!/bin/bash

# SpendSense Project Build Script
# This script builds the entire SpendSense project from scratch

set -e  # Exit on error

echo "======================================"
echo "SpendSense Project Build Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Check if Firebase service account exists
if [ ! -f "firebase-service-account.json" ]; then
    print_error "Firebase service account not found!"
    echo ""
    echo "Please create firebase-service-account.json with your Firebase credentials:"
    echo "  1. Go to Firebase Console > Project Settings > Service Accounts"
    echo "  2. Click 'Generate New Private Key'"
    echo "  3. Save as firebase-service-account.json in project root"
    echo ""
    echo "For local development without Firebase, you can skip this and use SQLite mode."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Install Python dependencies
echo ""
echo "Step 1: Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m pip install -r requirements.txt --quiet
    print_status "Python dependencies installed"
else
    print_error "Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

# Step 2: Install Node dependencies for frontend
echo ""
echo "Step 2: Installing frontend dependencies..."
cd consumer_ui
if command -v npm &> /dev/null; then
    npm install --silent
    print_status "Frontend dependencies installed"
else
    print_error "npm not found. Please install Node.js 18 or higher."
    exit 1
fi
cd ..

# Step 3: Generate demo data
echo ""
echo "Step 3: Generating demo data..."
mkdir -p data
python3 scripts/generate_demo_data.py
print_status "Demo data generated (3 users)"

# Step 4: Ingest data to Firestore (if Firebase is configured)
if [ -f "firebase-service-account.json" ]; then
    echo ""
    echo "Step 4: Ingesting data to Firestore..."
    python3 scripts/ingest_to_firestore.py
    print_status "Data ingested to Firestore"

    # Step 5: Compute features and generate recommendations
    echo ""
    echo "Step 5: Computing features and generating recommendations..."
    python3 scripts/compute_features.py
    print_status "Features computed and recommendations generated"
else
    print_warning "Skipping Firestore ingestion (no service account)"
    print_warning "Skipping feature computation (no service account)"
fi

# Step 6: Build frontend
echo ""
echo "Step 6: Building frontend..."
cd consumer_ui
npm run build
print_status "Frontend built successfully"
cd ..

echo ""
echo "======================================"
print_status "Build complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Start the API server:"
echo "     $ python3 api/main.py"
echo ""
echo "  2. Start the frontend dev server (in another terminal):"
echo "     $ cd consumer_ui && npm run dev"
echo ""
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "Demo accounts:"
echo "  - Hannah Martinez: hannah@demo.com"
echo "  - Sam Patel: sam@demo.com"
echo "  - Sarah Chen: sarah@demo.com"
echo ""
