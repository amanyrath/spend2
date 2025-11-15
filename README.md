# SpendSense - Financial Education Platform

SpendSense is a web-based financial education platform that analyzes user transaction data to deliver personalized, explainable financial guidance without crossing into regulated financial advice.

## Overview

- **Consumer Dashboard**: 4-tab interface (Transactions, Insights, Education, Offers) with personalized recommendations
- **Backend Engine**: FastAPI server with Firebase Firestore for data storage
- **Behavioral Signals**: Detects subscriptions, credit utilization, savings behavior, and income patterns
- **Persona Assignment**: Categorizes users into 5 personas for targeted education
- **Recommendation Engine**: Generates personalized content with rationales and decision traces

## Demo Users

The project includes 3 pre-configured demo users:

1. **Hannah Martinez** (`user_hannah`)
   - Email: hannah@demo.com
   - Persona: High Utilization (68% credit utilization)
   - Focus: Credit management, debt paydown strategies

2. **Sam Patel** (`user_sam`)
   - Email: sam@demo.com
   - Persona: Subscription-Heavy (8 active subscriptions, $203/month)
   - Focus: Subscription audit, cost optimization

3. **Sarah Chen** (`user_sarah`)
   - Email: sarah@demo.com
   - Persona: Savings Builder (3-6 months emergency fund)
   - Focus: Investment readiness, savings automation

## Project Structure

```
spend2/
├── api/
│   └── main.py                 # FastAPI server with all endpoints
├── consumer_ui/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── contexts/           # React contexts (Auth, Chat)
│   │   └── lib/                # Firebase config, utilities
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── src/
│   ├── database/
│   │   ├── fetch_records.py
│   │   └── firestore.py        # Firestore utilities
│   ├── assignment.py           # Persona assignment logic
│   ├── credit_offers.py        # Partner offers
│   ├── engine.py               # Recommendation engine
│   ├── prompts.py              # Chat prompts
│   └── signal_detection.py     # Behavioral signal detection
├── scripts/
│   ├── generate_demo_data.py   # Generate synthetic data
│   ├── ingest_to_firestore.py  # Load data to Firestore
│   ├── compute_features.py     # Compute features & personas
│   └── build_project.sh        # Master build script
├── docs/
│   ├── spendsense_prd.md       # Product Requirements Document
│   ├── schema.md               # Database schema
│   ├── ux-design-specification.md  # UX design specs
│   └── DATA_METHODOLOGY.md     # Data generation methodology
├── firebase.json               # Firebase configuration
├── firestore.rules             # Firestore security rules
├── firestore.indexes.json      # Firestore indexes
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** (comes with Node.js)
- **Firebase Project** (optional for local development)

## Setup Instructions

### 1. Firebase Setup (Optional for Local Development)

If you want to use Firebase/Firestore:

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save as `firebase-service-account.json` in project root
4. Create a `.env` file from `.env.example` and fill in Firebase credentials

### 2. Quick Start (Automated Build)

```bash
# Make build script executable
chmod +x scripts/build_project.sh

# Run the build script
./scripts/build_project.sh
```

This script will:
- Install Python and Node dependencies
- Generate demo data (3 users, 90 days of transactions)
- Ingest data to Firestore (if configured)
- Compute features and generate recommendations
- Build the frontend

### 3. Manual Setup (Step by Step)

If you prefer to run each step manually:

#### Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd consumer_ui
npm install
cd ..
```

#### Generate Demo Data

```bash
python3 scripts/generate_demo_data.py
```

This creates JSON files in `data/`:
- `users.json` - 3 demo users
- `accounts.json` - Bank accounts (checking, savings, credit cards)
- `transactions.json` - 90 days of transaction history

#### Ingest to Firestore

```bash
python3 scripts/ingest_to_firestore.py
```

#### Compute Features & Generate Recommendations

```bash
python3 scripts/compute_features.py
```

This will:
- Detect behavioral signals (subscriptions, credit utilization, savings)
- Assign personas based on signals
- Generate personalized recommendations

### 4. Run the Application

#### Start the API Server

```bash
python3 api/main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### Start the Frontend (in another terminal)

```bash
cd consumer_ui
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 5. Access the Application

Open `http://localhost:3000` in your browser.

Since Firebase Auth is not configured by default, the app runs in local development mode with mock authentication. You can navigate directly to user dashboards:

- Hannah: `http://localhost:3000/user_hannah/dashboard`
- Sam: `http://localhost:3000/user_sam/dashboard`
- Sarah: `http://localhost:3000/user_sarah/dashboard`

## API Endpoints

### Consumer Endpoints

- `GET /api/users/{user_id}/profile` - Get user profile with consent status
- `GET /api/users/{user_id}/accounts` - Get user's accounts
- `GET /api/users/{user_id}/transactions` - Get transaction list (with filters)
- `GET /api/users/{user_id}/insights` - Get computed insights and charts data
- `GET /api/users/{user_id}/recommendations` - Get education content and offers
- `POST /api/users/{user_id}/consent` - Grant or revoke consent
- `POST /api/chat` - Chat with AI agent about financial data

