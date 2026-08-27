"""dashboard api endpoints"""

import csv
import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.database import get_connection
from app.models.schemas import DashboardResponse, KPISummary, SalesTrendPoint, TopProduct
from app.routes.route_checks import assert_upload_ready
from app.services import analysis

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{upload_id}", response_model=DashboardResponse)
def get_full_dashboard(
    upload_id: int,
    start_date: str | None = Query(None, description="YYYY-MM-DD, filters sales_trend"),
    end_date: str | None = Query(None, description="YYYY-MM-DD, filters sales_trend"),
):
    assert_upload_ready(upload_id)
    return analysis.full_dashboard(upload_id, start_date, end_date)


@router.get("/{upload_id}/kpi-summary", response_model=KPISummary)
def get_kpi_summary(upload_id: int):
    assert_upload_ready(upload_id)
    return analysis.kpi_summary(upload_id)


@router.get("/{upload_id}/sales-trend", response_model=list[SalesTrendPoint])
def get_sales_trend(
    upload_id: int,
    start_date: str | None = Query(None, description="YYYY-MM-DD"),
    end_date: str | None = Query(None, description="YYYY-MM-DD"),
):
    assert_upload_ready(upload_id)
    return analysis.sales_trend(upload_id, start_date, end_date)


@router.get("/{upload_id}/top-products", response_model=list[TopProduct])
def get_top_products(upload_id: int, limit: int = Query(10, ge=1, le=50)):
    assert_upload_ready(upload_id)
    return analysis.top_products(upload_id, limit)


@router.get("/{upload_id}/profit-loss")
def get_profit_loss(upload_id: int):
    assert_upload_ready(upload_id)
    return analysis.profit_loss_summary(upload_id)


@router.get("/{upload_id}/party-dues")
def get_party_dues(upload_id: int):
    assert_upload_ready(upload_id)
    return analysis.party_wise_dues(upload_id)


@router.get("/{upload_id}/cleaned-preview")
def get_cleaned_preview(upload_id: int, sample_size: int = Query(10, ge=1, le=50)):
    """preview clean data"""
    assert_upload_ready(upload_id)
    return analysis.cleaned_dataset_preview(upload_id, sample_size)


@router.get("/{upload_id}/export")
def export_cleaned_csv(upload_id: int):
    """export to csv"""
    assert_upload_ready(upload_id)

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT transaction_date, party_name, item_name, quantity, unit_price, "
            "total_amount, amount_paid, amount_pending, transaction_type "
            "FROM transactions WHERE upload_id = ? ORDER BY id",
            (upload_id,),
        ).fetchall()
        file_name_row = conn.execute(
            "SELECT file_name FROM uploads WHERE id = ?", (upload_id,)
        ).fetchone()

    columns = [
        "transaction_date", "party_name", "item_name", "quantity", "unit_price",
        "total_amount", "amount_paid", "amount_pending", "transaction_type",
    ]

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row[c] for c in columns])
    buffer.seek(0)

    original_name = (file_name_row["file_name"] if file_name_row else f"upload_{upload_id}").rsplit(".", 1)[0]
    download_name = f"{original_name}_cleaned.csv"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )

