import os
import sys
from datetime import datetime
from pathlib import Path

# Airflow puts only the dags folder on sys.path, and that folder is not always
# this repo's dags/ (a standalone run defaults to ~/airflow/dags). Find the
# project root that actually holds src/ and grocery_list.py before importing it.
_MARKERS = ("src/etl_transform.py", "grocery_list.py")


def _find_project_root() -> Path:
    override = os.getenv("ETL_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    # .resolve() follows symlinks, so a symlinked copy of this file still lands
    # on the real path inside the repo.
    for candidate in Path(__file__).resolve().parents:
        if all((candidate / marker).exists() for marker in _MARKERS):
            return candidate
    raise RuntimeError(
        f"Could not locate the project root above {Path(__file__).resolve()}. "
        "Point Airflow at this repo's dags/ folder (source scripts/setup_airflow_env.sh), "
        "symlink this file instead of copying it, or set ETL_PROJECT_ROOT."
    )


PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

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
