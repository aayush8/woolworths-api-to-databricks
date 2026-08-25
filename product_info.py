import requests
import os
from dotenv import load_dotenv
import io
import pandas as pd
from datetime import datetime

load_dotenv()

# Function to fetch product information from the API
def get_product_info(product_name, headers):
    # Set up query parameters with the product name
    querystring = {"query": product_name}
    # Make GET request to the API
    response = requests.get(os.getenv("API_URL"), headers=headers, params=querystring)
    # Check if request was successful
    if response.status_code == 200:
        # Return the JSON response data
        return response.json()
    else:
        # Print error message if request failed
        print(f"Error fetching product info: {response.status_code}")
        # Return None if no data was retrieved
        return None

# Function to fetch information for multiple products from a grocery list
def get_products_info(grocery_list, headers) -> list:
    # Initialize empty list to store product information
    products_info = []
    # Iterate through each item in the grocery list
    for grocery in grocery_list:
        # Fetch product info for current grocery item
        product_info = get_product_info(grocery, headers)
        # Check if product info was successfully retrieved
        if product_info:
            # Add product info to results list
            products_info.append(product_info)
    # Return list of all product information
    return products_info

def get_csv(groceries) -> str:
    csv_buffer = io.StringIO()
    new_groceries = []
    for grocery in groceries:
        new_groceries.append(grocery["results"][0])
    df = pd.DataFrame(new_groceries)
    retracted_date = datetime.now().strftime("%Y-%m-%d")
    retracted_time = datetime.now().strftime("%H:%M:%S")
    df["date_retracted"] = retracted_date
    df["time_retracted"] = retracted_time
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()