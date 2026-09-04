from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.etl_transform import transform
from src.extract import extract
from src.load import load
from grocery_list import get_grocery_list

with DAG(
    dag_id='etl_pipeline_woolworths',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule=None,
    is_paused_upon_creation=True,
) as dag:
    # Define your tasks here

    grocery_list_task = PythonOperator(
        task_id='get_grocery_list',
        python_callable=get_grocery_list
    )
    
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
        op_kwargs={'grocery_list': grocery_list_task.output}

    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform,
        op_kwargs={'groceries': extract_task.output}
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load,
        op_kwargs={'df': transform_task.output}
    )

    grocery_list_task >> extract_task >> transform_task >> load_task
