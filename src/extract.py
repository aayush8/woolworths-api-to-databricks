import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def extract(grocery_list: list) -> list:
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "woolworths-products-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    groceries = get_products_info(grocery_list, headers)
    return [grocery.get('results')[0] for grocery in groceries]

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
