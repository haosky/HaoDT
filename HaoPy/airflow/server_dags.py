# -*-coding:utf-8-*-
from __future__ import print_function
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime,timedelta
from com.pz.scheduler.hivehealth import hivehealth
# import calendar
yesday = datetime.combine(
        datetime.today()-timedelta(days=1), datetime.min.time())
# from devops.weibo_user_info import weibo_user_info
'''重启hiveserver'''
def hive_restart(ds, **kwargs):
    hivehealth()

dag_hivesrestart_count_dag=DAG(
    dag_id='hivestart', default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 20:03:00','%Y-%m-%d %H:%M:%S'),
    # 'start_date':datetime.now(),
    'depends_on_past': False,
    'end_date': datetime(2016, 10, 27)
    },max_active_runs=1,
    # schedule_interval=timedelta(days=1)
     schedule_interval='20 3 * * *'
)

hivesrestart_task =PythonOperator(
    task_id='hivesrestart',
    provide_context=True,
    python_callable=hive_restart,
    dag=dag_hivesrestart_count_dag)

# '''内网跑微博'''
# def weibo_follow(ds, **kwargs):
#     #weibo_user_info().main()
#     return 'finish'
#
# dag_wb_follow_dag=DAG(
#     dag_id='weibo', default_args={
#     'owner': 'airflow',
#     'start_date':datetime.strptime('2016-11-09 17:00:00','%Y-%m-%d %H:%M:%S'),
#     # 'start_date':datetime.now(),
#     'depends_on_past': False,
#     'end_date': datetime(2099, 1, 1)
#     },max_active_runs=1,
#     # schedule_interval=timedelta(days=1)
#      schedule_interval='00 17 * * *'
# )
#
# hivesrestart_task =PythonOperator(
#     task_id='wfollow',
#     provide_context=True,
#     python_callable=weibo_follow,
#     dag=dag_wb_follow_dag)
