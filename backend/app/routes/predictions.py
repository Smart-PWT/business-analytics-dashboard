"""ml prediction endpoints"""

from fastapi import APIRouter

from app.models.schemas import PredictionsResponse
from app.routes.route_checks import assert_upload_ready
from app.services import predictions

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.post("/{upload_id}/run", response_model=PredictionsResponse)
def run_predictions(upload_id: int):
    assert_upload_ready(upload_id)
    return predictions.run_predictions(upload_id)


@router.get("/{upload_id}")
def get_predictions(upload_id: int):
    assert_upload_ready(upload_id)
    return predictions.get_latest_predictions(upload_id)
