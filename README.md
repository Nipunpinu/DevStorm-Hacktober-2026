# YojanaSetu (योजनासेतु) — National Civic Welfare Discovery Portal

YojanaSetu is a modern, transparent civic tech platform that connects Indian citizens with central and state government welfare schemes tailored to their identity, circumstances, and socio-economic background.

This repository features the complete full-stack implementation connecting the existing frontend website (`project/ai_studio_code.html` and `frontend/index.html`) to an enterprise-grade Python FastAPI backend, relational SQL database (SQLAlchemy + SQLite/PostgreSQL), Alembic migrations, official OpenAI SDK integration, deterministic eligibility rules engine, and role-based administrator portal.

---

## Architecture Overview

```
DevStorm-Hacktober-2026/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point, CORS, static routes
│   │   ├── config.py              # Pydantic Settings & environment config
│   │   ├── database.py            # SQLAlchemy engine, sessionmaker, SQLite/PostgreSQL
│   │   ├── models/                # 13 Relational SQL models
│   │   │   ├── scheme.py          # Schemes, translations, benefits, documents, steps
│   │   │   ├── rule.py            # Deterministic eligibility rules
│   │   │   ├── source.py          # Official gazettes & verification history
│   │   │   ├── announcement.py    # Official announcements
│   │   │   ├── user.py            # User profiles & saved tracking (isolated)
│   │   │   └── admin.py           # Admin accounts & audit logging
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── api/                   # REST API Routers
│   │   │   ├── eligibility.py     # POST /api/eligibility/check
│   │   │   ├── schemes.py         # GET /api/schemes, detail, checklist
│   │   │   ├── assistant.py       # POST /api/assistant/chat (Live AI)
│   │   │   ├── languages.py       # 14 Indian languages & translations
│   │   │   ├── sources.py         # Official source tracking
│   │   │   └── admin.py           # Verification queue, audit logs, imports
│   │   ├── services/
│   │   │   ├── eligibility.py     # Deterministic rules evaluation engine
│   │   │   ├── scheme_search.py   # SQL search, filtering, and sorting
│   │   │   ├── llm_service.py     # Official OpenAI SDK integration & report generator
│   │   │   ├── source_service.py  # Source verification, CSV & JSON import
│   │   │   └── translation_service.py # 14 Indian languages + RTL support
│   │   └── security/
│   │       └── auth.py            # Bcrypt hashing, JWT tokens, RBAC
│   ├── migrations/                # Alembic migration versions & environment
│   ├── tests/                     # 16 Pytest tests (unit, mock LLM, integration)
│   ├── scripts/
│   │   ├── seed_data.py           # Idempotent database seed with verified schemes
│   │   └── init_admin.py          # Secure admin initialization
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables template
│   └── .env                       # Local environment file
├── frontend/
│   └── index.html                 # Complete integrated frontend application
├── project/
│   ├── ai_studio_code.html        # Live website connected to backend API
│   └── ai_studio_code.original.backup.html # Preserved original backup
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14.7 macOS/Linux)
- Git

### 2. Setup Virtual Environment & Dependencies

```bash
# Clone the repository
git clone https://github.com/Nipunpinu/DevStorm-Hacktober-2026.git
cd DevStorm-Hacktober-2026

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy placeholder configuration
cp backend/.env.example backend/.env
```

Edit `backend/.env` to configure your settings:
```ini
# Database: SQLite for local dev, PostgreSQL compatible
DATABASE_URL=sqlite:///./yojanasetu.db

# OpenAI API Key (Required for live AI explanations and chat)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# CORS Origin for Frontend
FRONTEND_ORIGIN=http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000

# Security & JWT Secret
JWT_SECRET=super_secret_jwt_key_change_in_production_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

> **Note:** If `OPENAI_API_KEY` is not provided or offline, YojanaSetu **gracefully falls back** to deterministic SQL scheme records and clearly notifies the user, without crashing or returning fake answers.

### 4. Initialize Database & Run Migrations

```bash
# Apply Alembic migrations to create all 13 relational tables
PYTHONPATH=. alembic upgrade head
```

### 5. Seed Real Audited Government Scheme Data

```bash
# Populates the database with real verified central & state schemes
python backend/scripts/seed_data.py
```

### 6. Create Initial Administrator Account

Never use hardcoded passwords! The script allows passing custom credentials or generates a secure random password:

