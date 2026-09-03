from databricks import sql
from dotenv import load_dotenv
from src.view import get_all_products
import os
import pandas as pd

load_dotenv()  # Load environment variables from .env file

def load(df: pd.DataFrame, view: bool = False) -> str:
    cursor = None
    connection = None
    try:
        connection = sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_ACCESS_TOKEN")
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS woolis")
        cursor.execute("USE woolis")
        cursor.execute(sql_commands_for_this(df, 1))
        for row in df.itertuples(index=False, name=None):
            cursor.execute(sql_commands_for_this(df, 2), row)
        if view:
            return get_all_products(cursor).to_string()
        return "Data loaded successfully into Databricks SQL warehouse."
    except Exception as e:
        return f"Error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    

def sql_commands_for_this(df: pd.DataFrame, query_num: int) -> str: 
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS products (
            {', '.join([f'{col} STRING' for col in df.columns])}
        )
    """
    rows = list(df.itertuples(index=False, name=None))
    placeholders = ", ".join(["?"] * len(df.columns))
    insert_query = f"""
        INSERT INTO products
        VALUES (
            {placeholders}
        )
    """
    if query_num == 1:
        return create_table_query
    elif query_num == 2:
        return insert_query
