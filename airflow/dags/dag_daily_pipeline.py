"""
DAG principal — pipeline quotidien Olist.
"""
from datetime import datetime, timedelta
import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner":            "olist-dq",
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="olist_daily_pipeline",
    description="Pipeline quotidien Olist",
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-1),
    catchup=False,
    default_args=default_args,
    tags=["olist", "pipeline"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_olist_csv",
        bash_command=(
            "cd /usr/local/airflow && "
            "python ingestion/load_olist.py "
            "--data-dir /usr/local/airflow/data/olist"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /usr/local/airflow/dbt_project && "
            "dbt build --profiles-dir ."
        ),
    )

    def _run_anomaly_detection(**ctx):
        import sys
        sys.path.insert(0, "/usr/local/airflow")
        from monitoring.anomaly_detection import run_all_checks
        from monitoring.audit_logger import log_batch
        anomalies = run_all_checks()
        log_batch(anomalies)
        ctx["ti"].xcom_push(key="anomaly_count", value=len(anomalies))
        ctx["ti"].xcom_push(key="anomalies", value=[
            {
                "metric":      a.metric,
                "date":        a.date,
                "value":       a.value,
                "expected":    a.expected,
                "z_score":     a.z_score,
                "severity":    a.severity,
                "description": a.description
            }
            for a in anomalies
        ])

    def _run_business_rules(**ctx):
        import sys
        sys.path.insert(0, "/usr/local/airflow")
        from monitoring.business_rules import run_all_rules
        results = run_all_rules()
        for rule, data in results.items():
            if isinstance(data, dict):
                print(f"{rule} : {data}")
            else:
                print(f"{rule} : {len(data)} violation(s)")

    def _run_alerting(**ctx):
        import sys
        sys.path.insert(0, "/usr/local/airflow")
        from monitoring.anomaly_detection import Anomaly
        from alerting.email_alert import send_alert

        raw = ctx["ti"].xcom_pull(
            task_ids="anomaly_detection",
            key="anomalies"
        )

        if not raw:
            print("No anomalies — skipping alert.")
            return

        anomalies = [
            Anomaly(
                metric=a["metric"],
                date=a["date"],
                value=a["value"],
                expected=a["expected"],
                z_score=a["z_score"],
                severity=a["severity"],
                description=a["description"]
            )
            for a in raw
        ]

        critical = [a for a in anomalies if a.severity == "critical"]
        if len(anomalies) > 10:
            send_alert(
                critical,
                subject=f"Olist DQ — {len(critical)} anomalie(s) CRITICAL"
            )
        else:
            send_alert(
                anomalies,
                subject=f"Olist DQ — {len(anomalies)} anomalie(s)"
            )

    anomaly_detection = PythonOperator(
        task_id="anomaly_detection",
        python_callable=_run_anomaly_detection,
    )

    business_rules = PythonOperator(
        task_id="business_rules",
        python_callable=_run_business_rules,
    )

    alerting = PythonOperator(
        task_id="alerting",
        python_callable=_run_alerting,
    )

    ingest >> dbt_build >> anomaly_detection >> business_rules >> alerting