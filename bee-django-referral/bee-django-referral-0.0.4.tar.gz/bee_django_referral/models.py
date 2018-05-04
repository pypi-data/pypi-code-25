# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


class Activity(models.Model):
    name = models.CharField(max_length=180, verbose_name='活动名称')
    source_name = models.CharField(max_length=180, verbose_name='渠道名称', null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    detail = models.TextField(verbose_name='活动说明', null=True, blank=True)
    info = models.TextField(verbose_name='分享说明', null=True, blank=True)
    explain = models.TextField(verbose_name='规则解释', null=True, blank=True)
    # ===二维码===
    qrcode_width = models.IntegerField(verbose_name='二维码宽度', null=True,blank=True, default=0)
    qrcode_height = models.IntegerField(verbose_name='二维码高度', null=True,blank=True, default=0)
    qrcode_pos_x = models.IntegerField(verbose_name='二维码x轴坐标', null=True,blank=True, default=0)
    qrcode_pos_y = models.IntegerField(verbose_name='二维码y轴坐标', null=True,blank=True, default=0)
    qrcode_color = models.CharField(max_length=8, verbose_name='二维码颜色', default='#000000', null=True)
    qrcode_bg = models.ImageField(verbose_name='二维码', upload_to='bee_django_referral/qrcode/bg', null=True,blank=True)
    qrcode_thumb = models.CharField(verbose_name='二维码预览图', max_length=180, null=True,blank=True)
    qrcode_url = models.CharField(verbose_name='二维码地址', max_length=180, null=True,blank=True)

    class Meta:
        db_table = 'bee_django_referral_activity'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_referral:activity_detail', kwargs={"pk": self.id.__str__()})



class UserShareImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    qrcode = models.ImageField(verbose_name='二维码', upload_to='bee_django_referral/user_qrcode/')
    created_at = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)
    status = models.IntegerField(default=0, verbose_name='状态')

    class Meta:
        db_table = 'bee_django_referral_image'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.qrcode
