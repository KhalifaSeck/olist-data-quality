import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


load_dotenv()


def _get_params() -> dict:
    return {
        "host":     os.getenv("DB_HOST", "localhost"),
        "port":     int(os.getenv("DB_PORT", 5433)),
        "dbname":   os.getenv("DB_NAME", "olist"),
        "user":     os.getenv("DB_USER", "olist_user"),
        "password": os.getenv("DB_PASSWORD", "olist_pass"),
    }


def get_connection():
    """Connexion psycopg2 pour les inserts (audit_logger)."""
    return psycopg2.connect(**_get_params())


def get_engine():
    """Engine SQLAlchemy — gardé pour compatibilité."""
    from sqlalchemy import create_engine
    p = _get_params()
    return create_engine(
        f"postgresql+psycopg2://{p['user']}:{p['password']}"
        f"@{p['host']}:{p['port']}/{p['dbname']}"
    )


def read_sql(query: str, params: dict = None) -> pd.DataFrame:
    """
    Lit une requête SQL et retourne un DataFrame pandas.
    Utilise psycopg2 directement — compatible avec toutes
    les versions de pandas et SQLAlchemy.
    """
    conn = psycopg2.connect(**_get_params())
    try:
        # Remplace les paramètres nommés :param → %(param)s
        if params:
            for key, value in params.items():
                query = query.replace(f":{key}", str(value))
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df