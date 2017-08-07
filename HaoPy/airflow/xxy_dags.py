# -*-coding:utf-8-*-
from xxy_scheduler.xxysearch_so_url import run_so_url
from xxy_scheduler.search_list_spout import search_list_spout
from xxy_scheduler.weibo_mid_kafka_product import weibo_mid_kafka_product
from xxy_scheduler.toutiao_kw_scheduler import toutiaokw_url_bolt
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta



def run_so_url2kafka(ds, **kwargs):
    run_so_url()
    return 'finish'

run_so_url2kafka_dags=DAG(
    dag_id='so_url2kafka',
    default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 10:40:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },max_active_runs=1,
    # schedule_interval='*/5 * * * *', #timedelta(minutes=5)
    schedule_interval='50 */2 * * *'
)

run_statisMinss_min =PythonOperator(
    task_id='so_url2kafka',
    provide_context=True,
    python_callable=run_so_url2kafka,
    dag=run_so_url2kafka_dags)

# 微博授权媒体
def weibo_teams_mid_2_kafka(ds, **kwargs):
    weibo_mid_kafka_product().run()
    return 'finish'

run_weibo_teams_mid_2_kafka_dags=DAG(
    dag_id='weibo_teams_mid_kafka',
    default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 06:20:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },max_active_runs=1,
    # schedule_interval='*/5 * * * *', #timedelta(minutes=5)
    schedule_interval='20 * * * *'
)

run_weibo_teams_mid_2_kafka =PythonOperator(
    task_id='weibo_teams_mid_2_kafka_dags',
    provide_context=True,
    python_callable=weibo_teams_mid_2_kafka,
    dag=run_weibo_teams_mid_2_kafka_dags)

# 头条抓取调度
def toutiao_url_scheduer(ds, **kwargs):
    tk = toutiaokw_url_bolt()
    tk.run()
    return 'finish'

run_toutiao_url_scheduer_dags=DAG(
    dag_id='toutiao_url_scheduler',
    default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 08:40:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },max_active_runs=1,
    # schedule_interval='*/5 * * * *', #timedelta(minutes=5)
    schedule_interval='40 */4 * * *'
)

run_toutiao_url_scheduer =PythonOperator(
    task_id='toutiao_url_scheduer',
    provide_context=True,
    python_callable=toutiao_url_scheduer,
    dag=run_toutiao_url_scheduer_dags)

# url列表抓取
def search_list_spout_dz(ds, **kwargs):
    search_list_spout().run()
    return 'finish'

run_search_list_spout_dags=DAG(
    dag_id='search_list_spout',
    default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('2017-02-08 10:30:00','%Y-%m-%d %H:%M:%S'),
    'depends_on_past': False,
    },max_active_runs=1,
    # schedule_interval='*/5 * * * *', #timedelta(minutes=5)
    schedule_interval='30 */2 * * *'
)

run_search_list_spout =PythonOperator(
    task_id='search_list_spout',
    provide_context=True,
    python_callable=search_list_spout_dz,
    dag=run_search_list_spout_dags)