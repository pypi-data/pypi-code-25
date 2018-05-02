# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import APP_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + APP_DB_FILE_PATH, echo=True)
AppModelBase = declarative_base()


# 应用
class App(AppModelBase):
    __tablename__ = 'app'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    name = Column(String(30), default="", nullable=False, index=True)  # 应用名称
    file_path = Column(String(50), default="", nullable=False)  # 文件路径
    file_name = Column(String(50), default="", nullable=False)  # 文件名称
    log_file = Column(String(50), default="", nullable=False)  # 日志文件
    boot_cmd = Column(String(300), default="", nullable=False)  # 启动命令
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<App(name='%s')>" % (self.name)


# 初始化数据引擎
AppModelBase.metadata.create_all(engine)
AppModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
