#coding:utf-8
# write  by  zhou
import urllib
import  json
import  urllib2
from celery import  Celery
import redis
import time

_app = None
_redis_conn = redis.Redis('192.168.8.185',6379,6)


def data_to_online(dataset,key,data):
    '''
    数据转移到线上
    :param dataset: 数据集的名称，str, 如： hy88_product
    :param key:     数据的key， str,  如：http://www.huangye88.com/xinxi/11.html
    :param data:    数据的内容， dict 如: {"cate1":11,"cate2":111,"url":"xxxxx"}
    :return:
    True
    '''
    global  _app
    if _app == None:
        #
        _app = Celery()
        _app.conf.task_ignore_result = True
        _app.conf.task_queue_max_priority = 255
    while 1:
        if _redis_conn.llen("rawhttp.data_transfer") > 40000:
            time.sleep(1)
        else:
            break
    _app.send_task("rawhttp.data_transfer.transfer", kwargs={"dataset": dataset,
                                                            "key": key,
                                                            "data": data,
                                                            "http_proxy": ["192.168.14.%s:3128"%i for \
                                                                           i in range(120,131)]},
                  queue="rawhttp.data_transfer")
    return True
