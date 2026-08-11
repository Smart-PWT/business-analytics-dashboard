from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import dashboard, predictions, upload
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start fresh on every startup
    if os.path.exists("app.db"):
        os.remove("app.db")
    init_db()
    yield

app = FastAPI(
    title="hisaabi API",
    description="Small Business Analytics Dashboard — backend (ingestion, cleaning, analysis, predictions).",
    version="1.0.0",
    lifespan=lifespan
)

# CORS: wide open for local dev so the Vite frontend (localhost:5173 by
# default) can call this API without extra config. Tighten this to
# specific origins before any real deployment.
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
    """Convenience endpoint: list all uploads with their status, for debugging/frontend history view."""
    from app.database import get_connection
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, file_name, upload_date, status, error_message FROM uploads ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]
