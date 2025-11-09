from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="05_register_best_model",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    description="Register the best model in the model store"
) as dag:

    register = BashOperator(
        task_id="register_best_model",
        bash_command="python /opt/airflow/utils/training_utils.py register"
    )

    register
