"""File upload API endpoints"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import UPLOADS_DIR
from app.models.schemas import UploadResponse
from app.services.ingestion import IngestionError, ingest_file
from app.services.predictions import run_predictions

router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".csv"}


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Process uploaded CSV file"""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Please upload a .csv file.",
        )

    # Save to unique path
    temp_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = ingest_file(temp_path, original_file_name=file.filename)

        # Run predictions after cleaning
        try:
            run_predictions(result["upload_id"])
        except Exception:
            # Ignore prediction failures here
            pass

        return UploadResponse(**result)

    except IngestionError as exc:
        raise HTTPException(status_code=422, detail=exc.message)
    finally:
        # Delete raw upload file
        if temp_path.exists():
            temp_path.unlink()
