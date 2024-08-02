from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Definir algunos parámetros básicos del DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 6, 22),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "dbt_dag",
    default_args=default_args,
    description="A simple DAG to run dbt commands",
    schedule_interval=timedelta(days=1),
)

# Definir el BashOperator para ejecutar dbt run
dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command="docker exec -it dbt-dbt-1 dbt run",
    dag=dag,
)

# Puedes añadir más tareas para diferentes comandos de dbt
dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command="docker exec -it dbt-dbt-1 dbt test",
    dag=dag,
)

dbt_run >> dbt_test
