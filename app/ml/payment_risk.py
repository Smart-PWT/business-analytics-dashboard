"""
Payment risk prediction logic.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from app.config import MIN_TRANSACTIONS_FOR_PREDICTION, RISK_LABELS


def _build_party_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build party feature rows.
    """
    df = transactions_df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    today = pd.Timestamp(pd.Timestamp.now().date())

    df["is_overdue"] = df["amount_pending"] > 0
    df["days_since_txn"] = (today - df["transaction_date"]).dt.days

    grouped = df.groupby("party_name").agg(
        order_count=("total_amount", "count"),
        avg_order_value=("total_amount", "mean"),
        pct_orders_with_dues=("is_overdue", "mean"),
        avg_days_since_overdue_txn=("days_since_txn", lambda s: s[df.loc[s.index, "is_overdue"]].mean()
                                     if df.loc[s.index, "is_overdue"].any() else 0),
    ).reset_index()

    grouped["avg_days_since_overdue_txn"] = grouped["avg_days_since_overdue_txn"].fillna(0)
    return grouped


def _rule_based_label(row: pd.Series) -> str:
    """
    Calculate rule based labels.
    """
    pct_due = row["pct_orders_with_dues"]
    overdue_age = row["avg_days_since_overdue_txn"]

    if pct_due == 0:
        return "Low"
    if pct_due < 0.3 and overdue_age < 30:
        return "Low"
    if pct_due < 0.6 or overdue_age < 60:
        return "Medium"
    return "High"


def predict_payment_risk(transactions_df: pd.DataFrame) -> list[dict]:
    """
    Predict party payment risks.
    """
    if transactions_df.empty:
        return []

    df = transactions_df.copy()
    features = _build_party_features(df)

    # Split by data sufficiency.
    txn_counts = df.groupby("party_name").size()
    enough_data_parties = txn_counts[txn_counts >= MIN_TRANSACTIONS_FOR_PREDICTION].index
    insufficient_parties = txn_counts[txn_counts < MIN_TRANSACTIONS_FOR_PREDICTION].index

    results = []
    for party in insufficient_parties:
        results.append({"party_name": party, "status": "not_enough_data", "risk_label": None})

    eligible = features[features["party_name"].isin(enough_data_parties)].copy()
    if eligible.empty:
        return results

    # Build heuristic fallback labels.
    eligible["heuristic_label"] = eligible.apply(_rule_based_label, axis=1)

    label_diversity = eligible["heuristic_label"].nunique()
    enough_rows_to_train = len(eligible) >= 10  # Check training row count.

    if label_diversity >= 2 and enough_rows_to_train:
        # Fit logistic regression model.
        feature_cols = ["order_count", "avg_order_value", "pct_orders_with_dues", "avg_days_since_overdue_txn"]
        X = eligible[feature_cols].values
        y = eligible["heuristic_label"].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(max_iter=1000, multi_class="auto")
        model.fit(X_scaled, y)
        predicted_labels = model.predict(X_scaled)

        for party, label in zip(eligible["party_name"], predicted_labels):
            results.append({"party_name": party, "status": "ok", "risk_label": str(label)})
    else:
        # Apply rule based fallback.
        for _, row in eligible.iterrows():
            results.append({
                "party_name": row["party_name"],
                "status": "ok",
                "risk_label": row["heuristic_label"],
            })

    return results
