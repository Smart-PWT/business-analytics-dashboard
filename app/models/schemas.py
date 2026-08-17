"""
Pydantic response schema definitions.
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_id: int
    status: str
    rows_ingested: int
    rows_flagged: int
    column_mapping: dict[str, str | None]


class KPISummary(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    total_pending_dues: float


class SalesTrendPoint(BaseModel):
    date: str
    total_sales: float


class TopProduct(BaseModel):
    item_name: str
    revenue: float
    quantity: int


class ProfitLossByProduct(BaseModel):
    item_name: str
    revenue: float
    cost: float
    profit_loss: float


class ProfitLossSummary(BaseModel):
    total_profit_loss: float
    by_product: list[ProfitLossByProduct]


class PartyDue(BaseModel):
    party_name: str
    amount_pending: float
    overdue_days: int


class DashboardResponse(BaseModel):
    kpi_summary: KPISummary
    sales_trend: list[SalesTrendPoint]
    top_products: list[TopProduct]
    profit_loss: ProfitLossSummary
    party_wise_dues: list[PartyDue]


class DemandForecastItem(BaseModel):
    item_name: str
    status: str  # Forecast data status flag.
    predicted_units_next_30_days: float | None
    avg_daily_units: float | None


class PaymentRiskItem(BaseModel):
    party_name: str
    status: str  # Risk data status flag.
    risk_label: str | None


class PredictionsResponse(BaseModel):
    demand_forecast: list[DemandForecastItem]
    payment_risk: list[PaymentRiskItem]
    generated_at: str
