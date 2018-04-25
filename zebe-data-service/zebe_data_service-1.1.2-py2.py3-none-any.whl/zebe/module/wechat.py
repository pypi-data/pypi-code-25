# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from zebe.module import WECHAT_DB_FILE_PATH

# 定义数据库路径
engine = create_engine('sqlite:///' + WECHAT_DB_FILE_PATH, echo=True)
WeChatModelBase = declarative_base()


# 秒记先生微信用户
class WeChatMiaoJiUser(WeChatModelBase):
    __tablename__ = 'wechat_miaoji_user'
    id = Column(String(28), primary_key=True)  # ID（和openId相同）
    realname = Column(String(20), nullable=False, default='')  # 真实姓名
    nickname = Column(String(32), nullable=False, default='')  # 昵称
    wxid = Column(String(20), nullable=False, default='')  # 微信号
    follow_time = Column(DateTime, nullable=False, default=datetime.now())  # 关注时间
    unfollow_time = Column(DateTime)  # 取消关注时间

    def __repr__(self):
        return "<WeChatMiaoJiUser(id='%s')>" % (self.id)


# 秒记先生微信用户发来的消息
class WeChatMiaoJiUserMessage(WeChatModelBase):
    __tablename__ = 'wechat_miaoji_user_msg'
    id = Column(Integer, primary_key=True)  # ID
    type = Column(String(10), default="", nullable=False, index=True)  # 消息类型
    content = Column(Text, default="", nullable=False)  # 文本内容
    voice = Column(Text, default="", nullable=False)  # 语音内容
    link = Column(String(300), default="", nullable=False)  # 链接
    source = Column(String(40), default="", nullable=False)  # 消息来源
    reply = Column(Text, default="", nullable=False)  # 回复内容
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 发送时间

    def __repr__(self):
        return "<WeChatMiaoJiUserMessage(content='%s')>" % (self.content)


# Zebe个人微信用户
class WeChatZebeUser(WeChatModelBase):
    __tablename__ = 'wechat_zebe_user'
    id = Column(String(28), primary_key=True)  # ID（和openId相同）
    realname = Column(String(20), nullable=False, default='')  # 真实姓名
    nickname = Column(String(32), nullable=False, default='')  # 昵称
    wxid = Column(String(20), nullable=False, default='')  # 微信号
    follow_time = Column(DateTime, nullable=False, default=datetime.now())  # 关注时间
    unfollow_time = Column(DateTime)  # 取消关注时间

    def __repr__(self):
        return "<WeChatZebeUser(id='%s')>" % (self.id)


# Zebe个人微信用户发来的消息
class WeChatZebeUserMessage(WeChatModelBase):
    __tablename__ = 'wechat_zebe_user_msg'
    id = Column(Integer, primary_key=True)  # ID
    type = Column(String(10), default="", nullable=False, index=True)  # 消息类型
    content = Column(Text, default="", nullable=False)  # 文本内容
    voice = Column(Text, default="", nullable=False)  # 语音内容
    link = Column(String(300), default="", nullable=False)  # 链接
    source = Column(String(40), default="", nullable=False)  # 消息来源
    reply = Column(Text, default="", nullable=False)  # 回复内容
    create_time = Column(DateTime, default=datetime.now(), nullable=False)  # 发送时间

    def __repr__(self):
        return "<WeChatZebeUserMessage(content='%s')>" % (self.content)


# 初始化数据引擎
WeChatModelBase.metadata.create_all(engine)
WechatModelSession = sessionmaker(bind=engine)
logging.debug("初始化数据引擎 -> 成功")
