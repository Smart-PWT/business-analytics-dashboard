"""Dashboard analysis logic module."""

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
    """Calculate KPI summary cards."""
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
    """Calculate sales over time."""
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
        {"date": str(d), "total_sales": round(float(v), 2)}
        for d, v in zip(daily["date"], daily["total_sales"])
    ]


def top_products(upload_id: int, limit: int = TOP_N_PRODUCTS) -> list[dict]:
    """Get top revenue products."""
    df = _load_transactions(upload_id)
    if df.empty:
        return []

    sales_df = df[df["transaction_type"].str.lower() == "sale"]
    grouped = (
        sales_df.groupby("item_name").agg(
            total_amount=("total_amount", "sum"),
            quantity=("quantity", "sum")
        )
        .sort_values(by="total_amount", ascending=False)
        .head(limit)
        .reset_index()
    )
    return [
        {
            "item_name": row["item_name"], 
            "revenue": round(float(row["total_amount"]), 2),
            "quantity": int(row["quantity"])
        }
        for _, row in grouped.iterrows()
    ]


def profit_loss_summary(upload_id: int) -> dict:
    """Calculate profit loss summary."""
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
    """Get party wise dues."""
    df = _load_transactions(upload_id)
    if df.empty:
        return []

    today = pd.Timestamp(datetime.now().date())

    grouped = df.groupby("party_name").agg(
        total_pending=("amount_pending", "sum"),
        oldest_unpaid_date=("transaction_date", "min"),
    ).reset_index()

    # Filter parties with dues
    grouped = grouped[grouped["total_pending"] > 0]
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


def full_dashboard(upload_id: int, start_date: str | None = None, end_date: str | None = None) -> dict:
    """Aggregate all analysis views."""
    return {
        "kpi_summary": kpi_summary(upload_id),
        "sales_trend": sales_trend(upload_id, start_date, end_date),
        "top_products": top_products(upload_id),
        "profit_loss": profit_loss_summary(upload_id),
        "party_wise_dues": party_wise_dues(upload_id),
    }
