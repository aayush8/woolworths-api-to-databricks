import pandas as pd

def get_all_products(cursor) -> pd.DataFrame:
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df