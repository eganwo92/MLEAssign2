from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="07_inference_daily",
    start_date=datetime(2024, 7, 1),
    schedule_interval="@daily",
    catchup=False,
    description="Daily inference on newly arrived data"
) as dag:

    run_inference = BashOperator(
        task_id="run_daily_inference",
        bash_command="python /opt/airflow/utils/inference_utils.py run_daily_inference"
    )

    run_inference
