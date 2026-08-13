"""Export API endpoints — cleaned dataset preview and CSV download."""

import csv
import io
import random

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.database import get_connection

router = APIRouter(prefix="/api/export", tags=["export"])

_COLUMNS = [
    "transaction_date",
    "party_name",
    "item_name",
    "quantity",
    "unit_price",
    "total_amount",
    "amount_paid",
    "amount_pending",
    "transaction_type",
]


def _fetch_rows(upload_id: int) -> list[dict]:
    """Return all cleaned transaction rows for a given upload."""
    with get_connection() as conn:
        upload = conn.execute(
            "SELECT id FROM uploads WHERE id = ?", (upload_id,)
        ).fetchone()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found.")

        rows = conn.execute(
            f"""
            SELECT {', '.join(_COLUMNS)}
            FROM transactions
            WHERE upload_id = ?
            ORDER BY transaction_date ASC, id ASC
            """,
            (upload_id,),
        ).fetchall()

    return [dict(r) for r in rows]


@router.get("/{upload_id}/preview")
def get_preview(upload_id: int, n: int = 10):
    """
    Return a preview of the cleaned dataset split into three groups:
    - first n rows
    - n random rows from the middle
    - last n rows
    """
    all_rows = _fetch_rows(upload_id)
    total = len(all_rows)

    if total == 0:
        raise HTTPException(status_code=404, detail="No cleaned rows found for this upload.")

    first = all_rows[:n]
    last = all_rows[max(0, total - n):]

    # Middle = everything between first and last slices
    middle_pool = all_rows[n: max(n, total - n)]
    k = min(n, len(middle_pool))
    middle = random.sample(middle_pool, k) if k > 0 else []

    return {
        "total_rows": total,
        "first": first,
        "middle": middle,
        "last": last,
    }


@router.get("/{upload_id}/csv")
def export_csv(upload_id: int):
    """Stream the full cleaned dataset as a downloadable CSV file."""
    all_rows = _fetch_rows(upload_id)

    if not all_rows:
        raise HTTPException(status_code=404, detail="No cleaned rows found for this upload.")

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_COLUMNS)
    writer.writeheader()
    writer.writerows(all_rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cleaned_{upload_id}.csv"},
    )
