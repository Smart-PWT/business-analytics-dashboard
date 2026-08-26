"""dashboard analysis logic"""

from datetime import date, datetime

import pandas as pd

from app.config import TOP_N_PRODUCTS
from app.database import get_connection


def _load_transactions(upload_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE upload_id = ?", (upload_id,)
        ).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


def kpi_summary(upload_id: int) -> dict:
    df = _load_transactions(upload_id)
    if df.empty:
        return {"total_revenue": 0, "total_orders": 0, "average_order_value": 0, "total_pending_dues": 0}

    sales_df = df[df["transaction_type"].str.lower() == "sale"]
    total_revenue = float(sales_df["total_amount"].sum())
    total_orders = int(len(sales_df))
    avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0.0
    total_pending_dues = float(df["amount_pending"].sum())

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "average_order_value": round(avg_order_value, 2),
        "total_pending_dues": round(total_pending_dues, 2),
    }


def sales_trend(upload_id: int, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    df = _load_transactions(upload_id)
    if df.empty:
        return []

    sales_df = df[df["transaction_type"].str.lower() == "sale"].copy()

    if start_date:
        sales_df = sales_df[sales_df["transaction_date"] >= pd.to_datetime(start_date)]
    if end_date:
        sales_df = sales_df[sales_df["transaction_date"] <= pd.to_datetime(end_date)]

    daily = (
        sales_df.groupby(sales_df["transaction_date"].dt.date)["total_amount"]
        .sum()
        .reset_index()
        .rename(columns={"transaction_date": "date", "total_amount": "total_sales"})
        .sort_values("date")
    )

    return [
        {"date": d.isoformat() if isinstance(d, date) else str(d), "total_sales": round(float(v), 2)}
        for d, v in zip(daily["date"], daily["total_sales"])
    ]


def top_products(upload_id: int, limit: int = TOP_N_PRODUCTS) -> list[dict]:
    df = _load_transactions(upload_id)
    if df.empty:
        return []

    sales_df = df[df["transaction_type"].str.lower() == "sale"]
    grouped = (
        sales_df.groupby("item_name")["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(limit)
        .reset_index()
    )
    return [
        {"item_name": row["item_name"], "revenue": round(float(row["total_amount"]), 2)}
        for _, row in grouped.iterrows()
    ]


def profit_loss_summary(upload_id: int) -> dict:
    df = _load_transactions(upload_id)
    if df.empty:
        return {"total_profit_loss": 0, "by_product": []}

    sales_df = df[df["transaction_type"].str.lower() == "sale"]
    purchase_df = df[df["transaction_type"].str.lower() == "purchase"]

    revenue_by_item = sales_df.groupby("item_name")["total_amount"].sum()
    cost_by_item = purchase_df.groupby("item_name")["total_amount"].sum()

    all_items = sorted(set(revenue_by_item.index) | set(cost_by_item.index))
    by_product = []
    for item in all_items:
        revenue = float(revenue_by_item.get(item, 0.0))
        cost = float(cost_by_item.get(item, 0.0))
        by_product.append({
            "item_name": item,
            "revenue": round(revenue, 2),
            "cost": round(cost, 2),
            "profit_loss": round(revenue - cost, 2),
        })

    total_profit_loss = round(sum(p["profit_loss"] for p in by_product), 2)
    by_product.sort(key=lambda p: p["profit_loss"], reverse=True)

    return {"total_profit_loss": total_profit_loss, "by_product": by_product}


def party_wise_dues(upload_id: int) -> list[dict]:
    df = _load_transactions(upload_id)
    if df.empty:
        return []

    today = pd.Timestamp(datetime.now().date())

    # sum pending
    totals = df.groupby("party_name")["amount_pending"].sum().reset_index(name="total_pending")
    totals = totals[totals["total_pending"] > 0]

    # oldest unpaid
    unpaid_txns = df[df["amount_pending"] > 0]
    oldest_dates = unpaid_txns.groupby("party_name")["transaction_date"].min().reset_index(name="oldest_unpaid_date")

    grouped = pd.merge(totals, oldest_dates, on="party_name", how="inner")
    grouped["overdue_days"] = (today - grouped["oldest_unpaid_date"]).dt.days

    grouped = grouped.sort_values("total_pending", ascending=False)

    return [
        {
            "party_name": row["party_name"],
            "amount_pending": round(float(row["total_pending"]), 2),
            "overdue_days": int(row["overdue_days"]),
        }
        for _, row in grouped.iterrows()
    ]


def cleaned_dataset_preview(upload_id: int, sample_size: int = 10) -> dict:
    """preview clean data"""
    df = _load_transactions(upload_id)
    total_rows = len(df)
    if df.empty:
        return {"total_rows": 0, "first": [], "middle": [], "last": []}

    df = df.sort_values("id" if "id" in df.columns else "transaction_date").reset_index(drop=True)

    def _rows_to_dicts(sub_df: pd.DataFrame) -> list[dict]:
        out = []
        for _, row in sub_df.iterrows():
            out.append({
                "transaction_date": row["transaction_date"].strftime("%Y-%m-%d") if pd.notna(row["transaction_date"]) else None,
                "party_name": row["party_name"],
                "item_name": row["item_name"],
                "quantity": float(row["quantity"]),
                "unit_price": round(float(row["unit_price"]), 2),
                "total_amount": round(float(row["total_amount"]), 2),
                "amount_paid": round(float(row["amount_paid"]), 2) if pd.notna(row["amount_paid"]) else 0.0,
                "amount_pending": round(float(row["amount_pending"]), 2) if pd.notna(row["amount_pending"]) else 0.0,
                "transaction_type": row["transaction_type"],
            })
        return out

    n = min(sample_size, total_rows)
    first_df = df.iloc[:n]
    last_df = df.iloc[max(0, total_rows - n):]

    # sample middle rows
    middle_start = n
    middle_end = max(n, total_rows - n)
    middle_pool = df.iloc[middle_start:middle_end]
    middle_df = middle_pool if len(middle_pool) <= n else middle_pool.sample(n=n).sort_index()

    return {
        "total_rows": total_rows,
        "first": _rows_to_dicts(first_df),
        "middle": _rows_to_dicts(middle_df),
        "last": _rows_to_dicts(last_df),
    }


def full_dashboard(upload_id: int, start_date: str | None = None, end_date: str | None = None) -> dict:
    return {
        "kpi_summary": kpi_summary(upload_id),
        "sales_trend": sales_trend(upload_id, start_date, end_date),
        "top_products": top_products(upload_id),
        "profit_loss": profit_loss_summary(upload_id),
        "party_wise_dues": party_wise_dues(upload_id),
    }

