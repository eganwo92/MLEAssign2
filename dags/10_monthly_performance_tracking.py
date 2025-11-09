from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="10_monthly_performance_tracking",
    description="Monthly monitoring DAG — plots F1 vs time and Accuracy vs time",
    schedule_interval='@monthly',        
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
) as dag:

    run_monthly_tracking = BashOperator(
        task_id="run_monthly_performance_plot",
        bash_command="python /opt/airflow/utils/monthly_performance_plot.py",
    )

    run_monthly_tracking
