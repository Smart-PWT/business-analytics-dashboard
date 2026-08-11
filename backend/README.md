# hisaabi — Backend

Data ingestion, cleaning, analysis, and ML predictions for the Small Business
Analytics Dashboard (see SRS). This service owns everything in **SRS Section
4 (except auth/upload UI) and Section 5** — CSV/Excel in, clean structured
JSON out.

**Current scope (v1, per team split):**
- ✅ CSV/Excel upload + column mapping + validation + cleaning (FR2, FR3)
- ✅ Dashboard analysis: KPI cards, sales trend, top products, profit/loss, party dues (FR4)
- ✅ Predictions: demand forecast, payment risk (FR5)
- ⏳ Deferred to v2: Supabase (using local SQLite instead), Render deployment, Groq LLM column-mapping assist (rule-based mapper is the permanent fallback and works standalone for now)

---

## 1. Setup & Running Locally

```bash
cd hisaabi-backend
pip install -r requirements.txt --break-system-packages   # or use a venv
uvicorn main:app --reload --port 8000
```

Then open **http://127.0.0.1:8000/docs** — this is the live, interactive API
contract. Your frontend teammate can try every endpoint from the browser and
see exact request/response shapes without asking you.

The SQLite database file is created automatically at
`data/db/hisaabi.db` on first run. Delete it any time to reset all data.

---

## 2. How the Pipeline Works

```
Upload CSV/Excel
      │
      ▼
column_mapper.py   → matches messy headers ("Qty", "Rate") to schema names
      │
      ▼
validator.py       → rejects upload if required columns are missing (FR2.3)
      │
      ▼
cleaner.py          → dedupe, standardize dates/currency, handle missing values (FR3)
      │
      ▼
SQLite (transactions table)
      │
      ├──► analysis.py    → FR4 dashboard views (on-demand, read-only queries)
      └──► predictions.py → FR5 ML models (run once per upload, results cached)
```

Predictions run automatically right after a successful upload (mirrors the
SRS data-flow diagram in Section 3). If you want to force a re-run later
(e.g. after tuning a model), call `POST /api/predictions/{upload_id}/run`.

---

## 3. API Endpoints (Frontend Contract)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/upload` | Upload CSV/Excel file (multipart form, field name `file`) |
| GET | `/api/uploads` | List all uploads + status (debugging/history) |
| GET | `/api/dashboard/{upload_id}` | All 5 analysis views in one response |
| GET | `/api/dashboard/{upload_id}/kpi-summary` | FR4.5 |
| GET | `/api/dashboard/{upload_id}/sales-trend?start_date=&end_date=` | FR4.1 |
| GET | `/api/dashboard/{upload_id}/top-products?limit=10` | FR4.2 |
| GET | `/api/dashboard/{upload_id}/profit-loss` | FR4.3 |
| GET | `/api/dashboard/{upload_id}/party-dues` | FR4.4 |
| GET | `/api/predictions/{upload_id}` | Fetch cached predictions |
| POST | `/api/predictions/{upload_id}/run` | Force re-run predictions |

All responses are JSON. Errors return a `detail` field with a specific,
human-readable message (never a silent failure — FR2.3).

**Frontend integration note:** CORS is wide open (`allow_origins=["*"]`) for
local dev, so your Vite dev server can call this directly at
`http://127.0.0.1:8000` with no proxy config needed. Tighten this before any
real deployment.

---

## 4. Project Structure

```
hisaabi-backend/
├── main.py                    # FastAPI app entrypoint
├── requirements.txt
├── app/
│   ├── config.py               # schema definitions, constants — single source of truth
│   ├── database.py              # SQLite layer (stand-in for Supabase/Postgres)
│   ├── routes/
│   │   ├── upload.py            # POST /api/upload
│   │   ├── dashboard.py         # GET /api/dashboard/*
│   │   └── predictions.py       # GET/POST /api/predictions/*
│   ├── services/
│   │   ├── column_mapper.py     # rule-based header matching (LLM fallback target)
│   │   ├── validator.py         # required-column enforcement
│   │   ├── cleaner.py           # FR3.1-FR3.5 cleaning pipeline
│   │   ├── ingestion.py         # orchestrates mapper -> validator -> cleaner -> DB
│   │   ├── analysis.py          # FR4.1-FR4.5 dashboard queries
│   │   └── predictions.py       # runs ML models, persists results
│   ├── ml/
│   │   ├── demand_forecast.py   # FR5.1 — moving average
│   │   └── payment_risk.py      # FR5.2 — Logistic Regression + rule-based fallback
│   └── models/
│       └── schemas.py           # Pydantic response models (drives /docs)
└── data/
    ├── uploads/                 # temp storage during ingestion (auto-cleaned)
    └── db/hisaabi.db            # SQLite database (auto-created)
```

---

## 5. Known Limitations / Things to Flag to the Team Lead

1. **Profit/Loss has no true cost basis.** The SRS schema (Section 6/7) has
   no `cost_price` column — only `unit_price`/`total_amount`. Current logic
   treats `Sale` transactions as revenue and `Purchase` transactions as cost
   to approximate P/L. If the real Vyapar export (Week 1 blocking task)
   includes a cost/purchase price column, `analysis.py::profit_loss_summary`
   should be updated to use it directly — flagged in that function's
   docstring too.

2. **Payment risk labels are trained per-upload**, not on a shared
   population — there's no historical "did they actually default" ground
   truth in this schema, so the model bootstraps its own training labels
   from a rule-based heuristic, then tries to fit a real Logistic Regression
   on top of them where there's enough data diversity. This is documented
   in `app/ml/payment_risk.py` — worth a quick read before the ML sync.

3. **No auth/multi-tenancy yet.** Every upload is globally visible (no
   `user_id` scoping) since Supabase is deferred. Fine for local dev with
   your frontend teammate; must be revisited before deployment.

---

## 6. Testing It Yourself

A quick way to sanity-check the whole pipeline without a real Vyapar file:
generate a synthetic CSV with messy headers (`Date`, `Party`, `Item`, `Qty`,
`Rate`, `Amount`, `Paid`, `Type`) and currency-formatted values (`"Rs.
1,500"`), then `POST` it to `/api/upload` — the response will show exactly
how many rows were ingested vs flagged, and the column mapping that was
inferred.
