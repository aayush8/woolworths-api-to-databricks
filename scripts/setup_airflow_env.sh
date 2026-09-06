# Source this file (do not execute it): source scripts/setup_airflow_env.sh
# Resolves paths from the script's own location, so it works from any cwd.
_SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
PROJECT_ROOT="$(dirname "$_SETUP_DIR")"

export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
echo "AIRFLOW_HOME is set to $AIRFLOW_HOME"

export AIRFLOW__CORE__DAGS_FOLDER="$PROJECT_ROOT/dags"
echo "DAGS_FOLDER is set to $AIRFLOW__CORE__DAGS_FOLDER"

# The DAG adds the project root to sys.path itself, but exporting it here also
# covers anything else run from this shell (airflow tasks test, python -c, etc).
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
echo "PYTHONPATH is set to $PYTHONPATH"

# macOS: the dag processor forks, and the system proxy lookup pulled in by
# requests crashes in the child ("+[NSNumber initialize] ... Crashing instead",
# SIGABRT). These two disable that crash path.
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export NO_PROXY="*"

unset _SETUP_DIR
