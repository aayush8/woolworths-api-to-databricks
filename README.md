# Woolworths API to Databricks

A Python ETL project that retrieves grocery product data from a third-party Woolworths products API on RapidAPI, adds collection timestamps with Pandas, and appends the results to a Databricks SQL table. Apache Airflow orchestrates the pipeline, with Docker Compose providing the local runtime.

This project demonstrates API ingestion, modular Python ETL, Airflow TaskFlow dependencies, containerized orchestration, and SQL warehouse loading.

## How it works

The DAG runs four tasks in sequence:

1. **`get_groceries`** reads six product search strings from `grocery_list.py`.
2. **`extract_task`** queries the API once per grocery item and selects the first result from each successful response.
3. **`transform_task`** creates a Pandas DataFrame, adds `date_retracted` and `time_retracted`, and returns a list of dictionaries.
4. **`load_task`** reconstructs the DataFrame and inserts its rows into Databricks.

Airflow passes task return values through XCom. The current pipeline uses in-memory records; it does not write intermediate datasets to the mounted `data/` directory.

### DAG configuration

| Setting | Value |
| --- | --- |
| DAG ID | `etl_pipeline_woolworths` |
| Definition | `dags/etl_pipeline.py` |
| API | Airflow TaskFlow: `@dag` and `@task` |
| Schedule | Manual (`schedule=None`) |
| Start date | January 1, 2026 |
| Catchup | Disabled |
| Initial state | Paused |
| Task retries | None configured in the DAG; committed configuration defaults to zero |

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python 3.12 | Runtime selected by the Dockerfile |
| Apache Airflow 3.3.1 | Workflow orchestration, as pinned in the Dockerfile |
| Docker Compose | Runs the local Airflow services and dependencies |
| Requests | HTTP requests to RapidAPI |
| Pandas | Record transformation and DataFrame handling |
| python-dotenv | Loads `.env` values for direct Python execution |
| Databricks SQL Connector | Connects to the warehouse and executes SQL |
| PostgreSQL 16 | Airflow metadata and Celery result backend |
| Redis 7.2 | Celery message broker |

PostgreSQL stores orchestration state. Product records are stored in Databricks.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `dags/etl_pipeline.py` | Defines the four Airflow tasks and their dependencies |
| `grocery_list.py` | Product search list |
| `src/extract.py` | API requests and first-result selection |
| `src/etl_transform.py` | DataFrame creation and timestamp columns |
| `src/load.py` | Databricks connection, schema/table creation, and inserts |
| `src/view.py` | Queries `products` and returns a DataFrame |
| `src/__init__.py` | Python package marker |
| `Dockerfile` | Extends the Airflow image and installs project dependencies |
| `docker-compose.yaml` | Services, environment variables, mounts, and health checks |
| `requirements.txt` | Project Python dependencies |
| `config/airflow.cfg` | Committed Airflow configuration |
| `scripts/airflow.sh` | Helper for an existing local macOS Airflow environment |
| `main.ipynb` | Runs the modular ETL functions interactively |
| `product_info.py` | Earlier API/CSV helper; not used by the current DAG |
| `logs/` | Airflow logs; some generated logs are currently tracked |

Create `.env` locally. The `data/` and `plugins/` directories are mounted by Compose but are not required by the current ETL logic.

## Run with Docker Compose

### 1. Prerequisites

- Docker Desktop running, with the `docker compose` command available.
- Resources for the multi-service stack. The included initialization script checks for at least 4 GB of memory, 2 CPUs, and 10 GB of disk space.
- Access to the Woolworths products API on RapidAPI, including its search endpoint and an API key.
- A Databricks SQL warehouse, server hostname, HTTP path, and access token.
- Databricks permissions to use the warehouse, create the `woolis` schema and `products` table, and insert records in the active catalog.

A host Python virtual environment is not needed for the Docker workflow.

### 2. Clone the project

