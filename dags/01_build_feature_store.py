from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="01_build_feature_store",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    description="Build or update gold feature store"
) as dag:

    build_gold = BashOperator(
        task_id="build_gold_feature_store",
        bash_command="python /opt/airflow/utils/training_utils.py build_gold"
    )

    build_gold
