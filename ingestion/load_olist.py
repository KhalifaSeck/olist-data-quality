import argparse
import logging
from pathlib import Path

import pandas as pd
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

from db_connector import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TABLES = {
    "olist_orders_dataset.csv":                      "raw.orders",
    "olist_order_items_dataset.csv":                 "raw.order_items",
    "olist_customers_dataset.csv":                   "raw.customers",
    "olist_products_dataset.csv":                    "raw.products",
    "olist_sellers_dataset.csv":                     "raw.sellers",
    "olist_order_payments_dataset.csv":              "raw.order_payments",
    "olist_order_reviews_dataset.csv":               "raw.order_reviews",
    "olist_geolocation_dataset.csv":                 "raw.geolocation",
    "olist_closed_deals_dataset.csv":                "raw.closed_deals",
    "olist_marketing_qualified_leads_dataset.csv":   "raw.marketing_leads",
    "product_category_name_translation.csv":         "raw.category_translation",
}


def create_raw_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        conn.commit()
    log.info("Schema 'raw' prêt.")


def load_csv(conn, path: Path, table: str):
    log.info(f"Chargement {path.name} → {table}")
    df = pd.read_csv(path, low_memory=False)

    # Normaliser les noms de colonnes
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    with conn.cursor() as cur:
        # Supprimer la table si elle existe déjà
        cur.execute(f"DROP TABLE IF EXISTS {table};")

        # Créer la table avec toutes les colonnes en TEXT
        cols = ", ".join(f'"{c}" TEXT' for c in df.columns)
        cur.execute(f"CREATE TABLE {table} ({cols});")

        # Insérer les données
        rows = [
            tuple(str(v) if pd.notna(v) else None for v in row)
            for row in df.itertuples(index=False)
        ]
        execute_values(
            cur,
            f"INSERT INTO {table} VALUES %s",
            rows
        )
        conn.commit()

    log.info(f"  → {len(df):,} lignes chargées dans {table}")


def main(data_dir: str):
    data_path = Path(data_dir)

    if not data_path.exists():
        log.error(f"Dossier introuvable : {data_path}")
        return

    conn = get_connection()
    create_raw_schema(conn)

    for filename, table in TABLES.items():
        csv_file = data_path / filename
        if csv_file.exists():
            load_csv(conn, csv_file, table)
        else:
            log.warning(f"Fichier absent : {filename} — ignoré")

    conn.close()
    log.info("Ingestion terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Charge les CSV Olist dans PostgreSQL")
    parser.add_argument("--data-dir", default="./data/olist", help="Chemin vers les CSV")
    args = parser.parse_args()
    main(args.data_dir)