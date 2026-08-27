# Woolworths Grocery Data Pipeline

A small end-to-end **data engineering project** that extracts Woolworths grocery product data from an API, processes the data using **Python and Pandas**, and loads the results into **Databricks** using the Databricks SQL Connector.

The project demonstrates a simple **ETL (Extract, Transform, Load)** workflow using real-world retail product data.

---

## 🚀 Project Overview

The pipeline starts with a predefined grocery list and uses a Woolworths product API to retrieve information about each product.

The extracted data is then transformed into a Pandas DataFrame and enriched with the date and time when the data was retrieved.

Finally, the processed data is loaded into a Databricks database and stored in a `products` table.

### Pipeline

```text
Grocery List
     │
     ▼
Woolworths Product API
     │
     ▼
Python Requests
     │
     ▼
JSON Response
     │
     ▼
Pandas DataFrame
     │
     ▼
Data Transformation
     │
     ├── Add extraction date
     └── Add extraction time
     │
     ▼
Databricks SQL
     │
     ▼
Products Table
```

---

## 🛠️ Technologies Used

- **Python**
- **Pandas**
- **Requests**
- **python-dotenv**
- **Databricks SQL Connector**
- **Databricks**
- **SQL**
- **Jupyter Notebook**
- **Git & GitHub**
- **REST API**

---

## 📂 Project Structure

```text
datbricks_for_woolis_grocery/
│
├── .gitignore
├── databricks_info.py
├── grocery_list.py
├── main.ipynb
└── product_info.py
```

### File Descriptions

#### `grocery_list.py`

Contains the grocery items that the pipeline uses as input.

Example:

```python
def get_grocery_list():
    return [
        "Woolworths Full Cream Milk 3L",
        "Woolworths Peanuts Unsalted 375g",
        "Cloverdale Pure Honey Twist & Squeeze 375g",
    ]
```

#### `product_info.py`

Responsible for communicating with the product API.

It:

1. Sends a product name to the API.
2. Retrieves the JSON response.
3. Extracts product information.
4. Converts the results into a Pandas DataFrame.
5. Adds extraction date and time.
6. Produces CSV-formatted data when required.

#### `databricks_info.py`

Contains the SQL generation logic used to create the `products` table and insert records into Databricks.

The table columns are dynamically generated from the Pandas DataFrame.

#### `main.ipynb`

The main notebook that brings everything together.

It:

1. Loads environment variables.
2. Retrieves the grocery list.
3. Calls the product API.
4. Creates a Pandas DataFrame.
5. Connects to Databricks.
6. Creates the `woolis` database.
7. Creates the `products` table.
8. Inserts the records.
9. Queries the table.
10. Converts the returned records back into a Pandas DataFrame.

---

## 🔄 ETL Process

### 1. Extract

The grocery items are defined in `grocery_list.py`.

For each grocery item, the project sends a request to the product API.

```python
response = requests.get(
    os.getenv("API_URL"),
    headers=headers,
    params={"query": product_name}
)
```

The API response is returned as JSON.

---

### 2. Transform

The API results are converted into a Pandas DataFrame.

The pipeline also adds two metadata columns:

```text
date_retracted
time_retracted
```

These columns record when the product information was retrieved.

Example data:

| product_name | product_brand | current_price | product_size | date_retracted |
|---|---|---:|---|---|
| Woolworths Whole Milk Full Cream Milk | Woolworths | 4.35 | 3L | 2026-08-27 |
| Woolworths Peanuts Unsalted | Woolworths | 2.80 | 375g | 2026-08-27 |
| Cloverdale Pure Honey Twist & Squeeze | Cloverdale | 3.30 | 375g | 2026-08-27 |

---

### 3. Load

The transformed DataFrame is loaded into Databricks.

The project creates the database:

```sql
CREATE DATABASE IF NOT EXISTS woolis
```

It then creates a `products` table based on the DataFrame columns.

Rows are inserted using parameterized SQL:

```python
for row in df.itertuples(index=False, name=None):
    cursor.execute(
        sql_commands(df, 2),
        row
    )
```

Finally, the pipeline queries the table and converts the returned records back into a Pandas DataFrame.

---

## 🗄️ Databricks Architecture

The current project uses the Databricks SQL Connector to communicate with Databricks.

```text
Python Application
       │
       │ Databricks SQL Connector
       ▼
Databricks
       │
       ▼
woolis database
       │
       ▼
products table
```

The Databricks connection uses:

- Server hostname
- HTTP path
- Access token

These credentials are loaded from environment variables rather than being hard-coded into the Python source code.

---

## 🔐 Environment Variables

Create a `.env` file locally containing your API and Databricks credentials.

Example:

```text
API_URL=your_api_url
RAPIDAPI_KEY=your_rapidapi_key

DATABRICKS_SERVER_HOSTNAME=your_server_hostname
DATABRICKS_HTTP_PATH=your_http_path
DATABRICKS_ACCESS_TOKEN=your_access_token
```

The repository already includes `.env` in `.gitignore`.


## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/aayush8/datbricks_for_woolis_grocery.git
```

Move into the project:

```bash
cd datbricks_for_woolis_grocery
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install pandas requests python-dotenv databricks-sql-connector
```

---

## ▶️ Running the Project

Create your `.env` file and add the required API and Databricks credentials.

Then open:

```text
main.ipynb
```

Run the notebook cells in order.

The pipeline will:

```text
1. Load environment variables
        ↓
2. Load grocery list
        ↓
3. Query product API
        ↓
4. Extract product information
        ↓
5. Create Pandas DataFrame
        ↓
6. Add extraction timestamp
        ↓
7. Connect to Databricks
        ↓
8. Create woolis database
        ↓
9. Create products table
        ↓
10. Insert product records
        ↓
11. Query records from Databricks
```

---

## 📊 Data Collected

The product API currently provides information such as:

- Barcode
- Product name
- Product brand
- Current price
- Product size
- Product URL

The pipeline also adds:

- Extraction date
- Extraction time

This makes the project suitable for eventually tracking **grocery price changes over time**.

---


## 🎯 Project Objective

The primary objective of this project is to gain practical experience building a complete data pipeline using modern data engineering tools.

The project demonstrates how raw data can move through the following stages:

```text
Source
  ↓
Extraction
  ↓
Transformation
  ↓
Loading
  ↓
Storage
  ↓
Querying
```

It provides hands-on experience with APIs, Python, Pandas, SQL, Databricks, environment variables, and Git/GitHub.

---

## 👤 Author

**Aayush Kharel**

GitHub: [aayush8](https://github.com/aayush8)

---

## 📌 Project Status

**Status:** 🟢 Working prototype

The current version successfully demonstrates an API → Pandas → Databricks data pipeline.