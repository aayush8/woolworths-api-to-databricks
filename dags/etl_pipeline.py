import sys
from datetime import datetime
from pathlib import Path
from airflow.sdk import dag, task
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.etl_transform import transform
from src.extract import extract
from src.load import load
from grocery_list import get_grocery_list

@dag(
    dag_id='etl_pipeline_woolworths',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule=None,
    is_paused_upon_creation=True,
)
def etl_pipeline():
    @task
    def get_groceries():
        # Your implementation for getting the grocery list
        return get_grocery_list()

    @task
    def extract_task(grocery_list):
        # Your implementation for extracting data based on the grocery list
        return extract(grocery_list)

    @task
    def transform_task(groceries):
        # Your implementation for transforming the extracted data
        return transform(groceries).to_dict(orient='records')

    @task
    def load_task(df):
        # Your implementation for loading the transformed data
        load(pd.DataFrame(df))

    load_task(transform_task(extract_task(get_groceries())))

etl_pipeline()