### Operator Endpoints

- `GET /api/operator/users` - Get all users for operator dashboard
- `GET /api/operator/users/{user_id}` - Get detailed user information
- `GET /api/operator/users/{user_id}/signals` - Get user's behavioral signals
- `GET /api/operator/users/{user_id}/traces` - Get decision traces for recommendations

### Health Check

- `GET /health` - API health check

## Tech Stack

### Frontend
- **React 19** with Vite
- **Tailwind CSS** for styling
- **shadcn/ui** for component library
- **Recharts** for data visualization
- **React Router** for navigation
- **Firebase SDK** for authentication (optional)

### Backend
- **FastAPI** (Python 3.11+)
- **Firebase Admin SDK** for Firestore
- **Pydantic** for data validation
- **Uvicorn** as ASGI server

### Database
- **Firebase Firestore** (or SQLite for local development)
- Row-level security with Firestore rules
- Indexed queries for performance

## Development

### Frontend Development

```bash
cd consumer_ui
npm run dev      # Start dev server
npm run build    # Build for production
npm run lint     # Lint code
```

### Backend Development

```bash
# Run API server with auto-reload
uvicorn api.main:app --reload --port 8000

# Run tests (if available)
pytest
```

### Regenerate Data

To regenerate demo data:

```bash
# Generate new data
python3 scripts/generate_demo_data.py

# Re-ingest to Firestore
python3 scripts/ingest_to_firestore.py

# Recompute features
python3 scripts/compute_features.py
```

## Environment Variables

### Backend (.env)

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
OPENAI_API_KEY=your-openai-api-key  # Optional for chat
API_PORT=8000
```

### Frontend (consumer_ui/.env)

```bash
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_API_URL=http://localhost:8000
```

## Firestore Data Model

```
users/{user_id}
  - name, email, created_at, income

  /accounts/{account_id}
    - type, subtype, balance, limit, mask

  /transactions/{transaction_id}
    - date, amount, merchant_name, category, account_id

  /computed_features/{feature_id}
    - signal_type, signal_data, time_window, computed_at

  /persona_assignments/{assignment_id}
    - persona, criteria_met, time_window, assigned_at

  /recommendations/{recommendation_id}
    - type, content_id, title, rationale, decision_trace, shown_at

  /consent_records/{consent_id}
    - granted_at, revoked_at, version, ip_address
```

## Personas

The system assigns users to one of 5 personas based on behavioral signals:

1. **High Utilization** (Priority 1)
   - Criteria: Credit utilization ≥50% OR interest charges OR minimum payments only
   - Focus: Credit management, debt paydown

2. **Subscription-Heavy** (Priority 2)
   - Criteria: ≥3 recurring merchants AND ≥$50/month OR ≥10% of spending
   - Focus: Subscription audit, cost optimization

3. **Variable Income Budgeter** (Priority 3)
   - Criteria: Irregular income AND cash flow buffer <1 month
   - Focus: Percentage-based budgeting, emergency fund

4. **Savings Builder** (Priority 4)
   - Criteria: Savings growth ≥2% OR net inflow ≥$200/month AND utilization <30%
   - Focus: Investment readiness, savings automation

5. **General Financial Wellness** (Default)
   - Criteria: No specific persona criteria met
   - Focus: General financial education

## Documentation

- [Product Requirements Document](docs/spendsense_prd.md) - Complete PRD
- [Database Schema](docs/schema.md) - Data structures and API formats
- [UX Design Specification](docs/ux-design-specification.md) - Design system and patterns
- [Data Methodology](docs/DATA_METHODOLOGY.md) - Data generation methodology

## Troubleshooting

### Firebase Connection Issues

If you see Firebase connection errors:

1. Verify `firebase-service-account.json` exists and is valid
2. Check that your Firebase project ID matches in the service account file
3. Ensure Firestore is enabled in Firebase Console
4. For local development, you can run without Firebase (app will use mock auth)

### Frontend Build Errors

If you encounter frontend build errors:

```bash
cd consumer_ui
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API Server Errors

If the API server fails to start:

1. Check that port 8000 is not already in use
2. Verify Python dependencies are installed: `pip install -r requirements.txt`
3. Check Firebase service account file exists and is valid

## Contributing

This is an MVP demo project. For production deployment:

1. Set up proper Firebase Authentication
2. Configure environment-specific variables
3. Implement rate limiting and security measures
4. Add comprehensive error handling
5. Set up monitoring and logging
6. Deploy frontend to Vercel/Netlify
7. Deploy API to Railway/Render/Cloud Run

## License

MIT License - see LICENSE file for details

## Contact

For questions or issues, please open an issue in the GitHub repository.

---

**Note**: This is a demo/MVP project for educational purposes. Do not use with real financial data without proper security review and compliance measures.
