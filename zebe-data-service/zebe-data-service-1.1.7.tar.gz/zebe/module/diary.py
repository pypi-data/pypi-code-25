# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text, SmallInteger
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import DIARY_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + DIARY_DB_FILE_PATH, echo=True)
DiaryModelBase = declarative_base()


# 日记
class Diary(DiaryModelBase):
    __tablename__ = 'diary'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    title = Column(String(50), default="", nullable=False)  # 标题
    content = Column(Text, default="", nullable=False)  # 内容
    learned = Column(SmallInteger, default=0, nullable=False)  # 新掌握知识数量
    year = Column(SmallInteger, default=0, nullable=False)  # 所属年份
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 创建时间

    def __repr__(self):
        return "<Diary(content='%s')>" % (self.content)


# 初始化数据引擎
DiaryModelBase.metadata.create_all(engine)
DiaryModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
