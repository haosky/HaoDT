# -*-coding:utf-8-*-
from __future__ import print_function
from builtins import range
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from com.pz.scheduler.build_quece import *

seven_days_ago = datetime.combine(
        datetime.today() - timedelta(7), datetime.min.time())
args = {
    'owner': 'airflow',
    'start_date': seven_days_ago,
    'end_date': datetime(2099, 1, 1),
    'depends_on_past': False,
    # 'email': ['airflow@airflow.com'],
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5), # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

'''队列任务'''
def weibo_queue_f(ds, **kwargs):
    weibo_queue()

def zhongxing_queue_f(ds, **kwargs):
    zhongxing_queue()

def baijia_queue_f(ds, **kwargs):
    baijia_queue()

def snowball_queue_f(ds, **kwargs):
    snowball_queue()

def toutiao_queue_f(ds, **kwargs):
    toutiao_queue()

def yidian_queue_f(ds, **kwargs):
    yidian_queue()

def bz_queue_f(ds, **kwargs):
    bz_queue()

def xunwei_queue_f(ds, **kwargs):
    xunwei_queue()

def networks_queue_f(ds, **kwargs):
    networks_queue()

def weixin_queue_f(ds, **kwargs):
    weixin_queue()

dag_weibo=DAG(
    dag_id='weibo_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

webi_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=weibo_queue_f,
    dag=dag_weibo)

#
dag_zhongxing=DAG(
    dag_id='zhongxing_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

zhongxing_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=zhongxing_queue_f,
    dag=dag_zhongxing)

#
dag_baijia=DAG(
    dag_id='baijia_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

baijia_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=baijia_queue_f,
    dag=dag_baijia)
#
dag_snowball=DAG(
    dag_id='snowball_queue',max_active_runs=1,
     default_args={
    'owner': 'airflow',
    'start_date': datetime.strptime('2016-06-27 04:00:00',"%Y-%m-%d %H:%M:%S"),
    'depends_on_past': False,
    'end_date': datetime(2099, 1, 1)
    },
    schedule_interval=timedelta(days=1)
)

snowball_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=snowball_queue_f,
    dag=dag_snowball)
#
dag_toutiao=DAG(
    dag_id='toutiao_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=1)
)

toutiao_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=toutiao_queue_f,
    dag=dag_toutiao)
#
dag_yidian=DAG(
    dag_id='yidian_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=1)
)

yidian_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=yidian_queue_f,
    dag=dag_yidian)
#
dag_bz=DAG(
    dag_id='bz_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

bz_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=bz_queue_f,
    dag=dag_bz)
#
dag_xunwei=DAG(
    dag_id='xunwei_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

xunwei_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=xunwei_queue_f,
    dag=dag_xunwei)
#
dag_networks=DAG(
    dag_id='networks_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=3)
)

networks_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=networks_queue_f,
    dag=dag_networks)
#
dag_weixin=DAG(
    dag_id='weixin_queue',max_active_runs=1,
     default_args=args,
    schedule_interval=timedelta(hours=4)
)

weixin_queue_task =PythonOperator(
    task_id='build',
    provide_context=True,
    python_callable=weixin_queue_f,
    dag=dag_weixin)