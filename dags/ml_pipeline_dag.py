from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "ml_pipeline_dag",
    default_args=default_args,
    description="Loan Default ML Pipeline",
    schedule_interval=None,  # run manually or on schedule if needed
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command="python /opt/airflow/main.py",
    )

    run_pipeline
