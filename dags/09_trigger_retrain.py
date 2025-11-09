from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import json
from pathlib import Path


def check_accuracy(**context):
    metrics_path = Path("/opt/airflow/model_store/metadata.json")

    if not metrics_path.exists():
        print("⚠️ No metrics file found → trigger full retrain (02).")
        return "trigger_full_retrain"

    with open(metrics_path, "r") as f:
        meta = json.load(f)
        acc = meta.get("metrics", {}).get("accuracy", 0)

    print(f"📊 Latest model accuracy = {acc:.3f}")
    return "trigger_full_retrain" if acc < 0.7 else "no_retrain_needed"


with DAG(
    dag_id="09_trigger_retrain",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description="Trigger DAG 02_split_temporal if accuracy < 0.7, else skip retrain.",
) as dag:

    # 1️⃣ Decision node
    decide = BranchPythonOperator(
        task_id="check_accuracy_threshold",
        python_callable=check_accuracy,
    )

    # 2️⃣ Trigger the retraining chain starting from DAG 02
    trigger_full = TriggerDagRunOperator(
        task_id="trigger_full_retrain",
        trigger_dag_id="02_split_temporal",
        wait_for_completion=False,
    )

    # 3️⃣ End path (no retraining needed)
    skip = EmptyOperator(task_id="no_retrain_needed")

    decide >> [trigger_full, skip]
