"""Data cleaning pipeline module."""

import re
from dataclasses import dataclass, field

import pandas as pd

from app.config import REQUIRED_COLUMNS


@dataclass
class CleaningResult:
    df: pd.DataFrame
    log: list[dict] = field(default_factory=list)  # Log entry records


def _log_entry(row_number: int, reason: str, raw_row: dict) -> dict:
    return {"row_number": row_number, "reason": reason, "raw_row": raw_row}


def _standardize_currency(value) -> float | None:
    """Standardize currency values correctly."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    # Extract numeric portion directly
    text_no_commas = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text_no_commas)
    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def _standardize_date(value):
    """Standardize date formats properly."""
    return pd.to_datetime(value, errors="coerce", dayfirst=True)


def clean_dataframe(df: pd.DataFrame) -> CleaningResult:
    """Run full cleaning pipeline."""
    log: list[dict] = []
    working = df.copy()
    working.reset_index(drop=True, inplace=True)

    # Remove duplicate rows
    dup_mask = working.duplicated(keep="first")
    for idx in working[dup_mask].index:
        log.append(_log_entry(int(idx), "duplicate row removed", working.loc[idx].to_dict()))
    working = working[~dup_mask].reset_index(drop=True)

    # Standardize all dates
    if "transaction_date" in working.columns:
        working["transaction_date"] = working["transaction_date"].apply(_standardize_date)

    # Standardize currency columns
    numeric_cols = ["quantity", "unit_price", "total_amount", "amount_paid", "amount_pending"]
    for col in numeric_cols:
        if col in working.columns:
            working[col] = working[col].apply(_standardize_currency)

    # Drop missing required values
    rows_to_drop = []
    for idx, row in working.iterrows():
        missing_fields = [
            col for col in REQUIRED_COLUMNS
            if col in working.columns and (pd.isna(row[col]) or row[col] is None)
        ]
        if missing_fields:
            log.append(_log_entry(
                int(idx),
                f"missing required field(s): {', '.join(missing_fields)} — row dropped",
                row.to_dict(),
            ))
            rows_to_drop.append(idx)
    working = working.drop(index=rows_to_drop).reset_index(drop=True)

    # Fill missing optional defaults
    if "amount_paid" not in working.columns:
        working["amount_paid"] = 0.0
    else:
        working["amount_paid"] = working["amount_paid"].fillna(0.0)

    # Calculate pending amount
    if "amount_pending" not in working.columns:
        working["amount_pending"] = working["total_amount"] - working["amount_paid"]
    else:
        computed = working["total_amount"] - working["amount_paid"]
        working["amount_pending"] = working["amount_pending"].fillna(computed)

    # Default transaction type
    if "transaction_type" not in working.columns:
        working["transaction_type"] = "Sale"
    else:
        working["transaction_type"] = working["transaction_type"].fillna("Sale")
        working["transaction_type"] = working["transaction_type"].replace("", "Sale")

    return CleaningResult(df=working, log=log)
