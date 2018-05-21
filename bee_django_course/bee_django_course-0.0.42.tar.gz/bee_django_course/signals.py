# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 作业被评分前发出的信号
assignment_will_be_scored = Signal(providing_args=["user_course_section", "request"])

# 作业评分后发出的信号
assignment_was_scored = Signal(providing_args=["user_course_section", "request"])


