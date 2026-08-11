"""Dashboard analytics API endpoints"""

from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.models.schemas import DashboardResponse, KPISummary, SalesTrendPoint, TopProduct
from app.services import analysis

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


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


@router.get("/{upload_id}", response_model=DashboardResponse)
def get_full_dashboard(
    upload_id: int,
    start_date: str | None = Query(None, description="YYYY-MM-DD, filters sales_trend"),
    end_date: str | None = Query(None, description="YYYY-MM-DD, filters sales_trend"),
):
    """Full dashboard analysis views"""
    _assert_upload_exists(upload_id)
    return analysis.full_dashboard(upload_id, start_date, end_date)


@router.get("/{upload_id}/kpi-summary", response_model=KPISummary)
def get_kpi_summary(upload_id: int):
    """Get KPI summary cards"""
    _assert_upload_exists(upload_id)
    return analysis.kpi_summary(upload_id)


@router.get("/{upload_id}/sales-trend", response_model=list[SalesTrendPoint])
def get_sales_trend(
    upload_id: int,
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
):
    """Get filtered sales trend"""
    _assert_upload_exists(upload_id)
    return analysis.sales_trend(upload_id, start_date, end_date)


@router.get("/{upload_id}/top-products", response_model=list[TopProduct])
def get_top_products(upload_id: int, limit: int = Query(10, ge=1, le=50)):
    """Get top revenue products"""
    _assert_upload_exists(upload_id)
    return analysis.top_products(upload_id, limit)


@router.get("/{upload_id}/profit-loss")
def get_profit_loss(upload_id: int):
    """Get profit loss summary"""
    _assert_upload_exists(upload_id)
    return analysis.profit_loss_summary(upload_id)


@router.get("/{upload_id}/party-dues")
def get_party_dues(upload_id: int):
    """Get party wise dues"""
    _assert_upload_exists(upload_id)
    return analysis.party_wise_dues(upload_id)
