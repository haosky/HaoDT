# -*-coding:utf-8-*-
from __future__ import print_function
from airflow.operators import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
# from  com.pz.scheduler.build_quece import sche_queue
# from com.pz.scheduler.zhishu import  put_zhishu
from com.pz.scheduler.zhishu_30day import  zhishu30day
from com.pz.scheduler.zhishuCheck import  run_check_baidu,run_check_data_360,run_check_sina,run_check_youku
import time
from pprint import pprint
from  com.pz.scheduler.company_time_event import sche_company,eval_company
from com.pz.mrtasks.mrschedulerbase import mrschedulerbase
from com.pz.scheduler.index_day_report import doit
from com.pz.storecenter.hbasecenter.count_title_art import count_title_art
from com.pz.scheduler.emoTagsDayCount import emoTagsDayCount
from com.pz.scheduler.zhishu_tools import  zhishu_tools
from com.pz.scheduler.bz_day_report import main
import logging
import calendar
yesday = datetime.combine(
        datetime.today()-timedelta(days=1), datetime.min.time())
today = datetime.combine(
        datetime.today(), datetime.min.time())
lastFriday = datetime.combine( datetime.today(), datetime.min.time())
oneday = timedelta(days = 1)

while lastFriday.weekday() != calendar.FRIDAY:
    lastFriday -= oneday
# sd=lastFriday+timedelta(hours=17.5)
# print(sd.strftime("%Y-%m-%d %H:%M:%S")  )
# args = {
#     'owner': 'airflow',
#     'start_date': seven_days_ago,
#     'depends_on_past': False,
#     # 'email': ['airflow@airflow.com'],
#     # 'email_on_failure': False,
#     # 'email_on_retry': False,
#     # #'retries': 1,
#     # 'retry_delay': timedelta(minutes=5), # 'queue': 'bash_queue',
#     # 'pool': 'backfill',
#     # 'priority_weight': 10,
#     #'end_date': datetime(2099, 1, 1),
#
# }
def recrawler_queue(ds, **kwargs):
    eval_company()


def timer_build(ds, **kwargs):
    sche_company()


