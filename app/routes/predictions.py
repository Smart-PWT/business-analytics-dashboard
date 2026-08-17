"""Machine learning prediction endpoints"""

from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.models.schemas import PredictionsResponse
from app.services import predictions

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


def _assert_upload_exists(upload_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT status FROM uploads WHERE id = ?", (upload_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"No upload found with id {upload_id}.")
    if row["status"] != "cleaned":
        raise HTTPException(
            status_code=409,
            detail=f"Upload {upload_id} is not ready yet (status: {row['status']}).",
        )


@router.post("/{upload_id}/run", response_model=PredictionsResponse)
def run_predictions(upload_id: int):
    """Run and save predictions"""
    _assert_upload_exists(upload_id)
    return predictions.run_predictions(upload_id)


@router.get("/{upload_id}")
def get_predictions(upload_id: int):
    """Fetch most recent predictions"""
    _assert_upload_exists(upload_id)
    return predictions.get_latest_predictions(upload_id)
