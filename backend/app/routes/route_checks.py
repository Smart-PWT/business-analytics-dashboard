"""shared route checks"""

from fastapi import HTTPException

from app.database import get_connection


def assert_upload_ready(upload_id: int):
    """check upload status"""
    with get_connection() as conn:
        row = conn.execute("SELECT status FROM uploads WHERE id = ?", (upload_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"No upload found with id {upload_id}.")
    if row["status"] != "cleaned":
        raise HTTPException(
            status_code=409,
            detail=f"Upload {upload_id} is not ready yet (status: {row['status']}).",
        )
