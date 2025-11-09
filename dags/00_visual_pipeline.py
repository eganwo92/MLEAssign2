from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id="00_visual_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description="Visual DAG showing Flow A (01–05) and Flow B (06–09) with retrain note",
) as dag:

    start = DummyOperator(task_id="start_pipeline")

    with TaskGroup("Flow_A_Data_Model_Prep") as flow_a:
        t01 = DummyOperator(task_id="01_build_feature_store")
        t02 = DummyOperator(task_id="02_split_temporal")
        t03 = DummyOperator(task_id="03_train_model")
        t04 = DummyOperator(task_id="04_validate_model")
        t05 = DummyOperator(task_id="05_monitor_model")
        t01 >> t02 >> t03 >> t04 >> t05

    with TaskGroup("Flow_B_Daily_Operations") as flow_b:
        t06 = DummyOperator(task_id="06_update_feature_store")
        t07 = DummyOperator(task_id="07_inference_daily")
        t08 = DummyOperator(task_id="08_monitoring_daily")
        t09 = DummyOperator(task_id="09_trigger_retrain")
        t10 = DummyOperator(task_id="10_monthly_performance_tracking")
        t06 >> t07 >> t08 >> t09 >> t10

    # renamed this
    retrain_note = DummyOperator(
        task_id="note_retrain_triggers_FlowA_split_temporal"
    )

    start >> [flow_a, flow_b]
    t09 >> retrain_note
