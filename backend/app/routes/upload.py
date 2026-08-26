"""file upload endpoints"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import UPLOADS_DIR
from app.models.schemas import UploadResponse
from app.services.ingestion import IngestionError, ingest_file
from app.services.predictions import run_predictions

router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Please upload a .csv or .xlsx file.",
        )

    temp_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        result = ingest_file(temp_path, original_file_name=file.filename)

        # run predictions silently
        try:
            run_predictions(result["upload_id"])
        except Exception as exc:
            print(f"[upload] prediction run failed for upload {result['upload_id']}: "
                  f"{type(exc).__name__}: {exc}")

        return UploadResponse(**result)

    except IngestionError as exc:
        raise HTTPException(status_code=422, detail=exc.message)
    finally:
        if temp_path.exists():
            temp_path.unlink()