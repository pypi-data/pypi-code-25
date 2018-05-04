#!/usr/bin/env python
# -*- coding:utf-8 -*-

from .models import UserShareImage, Activity
from .utils import save_user_qrcode_img

__author__ = 'bee'


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime

# 获取活动的起止时间
def get_activity_date(activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
    except:
        return None
    return [activity.start_date, activity.end_date]


# 获取用户的二维码图片
def get_user_qrcode(user, activity_id, status):
    image_list = UserShareImage.objects.filter(user=user, activity__id=activity_id, status__in=status)
    return image_list


# 生成用户二维码
# def a(user, activity_id, url, count=1):
#     try:
#         activity = Activity.objects.get(id=activity_id)
#     except:
#         return
#
#     for i in range(0, count):
#         image = UserShareImage()
#         image.activity = activity
#         image.user = user
#         image.status = 1
#         ret = save_user_qrcode_img(activity_id=activity.id, user_id=user.id, url=url)
#         if ret:
#             image.qrcode = ret
#             image.save()
#     return
