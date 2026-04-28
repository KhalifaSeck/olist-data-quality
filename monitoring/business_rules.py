import logging
import sys
import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from db_connector import read_sql

log = logging.getLogger(__name__)


def check_payment_mismatch() -> pd.DataFrame:
    query = """
        select
            p.order_id,
            sum(p.payment_value) as total_payment,
            sum(i.total) as total_items,
            round(sum(p.payment_value) - sum(i.total), 2) as difference
        from staging.stg_order_payments p
        join staging.stg_order_items i using (order_id)
        group by p.order_id
        having abs(round(sum(p.payment_value) - sum(i.total), 2)) > 0.01
    """
    df = read_sql(query)
    log.info(f"Payment mismatch: {len(df)} order(s)")
    return df


def check_stale_shipped_orders() -> pd.DataFrame:
    query = """
        select
            order_id,
            order_status,
            purchased_at,
            shipped_at,
            current_date - shipped_at::date as days_since_shipped
        from staging.stg_orders
        where order_status = 'shipped'
          and delivered_at is null
          and shipped_at < current_date - interval '30 days'
        order by days_since_shipped desc
    """
    df = read_sql(query)
    log.info(f"Stale shipped orders: {len(df)}")
    return df


def check_low_review_categories() -> pd.DataFrame:
    query = """
        select
            p.category_name_english as category,
            round(avg(r.score), 2) as avg_score,
            count(r.review_id) as review_count
        from staging.stg_order_reviews r
        join staging.stg_order_items i using (order_id)
        join marts.dim_products p using (product_id)
        group by p.category_name_english
        having avg(r.score) < 3.0
           and count(r.review_id) > 50
        order by avg_score asc
    """
    df = read_sql(query)
    log.info(f"Low review categories: {len(df)}")
    return df


def check_repeat_purchase_rate() -> dict:
    query = """
        select
            count(distinct c.unique_customer_id) as unique_customers,
            count(distinct o.order_id) as total_orders
        from staging.stg_orders o
        join staging.stg_customers c using (customer_id)
    """
    df = read_sql(query)
    row = df.iloc[0]

    rate = round(
        (1 - row["unique_customers"] / row["total_orders"]) * 100, 2
    )
    result = {
        "unique_customers": int(row["unique_customers"]),
        "total_orders": int(row["total_orders"]),
        "repeat_rate_pct": rate
    }
    log.info(f"Repeat purchase rate: {rate}%")
    return result


def run_all_rules() -> dict:
    return {
        "payment_mismatch": check_payment_mismatch(),
        "stale_shipped_orders": check_stale_shipped_orders(),
        "low_review_categories": check_low_review_categories(),
        "repeat_purchase_rate": check_repeat_purchase_rate(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = run_all_rules()

    print(f"\n--- Payment mismatches : {len(results['payment_mismatch'])} ---")
    print(results["payment_mismatch"].head())

    print(f"\n--- Stale orders : {len(results['stale_shipped_orders'])} ---")
    print(results["stale_shipped_orders"].head())

    print(f"\n--- Low review categories : {len(results['low_review_categories'])} ---")
    print(results["low_review_categories"])

    print(f"\n--- Repeat purchase rate ---")
    print(results["repeat_purchase_rate"])