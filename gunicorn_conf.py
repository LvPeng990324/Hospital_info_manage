# 部署时候把注释的路径切换下
import multiprocessing

bind = "127.0.0.1:8080"
workers = multiprocessing.cpu_count() * 2 + 1
reload = True
daemon = True
errorlog = '/Hospital_info_manage/logs/gunicorn_error.log'
proc_name = 'gunicorn_Hospital_info_manage_project'
