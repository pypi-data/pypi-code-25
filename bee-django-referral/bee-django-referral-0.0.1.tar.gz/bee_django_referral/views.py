# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django import forms

from .decorators import cls_decorator, func_decorator
from .models import Activity, UserShareImage
from .utils import save_user_qrcode_img, get_now_timestamp
from .forms import ActivityForm, ActivityUpdateForm, ActivityQrCodeImgUpdateForm, ActivityQrCodeUpdateForm
from .qr import create_qrcode, merge_img, toRgb
from .exports import get_user_qrcode


# Create your views here.

def test(request):
    return


# ========Activity===========
@method_decorator(cls_decorator(cls_name='ActivityList'), name='dispatch')
class ActivityList(ListView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_list.html'
    context_object_name = 'activity_list'
    paginate_by = 20
    ordering = ["-start_date"]


@method_decorator(cls_decorator(cls_name='ActivityDetail'), name='dispatch')
class ActivityDetail(DeleteView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_detail.html'
    context_object_name = 'activity'


@method_decorator(cls_decorator(cls_name='SourceCreate'), name='dispatch')
class ActivityCreate(CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'bee_django_referral/activity/activity_form.html'


@method_decorator(cls_decorator(cls_name='ActivityUpdate'), name='dispatch')
class ActivityUpdate(UpdateView):
    model = Activity
    form_class = ActivityUpdateForm
    template_name = 'bee_django_referral/activity/activity_form.html'

    # def get_context_data(self, **kwargs):
    #     context = super(ActivityUpdate, self).get_context_data(**kwargs)
    #     context["activity"] = Activity.objects.get(id=self.kwargs["pk"])
    #     return context


@method_decorator(cls_decorator(cls_name='ActivityQrcodeUpdate'), name='dispatch')
class ActivityQrcodeUpdate(UpdateView):
    model = Activity
    form_class = ActivityQrCodeUpdateForm
    template_name = 'bee_django_referral/activity/activity_qrcode_form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:activity_qrcode_update', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActivityQrcodeUpdate, self).get_context_data(**kwargs)
        context["img_form"] = ActivityQrCodeImgUpdateForm
        context["timestamp"] = get_now_timestamp().__str__()
        return context

    def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        activity = form.save(commit=True)
        ret = save_user_qrcode_img(activity_id=activity.id, user_id='', url=activity.qrcode_url)
        if ret:
            activity.qrcode_thumb = ret
            activity.save()
        return super(ActivityQrcodeUpdate, self).form_valid(form)




# =======User Activity =======
@method_decorator(cls_decorator(cls_name='UserActivityDetail'), name='dispatch')
class UserActivityDetail(DetailView):
    model = Activity
    template_name = 'bee_django_referral/activity/user_activity_detail.html'
    context_object_name = 'activity'

    # def get_context_data(self, **kwargs):
    #     context = super(UserActivityDetail, self).get_context_data(**kwargs)
    #     user = None
    #     activity_id=self.kwargs["activity_id"]
    #     user_qrcode_list = get_user_qrcode(user,activity_id=activity_id)
    #     return context




