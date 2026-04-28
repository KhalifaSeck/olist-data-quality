from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner":   "olist-dq",
    "retries": 0,
}

with DAG(
    dag_id="olist_quality_check",
    description="Checks qualité horaires — anomalies + alerting",
    schedule_interval="0 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["olist", "quality"],
) as dag:

    def _check_and_alert(**ctx):
        import sys
        sys.path.insert(0, "/usr/local/airflow")
        from monitoring.anomaly_detection import run_all_checks
        from monitoring.audit_logger import log_batch
        from alerting.email_alert import send_alert

        anomalies = run_all_checks()
        log_batch(anomalies)

        # Alerter uniquement sur les critiques
        critical = [a for a in anomalies if a.severity == "critical"]
        if critical:
            send_alert(
                critical,
                subject="Olist DQ — CRITICAL anomalies détectées"
            )
            print(f"{len(critical)} critical anomaly(ies) — alert sent.")
        else:
            print(f"{len(anomalies)} anomaly(ies) — no critical — no alert.")

    PythonOperator(
        task_id="check_and_alert",
        python_callable=_check_and_alert,
    )