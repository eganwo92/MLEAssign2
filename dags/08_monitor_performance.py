from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="08_monitor_performance",
    start_date=datetime(2024, 7, 1),
    schedule_interval="@daily",
    catchup=False,
    description="Monitor model performance and drift"
) as dag:

    monitor_model = BashOperator(
        task_id="monitor_model_performance",
        bash_command="python /opt/airflow/utils/monitoring_utils.py monitor_daily"
    )

    monitor_model
