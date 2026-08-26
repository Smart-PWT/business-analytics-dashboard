"""stores backend settings"""

from pathlib import Path
from dotenv import load_dotenv

# load env explicitly
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
print(f"[config] .env loaded from {Path(__file__).resolve().parent.parent / '.env'}")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "db" / "hisaabi.db"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

REQUIRED_COLUMNS = [
    "transaction_date",
    "party_name",
    "item_name",
    "quantity",
    "unit_price",
    "total_amount",
]

COLUMN_SYNONYMS = {
    "transaction_date": ["date", "txndate", "billdate", "invoicedate", "transactiondate"],
    "party_name": ["party", "partyname", "customer", "customername", "client", "supplier", "vendor"],
    "item_name": ["item", "itemname", "product", "productname", "description"],
    "quantity": ["qty", "quantity", "units"],
    "unit_price": ["price", "unitprice", "rate", "priceper unit"],
    "total_amount": ["amount", "total", "totalamount", "netamount", "grandtotal"],
    "amount_paid": ["paid", "amountpaid", "received", "amountreceived"],
    "amount_pending": ["pending", "due", "balance", "amountpending", "amountdue"],
    "transaction_type": ["type", "transactiontype", "saletype"],
}

MIN_TRANSACTIONS_FOR_PREDICTION = 5

DEMAND_FORECAST_HORIZON_DAYS = 30
TOP_N_PRODUCTS = 10
RISK_LABELS = ["Low", "Medium", "High"]

ALL_EXPECTED_COLUMNS = list(COLUMN_SYNONYMS.keys())

# column mapping config

# allow llm fallback
ENABLE_LLM_COLUMN_FALLBACK = True

# llm model name
GROQ_MODEL = "openai/gpt-oss-20b"

