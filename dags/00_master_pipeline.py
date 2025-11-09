from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

# ==========================
# 🧩 FLOW A: 01 → 02 → 03 → 04 → 05
# ==========================
with DAG(
    dag_id="00_master_flow_A",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description="Master DAG for data prep, splitting, training, and validation (01→05)",
) as dag_a:

    t01 = TriggerDagRunOperator(
        task_id="trigger_01_build_feature_store",
        trigger_dag_id="01_build_feature_store",
        wait_for_completion=True,
    )

    t02 = TriggerDagRunOperator(
        task_id="trigger_02_split_temporal",
        trigger_dag_id="02_split_temporal",
        wait_for_completion=True,
    )

    t03 = TriggerDagRunOperator(
        task_id="trigger_03_train_model",
        trigger_dag_id="03_train_model",
        wait_for_completion=True,
    )

    t04 = TriggerDagRunOperator(
        task_id="trigger_04_validate_model",
        trigger_dag_id="04_validate_model",
        wait_for_completion=True,
    )

    t05 = TriggerDagRunOperator(
        task_id="trigger_05_monitor_model",
        trigger_dag_id="05_monitor_model",
        wait_for_completion=True,
    )

    t01 >> t02 >> t03 >> t04 >> t05


# ==========================
# 🧩 FLOW B: 06 → 07 → 08 → 09
# ==========================
with DAG(
    dag_id="00_master_flow_B",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description="Master DAG for daily updates, inference, monitoring, and retraining (06→09)",
) as dag_b:

    t06 = TriggerDagRunOperator(
        task_id="trigger_06_update_feature_store",
        trigger_dag_id="06_update_feature_store",
        wait_for_completion=True,
    )

    t07 = TriggerDagRunOperator(
        task_id="trigger_07_inference_daily",
        trigger_dag_id="07_inference_daily",
        wait_for_completion=True,
    )

    t08 = TriggerDagRunOperator(
        task_id="trigger_08_monitoring_daily",
        trigger_dag_id="08_monitoring_daily",
        wait_for_completion=True,
    )

    t09 = TriggerDagRunOperator(
        task_id="trigger_09_trigger_retrain",
        trigger_dag_id="09_trigger_retrain",
        wait_for_completion=True,
    )

    t10 = TriggerDagRunOperator(
    task_id="trigger_10_monthly_performance_tracking",
    trigger_dag_id="10_monthly_performance_tracking",
    wait_for_completion=True,
    )

    t06 >> t07 >> t08 >> t09 >> t10