```bash
git clone https://github.com/aayush8/woolworths-api-to-databricks.git
cd woolworths-api-to-databricks
mkdir -p logs plugins config data
```

### 3. Declare the dotenv dependency

Both `src/extract.py` and `src/load.py` import `dotenv`, but `python-dotenv` is currently commented out in `requirements.txt`. Uncomment it so the application declares the dependency explicitly:

```text
pandas
requests
python-dotenv
databricks-sql-connector
```

The Dockerfile installs Airflow separately at the version supplied by its base image.

### 4. Configure environment variables

Create `.env` in the repository root:

```dotenv
# Use 50000 for a local Docker Desktop setup on macOS.
# On Linux, replace this with the output of: id -u
AIRFLOW_UID=50000

# Use the actual search endpoint shown in your RapidAPI subscription.
API_URL=https://your-api-host/your-search-endpoint
RAPIDAPI_KEY=your_rapidapi_key

# Hostname only: do not include https://.
DATABRICKS_SERVER_HOSTNAME=your-workspace-hostname
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=your_databricks_token

# Local Airflow UI account created during initialization.
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=choose_a_local_password
```

The extraction module fixes the `x-rapidapi-host` header to `woolworths-products-api.p.rapidapi.com`. The API URL must point to the matching service and accept the `query` parameter.

**API key spelling:** Python reads `RAPIDAPI_KEY`. Compose currently also contains a misspelled `RAPIDDAPI_KEY` entry. Keep the correctly spelled variable in `.env`; Compose's `env_file` passes it to the containers. For consistency, replace the misspelled Compose entry with:

```yaml
RAPIDAPI_KEY: ${RAPIDAPI_KEY:-}
```

The repository excludes `.env` from Git and Docker's build context. Compose supplies the variables to containers at runtime.

### 5. Build and initialize

Run these commands from the repository root:

```bash
# Build the custom Airflow image with project dependencies.
docker compose build

# Initialize Airflow's metadata database and create the UI account.
docker compose up airflow-init
```

Wait for `airflow-init` to finish successfully before starting the remaining services. A successful initialization container exits; it is not a continuously running service.

### 6. Start Airflow

```bash
docker compose up -d
docker compose ps
```

