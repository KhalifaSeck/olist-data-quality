import logging
import sys
import os
from dataclasses import dataclass

import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from db_connector import get_connection, get_engine, read_sql

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


@dataclass
class Anomaly:
    metric:      str
    date:        str
    value:       float
    expected:    float
    z_score:     float
    severity:    str
    description: str

def fetch_daily_revenue(days: int = 90) -> pd.DataFrame:
    query = f"""
        select
            purchase_date::date                 as date,
            coalesce(sum(order_count), 0)       as order_count,
            coalesce(sum(total_gmv), 0)         as revenue,
            avg(avg_review_score)               as avg_score
        from marts.mart_sales
        where order_status != 'canceled'
        group by 1
        order by 1
    """
    return read_sql(query)

def detect_zscore_anomalies(df: pd.DataFrame, column: str,
                             warn: float = 2.0,
                             crit: float = 3.0) -> list:
    anomalies = []
    mu  = df[column].rolling(window=30, min_periods=7).mean()
    sig = df[column].rolling(window=30, min_periods=7).std()

    for i, row in df.iterrows():
        m = mu.iloc[i]
        s = sig.iloc[i]

        if pd.isna(s) or s == 0:
            continue

        z = (row[column] - m) / s

        if abs(z) < warn:
            continue

        severity = "critical" if abs(z) >= crit else "warning"

        anomalies.append(Anomaly(
            metric=column,
            date=str(row["date"]),
            value=round(float(row[column]), 2),
            expected=round(float(m), 2),
            z_score=round(float(z), 2),
            severity=severity,
            description=(
                f"{column} = {row[column]:.0f} "
                f"(z={z:.2f}, expected ≈ {m:.0f})"
            )
        ))

    return anomalies


def detect_wow_drop(df: pd.DataFrame, column: str,
                    threshold: float = 0.30) -> list:
    anomalies = []
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    weekly = (
        df.set_index("date")[column]
        .resample("W")
        .sum()
        .reset_index()
    )
    weekly["prev"]   = weekly[column].shift(1)
    weekly["change"] = (weekly[column] - weekly["prev"]) / weekly["prev"]

    for _, row in weekly.iterrows():
        if pd.isna(row["change"]) or row["change"] >= -threshold:
            continue

        anomalies.append(Anomaly(
            metric=f"{column}_wow_drop",
            date=str(row["date"]),
            value=round(float(row[column]), 2),
            expected=round(float(row["prev"]), 2),
            z_score=0.0,
            severity="warning",
            description=(
                f"WoW drop {abs(row['change']):.0%} : "
                f"{row['prev']:.0f} → {row[column]:.0f}"
            )
        ))

    return anomalies


def run_all_checks() -> list:
    log.info("Fetching daily revenue data...")
    df = fetch_daily_revenue(days=90)

    if df.empty:
        log.warning("No data found — skipping anomaly detection.")
        return []

    anomalies = (
        detect_zscore_anomalies(df, "revenue") +
        detect_zscore_anomalies(df, "order_count") +
        detect_wow_drop(df, "revenue")
    )

    log.info(f"Anomaly detection done: {len(anomalies)} anomaly(ies) found.")
    return anomalies


if __name__ == "__main__":
    results = run_all_checks()
    if not results:
        print("No anomalies detected.")
    for a in results:
        print(f"[{a.severity.upper()}] {a.date} | {a.description}")