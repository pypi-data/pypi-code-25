# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import MEMCARD_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + MEMCARD_DB_FILE_PATH, echo=True)
MemoryCardModelBase = declarative_base()


# 秒记卡
class MemoryCard(MemoryCardModelBase):
    __tablename__ = 'memcard'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # ID
    key = Column(String(20), default="", index=True)  # 记忆键
    content = Column(Text, default="")  # 记忆内容
    target = Column(String(100), default="")  # 记忆目标
    description = Column(Text, default="")  # 记忆描述
    type = Column(String(20), default="", index=True)  # 分类
    image = Column(String(300), default="")  # 辅助图像
    image_gif = Column(String(300), default="")  # 辅助图像(动态)
    sound = Column(String(300), default="")  # 辅助声音
    url = Column(String(500), default="")  # 跳转链接
    filename = Column(String(60), default="")  # 文件名
    create_time = Column(DateTime, default=datetime.now())  # 创建时间

    def __repr__(self):
        return "<MemoryCard(name='%s')>" % (self.name)


# 初始化数据引擎
MemoryCardModelBase.metadata.create_all(engine)
MemoryCardModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
