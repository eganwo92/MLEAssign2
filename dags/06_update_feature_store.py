from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="06_update_feature_store",
    start_date=datetime(2024, 7, 1),
    schedule_interval="@daily",
    catchup=False,
    description="Daily incremental update to feature store"
) as dag:

    update_store = BashOperator(
        task_id="append_new_data_to_feature_store",
        bash_command="python /opt/airflow/utils/feature_store_utils.py update_feature_store"
    )

    update_store
