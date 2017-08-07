# -*-coding:utf-8-*-
from __future__ import print_function
from builtins import range
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from devops.ops_day_count import day_count
from devops.ops_week_count import week_count
from devops.reportRate_medias import day_count as reportdate_count
from com.pz.scheduler.hivehealth import hivehealth
import calendar
yesday = datetime.combine(
        datetime.today()-timedelta(days=1), datetime.min.time())
today = datetime.combine(
        datetime.today(), datetime.min.time())
lastFriday = datetime.combine( datetime.today(), datetime.min.time())
oneday = timedelta(days = 1)

while lastFriday.weekday() != calendar.FRIDAY:
    lastFriday -= oneday


'''周统计邮件'''

def week_count_air(ds, **kwargs):
    week_count()

week_count_dag= DAG(
    dag_id='week_count',
    default_args={
        'owner': 'root',
        'start_date':datetime.strptime('%s 17:30:00' % (datetime.now().strftime('%Y-%m-%d')) ,'%Y-%m-%d %H:%M:%S')-timedelta(days=7),
        'depends_on_past': False,
    }
    ,max_active_runs= 1,
    schedule_interval='30 17 * * 5')

run_week_count_dag =PythonOperator(
    task_id='week_count_task',
    provide_context=True,
    python_callable=week_count_air,
    dag=week_count_dag)

'''日统计邮件'''

def day_count_air(ds, **kwargs):
    day_count(ds)
    return 'finish'

day_count_day= DAG(
    dag_id='day_count', default_args={
    'owner': 'root',
    # 'start_date':yesday+timedelta(hours=6),
    'start_date':datetime.strptime('%s 06:30:00' % (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    },max_active_runs=1,
    schedule_interval='30 6 * * *')

run_day_count_dag =PythonOperator(
    task_id='day_count_task',
    provide_context=True,
    python_callable=day_count_air,
    dag=day_count_day)


'''转发概率媒体报告'''
def reportRate_count(ds, **kwargs):
    reportdate_count(ds)
    return 'finish'

dag_reportRate_count_dag=DAG(
    dag_id='reportRate_medias_count', default_args={
    'owner': 'airflow',
    # 'start_date':  yesday+timedelta(hours=6),
    'start_date':datetime.strptime('%s 05:05:00' % (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    'end_date': datetime(2099, 1, 1)
    },max_active_runs=1,
    # schedule_interval=timedelta(days=1)
    schedule_interval='05 5 * * *'
)

report_count_task =PythonOperator(
    task_id='count_task',
    provide_context=True,
    python_callable=reportRate_count,
    dag=dag_reportRate_count_dag)


'''重启hiveserver'''
def hive_restart(ds, **kwargs):
    hivehealth()
    return 'finish'

dag_hivesrestart_count_dag=DAG(
    dag_id='hivestart', default_args={
    'owner': 'airflow',
    # 'start_date':  yesday+timedelta(hours=6),
    'start_date':datetime.now(),
    'depends_on_past': False,
    'end_date': datetime(2099, 1, 1)
    },max_active_runs=1,
    # schedule_interval=timedelta(days=1)
    schedule_interval=None
)

hivesrestart_task =PythonOperator(
    task_id='hivesrestart',
    provide_context=True,
    python_callable=hive_restart,
    dag=dag_hivesrestart_count_dag)
