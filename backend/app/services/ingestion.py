"""file ingestion pipeline"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.config import ALL_EXPECTED_COLUMNS
from app.database import get_connection
from app.services.cleaner import clean_dataframe
from app.services.column_mapper import map_columns
from app.services.validator import validate_schema


class IngestionError(Exception):
    """upload failed error"""
    def __init__(self, message: str, missing_required: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.missing_required = missing_required or []


def _read_file(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(file_path)
        except Exception:
            raise IngestionError(
                "Could not read Excel file. Please ensure it isn't corrupted or password-protected."
            )

    if suffix != ".csv":
        raise IngestionError(f"Unsupported file type '{suffix}'. Please upload a .csv or .xlsx file.")

    try:
        return pd.read_csv(file_path)
    except Exception:
        # try different encodings
        for encoding in ["utf-8", "latin-1", "iso-8859-1", "cp1252"]:
            try:
                return pd.read_csv(file_path, encoding=encoding, sep=None, engine="python")
            except Exception:
                continue
        raise IngestionError("Could not read CSV file. Please ensure it is a valid CSV with correct encoding and separator.")


def ingest_file(file_path: Path, original_file_name: str) -> dict:
    now_iso = datetime.now(timezone.utc).isoformat()

    # create upload record
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO uploads (file_name, upload_date, status) VALUES (?, ?, ?)",
            (original_file_name, now_iso, "processing"),
        )
        upload_id = cursor.lastrowid

    try:
        raw_df = _read_file(file_path)

        if raw_df.empty:
            raise IngestionError("The uploaded file has no data rows.")

        column_mapping = map_columns(list(raw_df.columns))

        result = validate_schema(column_mapping)
        if not result.is_valid:
            raise IngestionError(result.error_message, missing_required=result.missing_required)

        rename_map = {raw: expected for expected, raw in column_mapping.items() if raw is not None}
        mapped_df = raw_df.rename(columns=rename_map)
        mapped_df = mapped_df[[c for c in ALL_EXPECTED_COLUMNS if c in mapped_df.columns]]

        cleaning_result = clean_dataframe(mapped_df)
        clean_df = cleaning_result.df
        
        if "transaction_date" in clean_df.columns:
            clean_df = clean_df.sort_values(by="transaction_date", ascending=True).reset_index(drop=True)

        if clean_df.empty:
            raise IngestionError(
                "After cleaning, no valid rows remained (all rows were missing required data)."
            )

        with get_connection() as conn:
            for _, row in clean_df.iterrows():
                conn.execute(
                    """
                    INSERT INTO transactions
                        (upload_id, transaction_date, party_name, item_name, quantity,
                         unit_price, total_amount, amount_paid, amount_pending, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        upload_id,
                        row["transaction_date"].strftime("%Y-%m-%d") if pd.notna(row["transaction_date"]) else None,
                        str(row["party_name"]),
                        str(row["item_name"]),
                        float(row["quantity"]),
                        float(row["unit_price"]),
                        float(row["total_amount"]),
                        float(row["amount_paid"]),
                        float(row["amount_pending"]),
                        str(row["transaction_type"]),
                    ),
                )

            for entry in cleaning_result.log:
                conn.execute(
                    "INSERT INTO cleaning_log (upload_id, row_number, reason, raw_row) VALUES (?, ?, ?, ?)",
                    (upload_id, entry["row_number"], entry["reason"], json.dumps(entry["raw_row"], default=str)),
                )

            conn.execute("UPDATE uploads SET status = ? WHERE id = ?", ("cleaned", upload_id))

        return {
            "upload_id": upload_id,
            "status": "cleaned",
            "rows_ingested": len(clean_df),
            "rows_flagged": len(cleaning_result.log),
            "column_mapping": column_mapping,
        }

    except IngestionError as exc:
        with get_connection() as conn:
            conn.execute(
                "UPDATE uploads SET status = ?, error_message = ? WHERE id = ?",
                ("failed", exc.message, upload_id),
            )
        raise