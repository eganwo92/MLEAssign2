from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="03_train_models",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    description="Train multiple models on temporal splits"
) as dag:

    train_models = BashOperator(
        task_id="train_models",
        bash_command="python /opt/airflow/utils/training_utils.py train"
    )

    train_models
