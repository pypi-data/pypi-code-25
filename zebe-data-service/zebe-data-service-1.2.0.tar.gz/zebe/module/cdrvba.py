# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import CDRVBA_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + CDRVBA_DB_FILE_PATH, echo=True)
CorelDrawVBASubscriberModelBase = declarative_base()


# CorelDRAW VBA订阅用户
class CorelDrawVBASubscriber(CorelDrawVBASubscriberModelBase):
    __tablename__ = 'subscriber'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    name = Column(String(20), default="", nullable=False)  # 姓名
    email = Column(String(30), default="", nullable=False, index=True)  # 邮箱
    wechat = Column(String(25), default="", nullable=False)  # 微信
    qq = Column(String(30), default="", nullable=False)  # QQ
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<CorelDrawVBASubscriber(name='%s')>" % (self.name)


# CorelDRAW VBA文章
class CorelDrawVBAArticle(CorelDrawVBASubscriberModelBase):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    content = Column(Text, default="", nullable=False)  # 内容
    type = Column(String(10), default="", nullable=False)  # 分类
    tags = Column(String(100), default="", nullable=False)  # 标签
    cover = Column(String(300), default="", nullable=False)  # 封面图
    view_count = Column(Integer, default=0, nullable=False)  # 浏览数
    comment_count = Column(Integer, default=0, nullable=False)  # 评论数
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<CorelDrawVBAArticle(title='%s')>" % (self.title)


# 初始化数据引擎
CorelDrawVBASubscriberModelBase.metadata.create_all(engine)
CorelDrawVBASubscriberModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
