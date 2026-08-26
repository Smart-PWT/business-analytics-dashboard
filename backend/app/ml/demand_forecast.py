"""demand prediction logic"""

from datetime import timedelta

import pandas as pd

from ..config import (
    DEMAND_FORECAST_HORIZON_DAYS,
    MIN_TRANSACTIONS_FOR_PREDICTION,
    TOP_N_PRODUCTS,
)


def _moving_average_forecast(daily_units: pd.Series, window: int = 7) -> float:
    """get avg sales"""
    if daily_units.empty:
        return 0.0
    return float(daily_units.tail(window).mean())


def forecast_demand(transactions_df: pd.DataFrame, top_n: int = TOP_N_PRODUCTS) -> list[dict]:
    """predict top products"""
    if transactions_df.empty:
        return []

    df = transactions_df[transactions_df["transaction_type"].str.lower() == "sale"].copy()
    if df.empty:
        return []

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    top_items = (
        df.groupby("item_name")["quantity"].sum().sort_values(ascending=False).head(top_n).index
    )

    results = []
    for item in top_items:
        item_df = df[df["item_name"] == item]

        if len(item_df) < MIN_TRANSACTIONS_FOR_PREDICTION:
            results.append({
                "item_name": item,
                "status": "not_enough_data",
                "predicted_units_next_30_days": None,
                "avg_daily_units": None,
            })
            continue

        # add empty days
        daily = item_df.groupby(item_df["transaction_date"].dt.date)["quantity"].sum()
        full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
        daily = daily.reindex(full_range.date, fill_value=0)

        avg_daily_units = _moving_average_forecast(daily)
        predicted_units = round(avg_daily_units * DEMAND_FORECAST_HORIZON_DAYS, 1)

        results.append({
            "item_name": item,
            "status": "ok",
            "predicted_units_next_30_days": predicted_units,
            "avg_daily_units": round(avg_daily_units, 2),
        })

    return results


def forecast_dates(reference_date: pd.Timestamp, horizon_days: int = DEMAND_FORECAST_HORIZON_DAYS) -> list[str]:
    return [(reference_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, horizon_days + 1)]

