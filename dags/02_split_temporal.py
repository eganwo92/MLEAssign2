from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="02_split_temporal",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    description="Split gold feature store into train/val/oot/inference"
) as dag:

    split_data = BashOperator(
        task_id="split_temporal_data",
        bash_command="python -c 'from utils.training_utils import do_temporal_split; do_temporal_split()'"
    )

    split_data
