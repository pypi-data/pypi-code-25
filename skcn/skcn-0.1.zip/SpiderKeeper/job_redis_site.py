#!/usr/bin/env python
#coding=utf-8

import time
import datetime
import re
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler,BlockingScheduler
import redis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from SpiderKeeper.app import db, api, agent, app
from SpiderKeeper.app.spider.model import JobInstance, Project, JobExecution, SpiderInstance, JobRunType
from sqlalchemy import create_engine
from SpiderKeeper import config
class SetCount(object):
    def __init__(self):
        self.db = redis.StrictRedis.from_url ("redis://172.16.1.147/14")
        # SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
        self.engine = create_engine (config.SQLALCHEMY_DATABASE_URI, echo=False)
        # # 如果没有数据库链接，可以这样创建session
        self.Session = sessionmaker ()
        # 当后来由数据库链接后可以这样绑定
        self.Session.configure (bind=self.engine)
        self.session = self.Session ()

    def sqlite_find(self):
        dict_spider_count = dict ()
        for job_instance in JobInstance.query.filter_by (run_type="periodic").all ():
            # for job_instance in self.session.query (JobInstance).all ():
            print job_instance.id
            dict_spider_count ={
                "spidername":job_instance.spider_name,
                # "spidercount":job_Instance.COUNT
            }
            # print dict_spider_count

        return dict_spider_count

    def sqlite_update(self,k,n):

        job_Instance = self.session.query(JobInstance).filter_by (run_type="periodic",spider_name = k).first ()  # 查找
        job_Instance.COUNT = n
        self.session.commit()
        return dict_spider_count

    def redis_find(self,k):
        n = 0
        if k:
            try:
                n = self.db.llen(k)
            except:
                pass
        return n

    def _endfuction(self):
        self.session.close()

if __name__ == "__main__":
    while(True):
        sc = SetCount()
        dict_spider_count = sc.sqlite_find()
        for k in dict_spider_count:
            values=  dict_spider_count[k]
            n = sc.redis_find(dict_spider_count[k])
            sc.sqlite_update(values,n)
        sc._endfuction()
        time.sleep(5)





















    # Define apscheduler
    # scheduler = BlockingScheduler()
    #
    # scheduler.add_job(redis_find, 'interval', seconds=3)
    #
    # scheduler.start()
    #
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))


# def test_job():
#     print time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (time.time ()))
#
# scheduler = BlockingScheduler ()
# '''
# # 该示例代码生成了一个BlockingScheduler调度器，使用了默认的默认的任务存储MemoryJobStore，以及默认的执行器ThreadPoolExecutor，并且最大线程数为10。
# '''
# scheduler.add_job (test_job, 'interval', seconds = 5, id ='test_job')
# '''
# # 该示例中的定时任务采用固定时间间隔（interval）的方式，每隔5秒钟执行一次。
# # 并且还为该任务设置了一个任务id
# '''
# scheduler.start ()