Open [http://localhost:8080](http://localhost:8080) and sign in using the account configured in `.env`. If account variables are omitted, the Compose defaults are `airflow` / `airflow`.

The default stack runs the API server, scheduler, DAG processor, Celery worker, triggerer, PostgreSQL, and Redis. The CLI and Flower services use optional profiles.

Compose environment settings override several values in `config/airflow.cfg`: the Docker stack uses **CeleryExecutor**, **PostgreSQL**, **FAB authentication**, and **disabled example DAGs**, even though the committed config file contains different defaults.

### 7. Trigger the pipeline

In the Airflow UI, find `etl_pipeline_woolworths`, unpause it, and trigger a run. Inspect each task's logs as the run progresses.

You can also use the terminal:

```bash
docker compose exec airflow-scheduler airflow dags list
docker compose exec airflow-scheduler airflow dags unpause etl_pipeline_woolworths
docker compose exec airflow-scheduler airflow dags trigger etl_pipeline_woolworths
```

Unpausing does not create a recurring schedule. Each run must be triggered manually.

### 8. Verify the warehouse data

In Databricks SQL, select the same catalog used by the connector and run:

```sql
SELECT *
FROM woolis.products
LIMIT 100;

SELECT date_retracted, COUNT(*) AS row_count
FROM woolis.products
GROUP BY date_retracted
ORDER BY date_retracted DESC;
```

**Verify the table even when Airflow shows success.** The current `load()` function catches exceptions and returns an error string, while `load_task` ignores the return value. A failed database operation can therefore leave the task marked successful.

## Data and loading behavior

API response fields determine the DataFrame columns. These may include barcode, product name, brand, price, size, and product URL; the source schema is not fixed in the code.

The transformation adds two columns, retaining the names used by the implementation:

| Column | Format | Meaning |
| --- | --- | --- |
| `date_retracted` | `YYYY-MM-DD` | Date when transformation runs |
| `time_retracted` | `HH:MM:SS` | Time when transformation runs |

These values use `datetime.now()` in the executing environment. They are batch transformation timestamps, not individual API request timestamps, and do not include timezone information.

The loader:

1. Creates the `woolis` schema if it does not exist.
2. Selects that schema in the connection's current catalog.
3. Creates `products` if absent, declaring every DataFrame column as SQL `STRING`.
4. Inserts rows individually using parameterized `?` placeholders.
5. Closes the cursor and connection.

Every run **appends rows**. The implementation does not deduplicate, upsert, evolve an existing table's schema, or enforce native numeric/date types. Failed or repeated runs may produce partial or duplicate data. Price analysis requires appropriate SQL casts.

## Run the Python ETL without Airflow

For a direct run on macOS/Linux, configure the same `.env` file and create a separate Python environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt python-dotenv
```

Run this from the repository root:

```bash
python - <<'PY'
from grocery_list import get_grocery_list
from src.extract import extract
from src.etl_transform import transform
from src.load import load

records = extract(get_grocery_list())
if not records:
    raise RuntimeError("No product records were extracted")

print(load(transform(records), view=True))
PY
```

This writes to Databricks and prints the returned table or error message. The notebook `main.ipynb` uses the same functions and can be opened with a separately installed Jupyter environment.

`scripts/airflow.sh` is an existing local-development helper, not a Docker startup script. It assumes a prepared `.venv` containing Airflow, `jq`, macOS `pbcopy`, and an already generated Simple Auth Manager password file. `requirements.txt` alone does not install local Airflow.

## Everyday commands

```bash
# View service status, including exited containers.
docker compose ps -a

# Follow logs; press Ctrl+C to stop following.
docker compose logs -f airflow-worker airflow-dag-processor

# Check DAG import errors.
docker compose exec airflow-scheduler airflow dags list-import-errors

# Rebuild and recreate services after dependency or Dockerfile changes.
docker compose up -d --build

# Stop containers while retaining them.
docker compose stop

# Remove project containers and networks; retain the named database volume.
docker compose down
```

The DAG, `src/`, and `grocery_list.py` are bind-mounted into the containers, so source edits are visible without rebuilding the image. Allow time for the DAG processor to refresh its definition. Changing `.env` requires recreating services with `docker compose up -d`.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| DAG is missing | Inspect DAG processor logs and `airflow dags list-import-errors`; confirm imports and mounts |
| `No module named dotenv` | Declare `python-dotenv` in `requirements.txt` and rebuild the image |
| API returns an authentication error | Check `RAPIDAPI_KEY`, subscription access, endpoint, and the fixed host header |
| Extraction raises an index/type error | The code assumes a nonempty `results` list in every accepted response |
| UI cannot use port 8080 | Stop the existing local Airflow process or change Compose's host port mapping |
| Airflow is green but data is missing | Check Databricks credentials, warehouse permissions, and the loader's swallowed exceptions |
| Inserts fail after response fields change | Compare the existing table schema and column order with the DataFrame |

## Current limitations and next steps

This is a learning project with a local development deployment. The README is based on source inspection; startup and external API/warehouse execution have not been independently verified as part of this documentation update.

- Raise load exceptions so Airflow can report failures and apply retries.
- Add HTTP timeouts, retry/backoff handling, and validation for missing or empty API results. Non-200 responses are currently printed and skipped.
- Validate that the first search result matches the requested grocery item.
- Use explicit destination columns, typed schemas, and a deduplication strategy.
- Move larger task payloads to external storage and pass references through XCom.
- Pin application dependencies and add automated validation for the ETL behavior.
- Remove generated logs and runtime secrets from tracked configuration before sharing a deployment configuration. The checked-in configuration includes authentication secret values, and Compose supplies a default JWT secret.

## Author

**Aayush Kharel** — [GitHub](https://github.com/aayush8)
