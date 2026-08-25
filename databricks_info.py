import pandas as pd

def sql_commands(df: pd.DataFrame, query_num: int) -> str:

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
