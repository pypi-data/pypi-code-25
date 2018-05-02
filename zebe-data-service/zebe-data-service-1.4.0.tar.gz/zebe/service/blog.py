# -*- coding: utf-8 -*-
from zebe.module.blog import ZebeBlogArticle, BlogModelSession, CdrVbaBlogArticle, CdrVbaBlogSubscriber
from zebe.service.base import ModelBaseService


# Zebe博客文章服务
class ZebeBlogArticleService(ModelBaseService):

    def __init__(self):
        super().__init__(ZebeBlogArticle, BlogModelSession)


# CorelDrawVBA博客文章服务
class CdrVbaBlogArticleService(ModelBaseService):

    def __init__(self):
        super().__init__(CdrVbaBlogArticle, BlogModelSession)


# CorelDrawVBA博客订阅者服务
class CdrVbaBlogSubscriberService(ModelBaseService):

    def __init__(self):
        super().__init__(CdrVbaBlogSubscriber, BlogModelSession)
