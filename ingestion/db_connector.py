import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5433)),
        dbname=os.getenv("DB_NAME", "olist"),
        user=os.getenv("DB_USER", "olist_user"),
        password=os.getenv("DB_PASSWORD", "olist_pass"),
    )