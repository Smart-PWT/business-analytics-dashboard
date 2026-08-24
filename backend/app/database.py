"""
SQLite database interaction layer.
"""

import sqlite3
from contextlib import contextmanager

from .config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',   -- Upload processing status value.
    error_message TEXT,
    user_id TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    transaction_date TEXT NOT NULL,
    party_name TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    total_amount REAL NOT NULL,
    amount_paid REAL,
    amount_pending REAL,
    transaction_type TEXT
);

CREATE TABLE IF NOT EXISTS cleaning_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    row_number INTEGER,
    reason TEXT NOT NULL,       -- Row flag drop reason.
    raw_row TEXT                -- Serialized raw row data.
);

CREATE TABLE IF NOT EXISTS predictions_demand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    item_name TEXT NOT NULL,
    forecast_date TEXT NOT NULL,
    predicted_units REAL,
    generated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions_payment_risk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER NOT NULL REFERENCES uploads(id),
    party_name TEXT NOT NULL,
    risk_label TEXT NOT NULL,      -- Evaluated payment risk label.
    generated_at TEXT NOT NULL
);
"""


@contextmanager
def get_connection():
    """
    Context managed SQLite connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize SQLite database tables."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
