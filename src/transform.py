import pandas as pd
from datetime import datetime

def transform(groceries: list) -> pd.DataFrame:
   df = pd.DataFrame(groceries)
   df["date_retracted"] = datetime.now().strftime("%Y-%m-%d")
   df["time_retracted"] = datetime.now().strftime("%H:%M:%S")
   return df
