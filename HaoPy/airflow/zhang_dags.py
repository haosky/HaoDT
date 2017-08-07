# -*-coding:utf-8-*-
from com.pz.scheduler.process import  statisDay
from com.pz.scheduler.process import  statisMins
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta

'''张正'''
def f_statisDay(ds, **kwargs):
    statisDay.my_job()
    return 'finish'

dag_statisDay=DAG(
    dag_id='statisDay', default_args={
    'owner': 'airflow',
    # 'start_date': yesday+timedelta(hours=23.9),
    'start_date':datetime.strptime('2017-02-07 23:59:00','%Y-%m-%d %H:%M:%S') ,
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
    },max_active_runs=1,
    schedule_interval='59 23 * * *'
)

run_statisDay_dag =PythonOperator(
    task_id='queue',
    provide_context=True,
    python_callable=f_statisDay,
    dag=dag_statisDay)

def f_statisMins_day(ds, **kwargs):
    statisMins.day_job()
    return 'finish'

dag_statisDay_day=DAG(
    dag_id='statisMins_day', default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-07 23:59:00' ,'%Y-%m-%d %H:%M:%S') ,
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
    },max_active_runs=1,
    schedule_interval='59 23 * * *'
)

run_statisMins_day =PythonOperator(
    task_id='day_job',
    provide_context=True,
    python_callable=f_statisMins_day,
    dag=dag_statisDay_day)

def f_statisMins_minutes(ds, **kwargs):
    statisMins.min_job()
    return 'finish'

dag_statisDay_min_dags=DAG(
    dag_id='statisMins_minutes',
    default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 13:50:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },max_active_runs=3,
    # schedule_interval='*/5 * * * *', #timedelta(minutes=5)
    schedule_interval='*/5 * * * *'
)

run_statisMinss_min =PythonOperator(
    task_id='min_job',
    provide_context=True,
    python_callable=f_statisMins_minutes,
    dag=dag_statisDay_min_dags)