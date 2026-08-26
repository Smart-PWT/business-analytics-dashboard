import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# load env explicitly
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

if os.environ.get("GROQ_API_KEY"):
    print(f"[main] GROQ_API_KEY loaded ({len(os.environ['GROQ_API_KEY'])} chars) from {_ENV_PATH}")
else:
    print(f"[main] WARNING: GROQ_API_KEY not found. Expected .env at: {_ENV_PATH}")

from app.config import DB_PATH
from app.database import get_connection, init_db
from app.routes import dashboard, predictions, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize the database
    init_db()
    yield


app = FastAPI(
    title="hisaabi API",
    description="Small Business Analytics Dashboard — backend (ingestion, cleaning, analysis, predictions).",
    version="1.0.0",
    lifespan=lifespan,
)

# allow all cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(predictions.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "hisaabi backend is running. See /docs for API reference."}


@app.get("/api/uploads")
def list_uploads():
    """shows past file uploads"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, file_name, upload_date, status, error_message FROM uploads ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]
