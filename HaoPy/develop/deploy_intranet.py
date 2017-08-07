# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.context_managers import *

__author__ = 'hao'


#指定需要部署的机器

# env.host_string = "gx.master"
env.host_string = "192.168.1.122"

#指定部署机器的用户
env.user = "root"
#指定部署的机器的path
dist_dir = "/extDisk/work"

#指定启动的入口
# run_py = "gxthrift/eshandler/services/search_data_for_keyword.py"

def depoly_storm_repeat_depy():
    with cd(dist_dir):
        run("rm -rf /root/work/HaoPy/*")
        curr_dir = 'D:\\workspace\\java_project\\Integration\\HaoPy'
        put(curr_dir,dist_dir)
        run("ls /root/work/HaoPy/")
        open_shell('''
        cd /root/work/HaoPy/haostorm/;
        pyleus -v build check_repeat.yaml;
        pyleus -v submit -n 192.168.1.122 ./check_repeat.jar;
        exit;
        ''')

def depoly_storm_repeat_task_depy():
    with cd(dist_dir):
        run("rm -rf /root/work/HaoPy/*")
        curr_dir = 'D:\\workspace\\java_project\\Integration\\HaoPy'
        put(curr_dir,dist_dir)
        run("ls /root/work/HaoPy/")
        open_shell('''
        cd /root/work/HaoPy/haostorm/;
        pyleus -v build check_repeat_task.yaml;
        pyleus -v submit -n 192.168.1.122 ./check_repeat_task.jar;
        exit;
        ''')

def deploy_put():
    with cd(dist_dir):
        run("rm -rf /extDisk/work/HaoPy/*")
        curr_dir = 'D:\\workspace\\java_project\\Integration\\HaoPy'
        put(curr_dir,dist_dir)
        run("ls /extDisk/work/HaoPy/")

def deploy_putt():
    with cd(dist_dir):
        curr_dir = 'D:\\workspace\\java_project\\Integration\\HaoPy\\sources'
        put(curr_dir,'/extDisk/work/HaoPy/')
        run("ls /extDisk/work/HaoPy/")

if __name__ == "__main__":
    # 离线任务
    # depoly_storm_repeat_task_depy()
    # 实时任务
    # depoly_storm_repeat_depy()
    deploy_put()