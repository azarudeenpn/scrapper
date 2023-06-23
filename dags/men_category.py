import datetime as dt
from airflow import DAG
from airflow.operators.python import PythonOperator

from zappos_scraper import ZapposScraper

default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2022, 8, 24, 10, 00, 00),
    'concurrency': 1,
    'retries': 0
}

scraper = ZapposScraper()

with DAG('get_category_men',
         default_args=default_args,
         schedule_interval='0 0 * * *',  # to run once daily
         ) as dag:
    opr_men = PythonOperator(task_id='category_men',
                             python_callable=scraper.get_men_category)
    opr_women = PythonOperator(task_id='category_women',
                               python_callable=scraper.get_women_category)
    opr_men_shoes = PythonOperator(task_id='men_shoes',
                                   python_callable=scraper.get_men_shoes)
    opr_women_shoes = PythonOperator(task_id='women_shoes',
                                     python_callable=scraper.get_women_shoes)
    opr_men >> opr_women >> [opr_men_shoes, opr_women_shoes]  # to run tasks in parallel