```bash
python backend/scripts/init_admin.py --username admin --email admin@yojanasetu.gov.in --password "YourStrongPassword2026!" --role superadmin
```

### 7. Start the FastAPI Server

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The system will now be live:
- **Web Application:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check & DPDP Notice:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 14 Supported Indian Languages

YojanaSetu natively supports 14 languages across all form fields, results, document checklists, and the AI assistant:
1. **English** (`en`)
2. **हिन्दी** (Hindi, `hi`)
3. **മലയാളം** (Malayalam, `ml`)
4. **తెలుగు** (Telugu, `te`)
5. **मराठी** (Marathi, `mr`)
6. **ਪੰਜਾਬੀ** (Punjabi, `pa`)
7. **বাংলা** (Bengali, `bn`)
8. **ગુજરાતી** (Gujarati, `gu`)
9. **ಕನ್ನಡ** (Kannada, `kn`)
10. **ଓଡ଼ିଆ** (Odia, `or`)
11. **অসমীয়া** (Assamese, `as`)
12. **اردو** (Urdu, `ur`) — *Full Right-to-Left (RTL) support enabled*
13. **کٲشُر** (Kashmiri, `ks`)
14. **संस्कृतम्** (Sanskrit, `sa`)

---

## Key Backend Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/eligibility/check` | Evaluates citizen profile against verified criteria (`potential_match`, `needs_verification`, `does_not_match`) |
| `GET` | `/api/eligibility/options` | Standardized demographic and economic parameters for frontend forms |
| `GET` | `/api/schemes` | Filter schemes by category, status, search query, and benefit value |
| `GET` | `/api/schemes/{slug}` | Detailed scheme view with conditions, benefits, documents, and verified sources |
| `GET` | `/api/schemes/{slug}/checklist` | Mandatory vs. optional top-up document checklist with turnaround and fees |
| `POST` | `/api/assistant/chat` | Live AI assistant grounded in verified SQL scheme records |
| `GET` | `/api/languages` | Supported languages metadata with RTL direction indicators |
| `GET` | `/api/languages/{code}/translations` | Localized translation dictionaries |
| `GET` | `/api/sources/summary` | Real-time verification status across government gazettes |
| `POST` | `/api/admin/login` | Administrator authentication & JWT issue |
| `GET` | `/api/admin/verification-queue` | Stale or unreviewed source verification queue |
| `POST` | `/api/admin/import/json` | Bulk import of new scheme records with duplicate detection |
| `POST` | `/api/admin/import/csv` | CSV upload for scheme records |
| `GET` | `/api/admin/audit-logs` | Tamper-evident administrative action history |

---

## Testing

Run the automated test suite with pytest:

```bash
source .venv/bin/activate
pytest backend/tests/ -v
```

All 16 test suites verify:
- Database schema and relationship integrity
- Deterministic eligibility evaluation (`potential_match`, `does_not_match`, `needs_verification`)
- Missing information handling (does not assume ineligibility)
- OpenAI LLM structured output and graceful offline fallback
- Live assistant grounded in real database records
- 14 language direction and translations
- Admin JWT authentication, RBAC authorization, and audit logs
- CSV & JSON import parsing with duplicate detection

---

## Database Backup & Maintenance

### SQLite Local Backup
To create a timestamped backup of the local database:
```bash
sqlite3 yojanasetu.db ".backup 'backup_yojanasetu_$(date +%Y%m%d_%H%M%S).db'"
```

### PostgreSQL Compatibility
To use PostgreSQL in production, update `DATABASE_URL` in `backend/.env`:
```ini
DATABASE_URL=postgresql://username:password@localhost:5432/yojanasetu
```
Then run `alembic upgrade head`. All SQLAlchemy schemas, column types, and foreign key cascades are 100% PostgreSQL compliant.

---

## Privacy & Statutory Notice (DPDP Compliance)

1. **No Sensitive PII Retained:** YojanaSetu adheres to the Digital Personal Data Protection (DPDP) Act. No Aadhaar numbers, biometric data, or financial bank account credentials are ever collected or stored.
2. **Preliminary Guidance Only:** Match statuses and document readiness calculations are derived strictly from published operational gazettes. Final sanction and fund disbursement remain under the exclusive statutory authority of the designated government departments.
3. **Transparent External Handoff:** Official benefit submission requires authentication on authorized `.gov.in` gateways (such as NSP, PM-KISAN, or Swavlamban). YojanaSetu never charges processing fees or claims to replace official departmental submissions.
