from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import dashboard, export, predictions, upload
import os
from contextlib import asynccontextmanager

from app.config import DB_PATH

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start fresh on every startup
    if DB_PATH.exists():
        DB_PATH.unlink()
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
app.include_router(export.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "hisaabi backend is running. See /docs for API reference."}


@app.get("/api/uploads")
def list_uploads(user_id: str = None):
    """Convenience endpoint: list all uploads with their status, for debugging/frontend history view."""
    from app.database import get_connection
    with get_connection() as conn:
        if user_id:
            rows = conn.execute(
                "SELECT id, file_name, upload_date, status, error_message, user_id FROM uploads WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, file_name, upload_date, status, error_message, user_id FROM uploads ORDER BY id DESC"
            ).fetchall()
    return [dict(r) for r in rows]


@app.delete("/api/uploads/{upload_id}")
def delete_upload(upload_id: int):
    """Delete an upload and all its associated data (transactions, logs, predictions)"""
    from app.database import get_connection
    from fastapi import HTTPException
    with get_connection() as conn:
        # Delete from child tables first
        conn.execute("DELETE FROM transactions WHERE upload_id = ?", (upload_id,))
        conn.execute("DELETE FROM cleaning_log WHERE upload_id = ?", (upload_id,))
        conn.execute("DELETE FROM predictions_demand WHERE upload_id = ?", (upload_id,))
        conn.execute("DELETE FROM predictions_payment_risk WHERE upload_id = ?", (upload_id,))
        
        # Delete from parent table
        cursor = conn.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Upload not found")
            
    return {"status": "ok", "message": f"Upload {upload_id} deleted successfully."}
