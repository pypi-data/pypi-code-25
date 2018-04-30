# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import AD_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + AD_DB_FILE_PATH, echo=True)
AdModelBase = declarative_base()


# 广告
class Ad(AdModelBase):
    __tablename__ = 'ad'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    name = Column(String(40), default="", nullable=False)  # 广告名称
    image = Column(String(300), default="", nullable=False)  # 广告图片
    link = Column(String(300), default="", nullable=False)  # 跳转链接
    is_enable = Column(Boolean, default=False, nullable=False, index=True)  # 是否有效
    click_count = Column(Integer)  # 点击次数
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<Ad(name='%s')>" % (self.name)


# 初始化数据引擎
AdModelBase.metadata.create_all(engine)
AdModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
