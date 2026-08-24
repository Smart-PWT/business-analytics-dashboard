"""
Ingestion orchestrator — ties together file parsing, column mapping,
schema validation, cleaning, and persistence into a single pipeline.

This is what app/routes/upload.py calls. Keeping the orchestration
separate from the route handler means it's testable without spinning
up FastAPI, and it's the natural place to plug in the Groq LLM mapper
later (v2) as a pre-step before the rule-based column_mapper fallback.
"""

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
    """Raised when an upload cannot proceed (FR2.3 — clear, non-silent failure)."""
    def __init__(self, message: str, missing_required: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.missing_required = missing_required or []


def _read_file(file_path: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame. Raises IngestionError on bad files."""
    suffix = file_path.suffix.lower()
    if suffix != ".csv":
        raise IngestionError(f"Unsupported file type '{suffix}'. Please upload a .csv file.")
    
    try:
        # Try default parsing first
        return pd.read_csv(file_path)
    except Exception:
        # If it fails, try with different encodings and automatic separator detection
        encodings_to_try = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
        for encoding in encodings_to_try:
            try:
                # python engine with sep=None allows auto-detecting separators like ;
                return pd.read_csv(file_path, encoding=encoding, sep=None, engine="python")
            except Exception:
                continue
        raise IngestionError("Could not read CSV file. Please ensure it is a valid CSV with correct encoding and separator.")


def ingest_file(file_path: Path, original_file_name: str, user_id: str | None = None) -> dict:
    """
    Full pipeline: read -> map columns -> validate -> clean -> persist.

    Returns a summary dict with upload_id, row counts, and cleaning log
    summary. Raises IngestionError for anything that should surface as
    a 4xx to the API caller (bad schema, unreadable file, etc).
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Create the upload record up front (status='processing') so we
    #    always have an audit trail, even if later steps fail.
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO uploads (file_name, upload_date, status, user_id) VALUES (?, ?, ?, ?)",
            (original_file_name, now_iso, "processing", user_id),
        )
        upload_id = cursor.lastrowid

    try:
        raw_df = _read_file(file_path)

        if raw_df.empty:
            raise IngestionError("The uploaded file has no data rows.")

        # 2. Map raw headers -> expected schema columns (rule-based, FR2.2 support)
        column_mapping = map_columns(list(raw_df.columns))

        # 3. Validate required columns are present (FR2.2, FR2.3)
        result = validate_schema(column_mapping)
        if not result.is_valid:
            raise IngestionError(result.error_message, missing_required=result.missing_required)

        # 4. Rename raw columns to standardized schema names, keep only expected columns
        rename_map = {raw: expected for expected, raw in column_mapping.items() if raw is not None}
        mapped_df = raw_df.rename(columns=rename_map)
        mapped_df = mapped_df[[c for c in ALL_EXPECTED_COLUMNS if c in mapped_df.columns]]

        # 5. Run the cleaning pipeline (FR3.1-FR3.5)
        cleaning_result = clean_dataframe(mapped_df)
        clean_df = cleaning_result.df

        if clean_df.empty:
            raise IngestionError(
                "After cleaning, no valid rows remained (all rows were missing required data)."
            )

        # 6. Persist cleaned transactions + cleaning log + upload status
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
