#!/usr/bin/env python
# -*- coding:utf-8 -*-

from .models import UserShareImage, Activity, UserShareImage, UserQrcodeRecordStatus
from .utils import save_user_qrcode_img, save_user_image_db, get_now_timestamp, user_qrcode_record_add

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
def get_user_qrcode(user, activity_id, status=None):
    image_list = UserShareImage.objects.filter(user=user, activity__id=activity_id)
    if status:
        image_list = image_list.filter(status__in=status)
    return image_list


# 生成用户二维码,并保存到数据库
def create_user_image(user, activity_id, ex_url, status, count=3):
    try:
        activity = Activity.objects.get(id=activity_id)
    except:
        return

    for i in range(0, count):
        timestamp = get_now_timestamp()
        url = ex_url + "&t=" + timestamp.__str__()
        qrcode_path = save_user_qrcode_img(activity_id=activity.id, user_id=user.id, url=url, timestamp=timestamp)
        if qrcode_path:
            save_user_image_db(user=user, activity=activity, qrcode_path=qrcode_path, status=status,
                               timestamp=timestamp)
    return


def get_user_qrcode_image(timestamp, user, activity_id):
    try:
        user_image = UserShareImage.objects.get(user=user, timestamp=timestamp, activity_id=activity_id)
        return user_image
    except:
        return None


def after_preuser_add(user, timestamp, preuser_id, img_status):
    try:
        user_image = UserShareImage.objects.get(user=user, timestamp=timestamp)
    except:
        return None

    user_qrcode_record_add(user_qrcode_img_id=user_image.id, preuser_id=preuser_id,
                           record_status=UserQrcodeRecordStatus.reg, img_status=img_status)
