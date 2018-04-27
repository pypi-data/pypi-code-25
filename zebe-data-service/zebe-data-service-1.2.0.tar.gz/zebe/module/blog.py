# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import BLOG_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + BLOG_DB_FILE_PATH, echo=True)
BlogModelBase = declarative_base()


# 博客文章
class BlogArticle(BlogModelBase):
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
        return "<BlogArticle(title='%s')>" % (self.title)


# 初始化数据引擎
BlogModelBase.metadata.create_all(engine)
BlogModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
