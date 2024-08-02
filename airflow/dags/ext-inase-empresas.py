import sys
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

# Añadir el directorio 'scripts' al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

# Importar funciones desde scripts
from scripts.scrape_data import scrape_data
from scripts.upload_to_drive import upload_to_drive

default_args = {
    "owner": "Data",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

dag = DAG(
    "upload_csv_to_drive",
    default_args=default_args,
    description="Generate CSV and upload to Google Drive",
    schedule_interval=None,
)

start_task = DummyOperator(
    task_id="start",
    dag=dag,
)

scrape_task = PythonOperator(
    task_id="scrape_data",
    python_callable=scrape_data,
    op_kwargs={
        "url": "https://gestion.inase.gob.ar/empresas/empresas",
    },
    provide_context=True,
    dag=dag,
)

upload_task = PythonOperator(
    task_id="upload_to_drive",
    python_callable=upload_to_drive,
    op_kwargs={
        "temp_csv_path": "{{ ti.xcom_pull(task_ids='scrape_data', key='temp_csv_path') }}",
        "creds_json": Variable.get("google_drive_creds"),
        "folder_id": Variable.get("inase_empresas_drive_id"),
        "file_metadata": {"name": "inase_empresas.csv"},
    },
    provide_context=True,
    dag=dag,
)

end_task = DummyOperator(
    task_id="end",
    dag=dag,
)

start_task >> scrape_task >> upload_task >> end_task
