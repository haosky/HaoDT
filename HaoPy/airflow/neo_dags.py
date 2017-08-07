# -*-coding:utf-8-*-
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from neodev.programs.statistics_keywords import   statistics as sk_dayjob
from neodev.programs.statistics_negative_keywords import  statistics as  snkw_dayjob
from neodev.programs.statistics_rank import  statistics as  sr_dayjob
from neodev.programs.statistics_relation import  statistics as  sr2_dayjob

# from neodev2.programs.statistics_keywords import   sk_dayjob as sk_dayjob_2
# from neodev2.programs.statistics_negative_keywords import   snkw_dayjob as snkw_dayjob_2
# from neodev2.programs.statistics_rank import   sr_dayjob as sr_dayjob_2


'''statistics_negative_keywords'''
def snk_dag_cb(ds, **kwargs):
    # sk_dayjob_2().main(ds)
    snkw_dayjob().main(ds)


run_snk_dag= DAG(
    dag_id='statistics_negative_keywords_day',
    default_args={
    'owner': 'root',
    # 'start_date':datetime.now()-timedelta(days=1),
    'start_date':datetime.strptime('2017-02-07 00:00:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },
    max_active_runs=1,
    schedule_interval='10 1 * * *')

snk_day_job = PythonOperator(
    task_id='snk_day_job',
    provide_context=True,
    python_callable=snk_dag_cb,
    dag=run_snk_dag)

'''statistics_keywords'''
def snkw_dag_cb(ds, **kwargs):
    # snkw_dayjob_2().main(ds)
    sk_dayjob().main(ds)

run_snkw_dag= DAG(
    dag_id='statistics_keywords_day',
    default_args={
    'owner': 'root',
    # 'start_date':datetime.now()-timedelta(days=1),
    'start_date':datetime.strptime('2017-02-07 00:00:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },
    max_active_runs=1,
    schedule_interval='40 1 * * *')

snkw_dag_job = PythonOperator(
    task_id='put_others',
    provide_context=True,
    python_callable=snkw_dag_cb,
    dag=run_snkw_dag)

'''statistics_rank'''
def sr_dag_cb(ds, **kwargs):
    # sr_dayjob_2().main(ds)
    sr_dayjob().main(ds)

sr_dag= DAG(
    dag_id='statistics_rank_day',
    default_args={
    'owner': 'root',
    # 'start_date':datetime.now()-timedelta(days=1),
    'start_date':datetime.strptime('2017-02-07 00:00:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },
    max_active_runs=1,
    schedule_interval='10 2 * * *')

sr_dag_job = PythonOperator(
    task_id='put_others',
    provide_context=True,
    python_callable=sr_dag_cb,
    dag=sr_dag)


# '''statistics_relation'''
# def sr2_dag_cb(ds, **kwargs):
#     # sr_dayjob_2().main(ds)
#     sr2_dayjob().main(ds)
#
# sr2_dag= DAG(
#     dag_id='statistics_relation_day',
#     default_args={
#     'owner': 'root',
#     # 'start_date':datetime.now()-timedelta(days=1),
#     'start_date':datetime.strptime('2016-10-23 00:00:00','%Y-%m-%d %H:%M:%S'),
#     'depends_on_past': False,
#     },
#     max_active_runs=1,
#     schedule_interval='30 2 * * *')
#
# srrelation_dayjob = PythonOperator(
#     task_id='put_others',
#     provide_context=True,
#     python_callable=sr2_dag_cb,
#     dag=sr2_dag)
