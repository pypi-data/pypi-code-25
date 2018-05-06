# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import json
from random import random
import os
import datetime
from django.utils import timezone
import random
import requests
from django.conf import settings


from .models import Feedback

app_name = 'feedback'

def index(request):
    template_path = '{app}/index.html'.format(app=app_name)
    context = {}
    return render(request, template_path, context)



def submit_feedback(request):
    if request.POST:
        try:
            feedback = Feedback()
            feedback.rating = request.POST['rating']
            feedback.feedback = request.POST['feedback']
            feedback.email = request.POST['email']
            feedback.page = request.POST['page']
            feedback.save()
            print('here', request.POST, feedback)
            return HttpResponse('submitted')
        except:
            return HttpResponse('error')

    return HttpResponse('Not posted to submit_feedback.')
