"""Machine learning prediction orchestrator."""

from datetime import datetime, timezone

import pandas as pd

from app.database import get_connection
from app.ml.demand_forecast import forecast_demand
from app.ml.payment_risk import predict_payment_risk


def _load_transactions(upload_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE upload_id = ?", (upload_id,)
        ).fetchall()
    return pd.DataFrame([dict(r) for r in rows])


def run_predictions(upload_id: int) -> dict:
    """Run both prediction models."""
    df = _load_transactions(upload_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    demand_results = forecast_demand(df)
    risk_results = predict_payment_risk(df)

    with get_connection() as conn:
        # Clear previous predictions
        conn.execute("DELETE FROM predictions_demand WHERE upload_id = ?", (upload_id,))
        conn.execute("DELETE FROM predictions_payment_risk WHERE upload_id = ?", (upload_id,))

        for item in demand_results:
            if item["status"] == "ok":
                conn.execute(
                    """INSERT INTO predictions_demand
                       (upload_id, item_name, forecast_date, predicted_units, generated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (upload_id, item["item_name"], now_iso, item["predicted_units_next_30_days"], now_iso),
                )

        for party in risk_results:
            conn.execute(
                """INSERT INTO predictions_payment_risk
                   (upload_id, party_name, risk_label, generated_at)
                   VALUES (?, ?, ?, ?)""",
                (upload_id, party["party_name"], party["risk_label"] or "Not enough data", now_iso),
            )

    return {
        "demand_forecast": demand_results,
        "payment_risk": risk_results,
        "generated_at": now_iso,
    }


def get_latest_predictions(upload_id: int) -> dict:
    """Fetch most recent predictions."""
    with get_connection() as conn:
        demand_rows = conn.execute(
            "SELECT item_name, predicted_units, forecast_date FROM predictions_demand WHERE upload_id = ?",
            (upload_id,),
        ).fetchall()
        risk_rows = conn.execute(
            "SELECT party_name, risk_label FROM predictions_payment_risk WHERE upload_id = ?",
            (upload_id,),
        ).fetchall()

    return {
        "demand_forecast": [dict(r) for r in demand_rows],
        "payment_risk": [dict(r) for r in risk_rows],
    }
