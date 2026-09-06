#First activate the virtual environment
source .venv/bin/activate

export AIRFLOW_HOME="$(pwd)/airflow_home"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/dags"

cat airflow_home/simple_auth_manager_passwords.json.generated \
    | jq -r ".admin" \
    | pbcopy

airflow standalone


