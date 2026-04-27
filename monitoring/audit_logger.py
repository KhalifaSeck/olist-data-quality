import json
import logging
import sys
import os

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from db_connector import get_connection

log = logging.getLogger(__name__)

DDL = """
create schema if not exists quality;

create table if not exists quality.audit_log (
    id          serial primary key,
    run_at      timestamp default current_timestamp,
    source      text not null,
    rule_name   text not null,
    severity    text not null check (severity in ('info', 'warning', 'critical')),
    details     jsonb,
    resolved    boolean default false
);
"""


def ensure_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            conn.commit()


def log_anomaly(source: str, rule_name: str,
                severity: str, details: dict):
    ensure_table()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into quality.audit_log
                    (source, rule_name, severity, details)
                values (%s, %s, %s, %s)
                """,
                (source, rule_name, severity, json.dumps(details))
            )
            conn.commit()
    log.info(f"Logged [{severity}] {source}/{rule_name}")


def log_batch(anomalies: list):
    """Persiste une liste d'objets Anomaly en une fois."""
    for a in anomalies:
        log_anomaly(
            source="anomaly_detection",
            rule_name=a.metric,
            severity=a.severity,
            details={
                "date":        a.date,
                "value":       a.value,
                "expected":    a.expected,
                "z_score":     a.z_score,
                "description": a.description
            }
        )
    log.info(f"Batch logged: {len(anomalies)} anomaly(ies)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ensure_table()
    log.info("audit_log table ready.")