# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Activity, UserShareImage


# ===source===
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'source_name', 'start_date', 'end_date', 'detail', 'info', "explain"]


class ActivityUpdateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'start_date', 'end_date', 'detail', 'info', "explain"]


class ActivityQrCodeImgUpdateForm(forms.ModelForm):

    class Meta:
        model = Activity
        fields = ['qrcode_bg']

class ActivityQrCodeUpdateForm(forms.ModelForm):
    qrcode_width = forms.IntegerField(min_value=1, label='二维码宽度',required=False)
    qrcode_height = forms.IntegerField(min_value=1, label='二维码高度',required=False)

    class Meta:
        model = Activity
        fields = ["qrcode_width", "qrcode_height", "qrcode_pos_x", "qrcode_pos_y", "qrcode_color", ]
