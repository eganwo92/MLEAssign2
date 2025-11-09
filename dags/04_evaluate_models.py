from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="04_evaluate_models",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    description="Evaluate models on validation and OOT sets"
) as dag:

    evaluate = BashOperator(
        task_id="evaluate_models",
        bash_command="python /opt/airflow/utils/training_utils.py evaluate"
    )

    evaluate
