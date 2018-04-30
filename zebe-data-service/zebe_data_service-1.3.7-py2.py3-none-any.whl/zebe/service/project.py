# -*- coding: utf-8 -*-
from datetime import datetime

from zebe.module.project import Project, Task, ProjectModelSession, AutoDailyTask
from zebe.service.base import ModelBaseService


# 项目服务
class ProjectService(ModelBaseService):

    def __init__(self):
        super().__init__(Project, ProjectModelSession)

    # 按照年份和类型查询全部项目
    def find_by_year_and_type(self, year, project_type):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.type == project_type).all()
        self.session.close()
        return result

    # 按照年份查询全部项目
    def find_all_by_year(self, year):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year)).all()
        self.session.close()
        return result

    # 按照年份查询主要项目
    def find_main_by_year(self, year):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.is_main == 1).all()
        self.session.close()
        return result

    # 按照年份查询次要项目
    def find_secondary_by_year(self, year):
        entity = self.entity
        result = self.session.query(entity).filter(entity.year == int(year), entity.is_main == 0).all()
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

    # 获取一组项目的进度
    def get_progress_of_projects(self, project_list):
        progress = 0
        if project_list is None and len(project_list) > 0:
            total_project = len(project_list)
            total_progress = 0
            for project in project_list:
                total_progress += project.progress
            progress = round(total_progress / total_project, 2)
        return progress

    # 获取一组项目的任务总数
    def get_total_task_of_projects(self, project_list):
        total_task = 0
        if project_list is not None and len(project_list) > 0:
            for project in project_list:
                total_task += project.total_task
        return total_task

    # 获取一组项目的已完成任务总数
    def get_finished_task_of_projects(self, project_list):
        total_finished_task = 0
        if project_list is not None and len(project_list) > 0:
            for project in project_list:
                total_finished_task += project.finished_task
        return total_finished_task


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


# 自动日常任务服务
class AutoDailyTaskService(ModelBaseService):

    def __init__(self):
        super().__init__(AutoDailyTask, ProjectModelSession)

    # 按日期查询全部任务
    def find_all_by_date(self, date):
        entity = self.entity
        result = self.session.query(entity).filter(entity.date == str(date)).all()
        self.session.close()
        return result

    # 按日期删除全部数据
    def delete_all_by_date(self, date):
        self.session.query(self.entity).filter(self.entity.date == str(date)).delete(synchronize_session=False)
        self.session.commit()
        self.session.close()

    # 标记任务完成
    def mark_finish(self, data_id):
        self.__mark_finish_or_unfinish(data_id, True)

    # 标记任务未完成
    def mark_unfinish(self, data_id):
        self.__mark_finish_or_unfinish(data_id, False)

    # 标记任务完成|未完成
    def __mark_finish_or_unfinish(self, data_id, finished):
        entity = self.find_one(data_id)
        if entity is not None:
            entity.status = 1 if finished else 0  # TODO 1和0是魔法数字，改为常量
            entity.finish_time = datetime.now() if finished else None
            self.update(entity)
            # 如果任务归属于某个项目，则自动更新项目的进度
            project_id = entity.project_id
            if project_id is not None:
                project_service = ProjectService()
                project = project_service.find_one(project_id)
                if project is not None:
                    project.finished_task = project.finished_task + 1
                    project.progress = round((project.finished_task / project.total_task) * 100, 2)
                    project_service.update(project)
                    print("任务归属于项目，已自动更新项目的进度")
            else:
                print("任务不归属于任何项目，不需要更新项目的进度")
