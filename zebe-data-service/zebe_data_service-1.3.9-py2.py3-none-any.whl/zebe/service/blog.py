# -*- coding: utf-8 -*-
from zebe.module.blog import BlogArticle, BlogModelSession
from zebe.service.base import ModelBaseService


# 博客文章服务
class BlogArticleService(ModelBaseService):

    def __init__(self):
        super().__init__(BlogArticle, BlogModelSession)
