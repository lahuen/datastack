import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from scripts.upload_to_drive import upload_to_drive

default_args = {
    "owner": "Data",
    "start_date": "2024-08-01",
    "schedule_interval": "@weekly",
    "depends_on_past": False,
    "retries": 1,
}

dag = DAG(
    "catalogo_upload_csv_to_drive",
    default_args=default_args,
    description="Download CSV and upload to Google Drive",
    schedule_interval=None,
)

start_task = DummyOperator(
    task_id="start",
    dag=dag,
)

download_task = BashOperator(
    task_id="scrape_data",
    bash_command='curl -s -o /tmp/inase_catalogo.csv "https://gestion.inase.gob.ar/registroCultivares/publico/catalogo/downloadcsv/%7B%7D/e73u4wx7p" && echo "/tmp/inase_catalogo.csv"',
    do_xcom_push=True,
    dag=dag,
)

upload_task = PythonOperator(
    task_id="upload_to_drive",
    python_callable=upload_to_drive,
    op_kwargs={
        "temp_csv_path": "{{ ti.xcom_pull(task_ids='scrape_data', key='return_value') }}",
        "creds_json": Variable.get("google_drive_creds"),
        "folder_id": Variable.get("inase_catalogo_drive_id"),
        "file_metadata": {"name": "inase_catalogo.csv"},
    },
    provide_context=True,
    dag=dag,
)

end_task = DummyOperator(
    task_id="end",
    dag=dag,
)

start_task >> download_task >> upload_task >> end_task
