# -*- coding: utf-8 -*-
from zebe.module.diary import Diary, DiaryModelSession
from zebe.service.base import ModelBaseService


# 日记服务
class DiaryService(ModelBaseService):

    def __init__(self):
        super().__init__(Diary, DiaryModelSession)

    # 通过标题查找一篇日记
    def find_one_by_title(self, title):
        result = None
        if title is not None:
            result = self.session.query(self.entity).filter(self.entity.title == title).one_or_none()
            self.session.close()
        return result