dag_queue = DAG(
    dag_id='company_recrawler',
    default_args={
    'owner': 'root',
    'start_date':datetime.now()-timedelta(minutes=31),
    # datetime.strptime('2016-06-30 13:08:00','%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    },
    max_active_runs=1,
    #define a schedule_interval of 30 minutes for the DAG
    schedule_interval=timedelta(minutes=30)
    )

dag_comptimer = DAG(
    dag_id='company_timer',
    default_args={
    'owner': 'root',
    'start_date':datetime.now()-timedelta(minutes=11),
    'depends_on_past': False,
    },
    max_active_runs=1,
    schedule_interval=timedelta(minutes=10))

run_queue = PythonOperator(
    task_id='queue',
    provide_context=True,
    python_callable=recrawler_queue,
    dag=dag_queue)

run_timer = PythonOperator(
    task_id='timer',
    provide_context=True,
    python_callable=timer_build,
    dag=dag_comptimer)

# '''构建爬取队列'''
# def sche_queue_dag(ds, **kwargs):
#     sche_queue()
#
#
# run_sche_queue_dag = DAG(
#     dag_id='sche_queue', default_args=args,max_active_runs=1,
#     schedule_interval=timedelta(minutes=10))
#
# run_sche_queue = PythonOperator(
#     task_id='queue',
#     provide_context=True,
#     python_callable=sche_queue_dag,
#     dag=run_sche_queue_dag)

# '''30天其他指数爬取'''
# def put_zhishu30day_others_dag(ds, **kwargs):
#     zhishu30day().request_index()
# 
# 
# run_put_zhishu30day_others_dag= DAG(
#     dag_id='others_zhishu30day',
#     default_args={
#     'owner': 'root',
#     'start_date':datetime.now()-timedelta(minutes=42),
#     'depends_on_past': False,
#     },
#     max_active_runs=1,
#     schedule_interval='*/40 * * * *')
# 
# run_put_zhishu30day_others = PythonOperator(
#     task_id='put_others',
#     provide_context=True,
#     python_callable=put_zhishu30day_others_dag,
#     dag=run_put_zhishu30day_others_dag)

#['data_360', 'sina','youku' ]
'''30天data_360指数爬取'''
def put_zhishu30day_360_dag(ds, **kwargs):
    # zhishu30day().request_index(indexName='data_360')
    run_check_data_360()
    return 'finish'


run_put_zhishu30day_360_dag= DAG(
    dag_id='data360_zhishu30day',
    default_args={
    'owner': 'root',
    'start_date':datetime.strptime('2017-02-08 12:50:00','%Y-%m-%d %H:%M:%S') ,
    'depends_on_past': False,
    #'retries': 0,
    },
    max_active_runs=2,
    schedule_interval='*/20 * * * *')
    # schedule_interval=timedelta(hours=2)


run_put_zhishu30day_360 = PythonOperator(
    task_id='put_others',
    provide_context=True,
    python_callable=put_zhishu30day_360_dag,
    dag=run_put_zhishu30day_360_dag)

'''30天data_sina指数爬取'''
def put_zhishu30day_sina_dag(ds, **kwargs):
    run_check_sina()
    return 'finish'


run_put_zhishu30day_sina_dag= DAG(
    dag_id='sina_zhishu30day',
    default_args={
    'owner': 'root',
    'start_date':datetime.strptime('2017-02-08 12:30:00','%Y-%m-%d %H:%M:%S'),  #datetime.now(),#-timedelta(minutes=371), #datetime.now(),#-timedelta(minutes=70),
    'depends_on_past': False,
    },
    max_active_runs=2,
    # schedule_interval=timedelta(hours=2))
    schedule_interval='*/20 * * * *')

run_put_zhishu30day_sina = PythonOperator(
    task_id='put_others',
    provide_context=True,
    python_callable=put_zhishu30day_sina_dag,
    dag=run_put_zhishu30day_sina_dag)


'''30天data_youku指数爬取'''
def put_zhishu30day_youku_dag(ds, **kwargs):
    run_check_youku()
    return 'finish'


run_put_zhishu30day_youku_dag= DAG(
    dag_id='youku_zhishu30day',
    default_args={
    'owner': 'root',
    'start_date':datetime.strptime('2017-02-08 12:10:00','%Y-%m-%d %H:%M:%S'), #-timedelta(minutes=351), #datetime.now(),#-timedelta(minutes=60),
    'depends_on_past': False,
    #'retries': 0,
    },
    max_active_runs=2,
    schedule_interval='*/20 * * * *')
    # schedule_interval=timedelta(hours=2))

run_put_zhishu30day_youku = PythonOperator(
    task_id='put_others',
    provide_context=True,
    python_callable=put_zhishu30day_youku_dag,
    dag=run_put_zhishu30day_youku_dag)

'''30天百度指数爬取'''
def put_zhishu30day_baidu_dag(ds, **kwargs) :
     # zhishu30day().request_baidu()
     run_check_baidu()
     return 'finish'


run_put_zhishu30day_baidu_dag = DAG(
    dag_id='baidu_zhishu30day',
    default_args={
    'owner': 'root',
    'start_date':datetime.strptime('2017-02-08 14:00:00','%Y-%m-%d %H:%M:%S'),#-timedelta(minutes=341), #datetime.now(),#-timedelta(minutes=142),
    'depends_on_past': False,
    #'retries': 0,
    },
    max_active_runs=1,
    schedule_interval='*/20 * * * *')
    # schedule_interval=timedelta(hours=2))

run_put_zhishu30day_baidu = PythonOperator(
    task_id='put_baidu',
    provide_context=True,
    python_callable=put_zhishu30day_baidu_dag,
    dag=run_put_zhishu30day_baidu_dag)
#
'''转发概率MR运行'''
def reportRate_runmr(ds, **kwargs):
     mr= mrschedulerbase()
     # da=datetime.today() - timedelta(1)
     mr.execreportrate_mr(ds.replace('-',''))
     return 'finish'

dag_reportRate_runmr_dag=DAG(
    dag_id='reportRate_MR', default_args={
    'owner': 'airflow',
    # 'start_date': yesday+timedelta(hours=4.5),
    'start_date':datetime.strptime('%s 04:09:00' % (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
    },max_active_runs=1,
    # schedule_interval=timedelta(days=1)
    schedule_interval='10 4 * * *'
)

report_task =PythonOperator(
    task_id='reportRate_task',
    provide_context=True,
    python_callable=reportRate_runmr,
    dag=dag_reportRate_runmr_dag)

'''指数监控'''
def reportindex_mon(ds, **kwargs):
    doit()
    return 'finish'

dag_reportindex_mon_dag=DAG(
     dag_id='IndexAlert',
     default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('%s 07:09:00' % (datetime.now().strftime('%Y-%m-%d')) ,'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
    },
    max_active_runs=1,
    schedule_interval='10 7 * * *'
)

reportindex_alert_task =PythonOperator(
    task_id='alert_task',
    provide_context=True,
    python_callable=reportindex_mon,
    dag=dag_reportindex_mon_dag)

'''标题出现次数统计前10条'''
def art_title_count(ds, **kwargs):
    count_title_art().app_title()
    return 'finish'

art_title_count_dag=DAG(
     dag_id='art_title_count',
     default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('%s 01:29:00' %  (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
    },
    max_active_runs=1,
    schedule_interval='30 1 * * *'
)

art_title_count_task =PythonOperator(
    task_id='count_task',
    provide_context=True,
    python_callable=art_title_count,
    dag=art_title_count_dag)

def emoTagsDayCount_task(ds, **kwargs):
    emoTagsDayCount().count(ds)
    return 'finish'

emoTagsDayCount_dag=DAG(
 dag_id='emoTagsDayCount',
 default_args={
'owner': 'airflow',
'start_date':datetime.strptime('%s 03:29:00' %  (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
'depends_on_past': False,
# #'end_date': datetime(2099, 1, 1)
},
max_active_runs=1,
schedule_interval='30 3 * * *'
)

emoTagsDayCount_job =PythonOperator(
    task_id='count_task',
    provide_context=True,
    python_callable=emoTagsDayCount_task,
    dag=emoTagsDayCount_dag)


'''指数导入'''

def index_upload_task(ds, **kwargs):
    zhishu_tools().upload_pop_queue()
    return 'finish'

indext_upload_tag=DAG(
 dag_id='index_upload',
 default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('%s:20:00' %  (datetime.now().strftime('%Y-%m-%d %H')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
 },
 max_active_runs=8,
 schedule_interval='*/5 * * * *'
 )

indext_upload_job =PythonOperator(
    task_id='upload',
    provide_context=True,
    python_callable=index_upload_task,
    dag=indext_upload_tag
)

'''报纸检查'''

def bz_check_task(ds, **kwargs):
    main()
    return 'finish'

check_bz_tag=DAG(
 dag_id='bz_check',
 default_args={
    'owner': 'airflow',
    'start_date':datetime.strptime('%s 03:09:00' % (datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d %H:%M:%S')-timedelta(days=1),
    'depends_on_past': False,
    # #'end_date': datetime(2099, 1, 1)
 },
 max_active_runs=1,
 schedule_interval='10 3 * * *'
 )

check_bz_job =PythonOperator(
    task_id='check',
    provide_context=True,
    python_callable=bz_check_task,
    dag=check_bz_tag
)
#
# '''test'''
# def test(ds, **kwargs):
#    for i in range(0,100000) :
#       pprint(kwargs)
#       logging.info(ds)
#       logging.info('-------')
#       time.sleep(3)
#
# t2_dag=DAG(
#     dag_id='sdfsdfs', default_args={
#     'owner': 'airflow',
#     'start_date':  yesday+timedelta(hours=10.6),
#     'depends_on_past': False,
#     #'end_date': datetime(2099, 1, 1)
#     },max_active_runs=1,
#     schedule_interval=timedelta(days=1)
# )
#
# t3t =PythonOperator(
#     task_id='ss',
#     provide_context=True,
#     python_callable=test,
#     dag=t2_dag)
#



