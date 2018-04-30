# -*- coding: utf-8 -*-
from zebe.module.project import Project, Task, ProjectModelSession
from zebe.service.base import ModelBaseService


# 项目服务
class ProjectService(ModelBaseService):

    def __init__(self):
        super().__init__(Project, ProjectModelSession)

    # 按照年份和类型查询项目
    def find_by_year_and_type(self, year, project_type):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.type == project_type).all()
        self.session.close()
        return result

    # 按照年份和类型查询项目总数
    def count_by_year_and_type(self, year, project_type):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.type == project_type).count()
        self.session.close()
        return result

    # 更新单个任务进度
    def update_progress(self, data_id, progress):
        entity = self.session.query(self.entity).filter(self.entity.id == data_id).one_or_none()
        if entity is not None:
            entity.progress = progress
            self.session.commit()
            self.session.close()

    # 按照名称查找项目
    def find_one_by_name(self, name):
        result = self.session.query(self.entity).filter(self.entity.name == name).one_or_none()
        self.session.close()
        return result


# 任务服务
class TaskService(ModelBaseService):

    def __init__(self):
        super().__init__(Task, ProjectModelSession)

    # 按照年份查询全部任务总数
    def count_all_by_year(self, year):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year)).count()
        self.session.close()
        return result

    # 按照年份查询已完成任务总数
    def count_finished_by_year(self, year):
        # TODO 1 是个魔法数字，修正为常量
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.status == 1).count()
        self.session.close()
        return result
