from django.conf import settings
from django.contrib.auth import get_user_model
import requests
from .helpers import (get_user, ag_authenticate, user_from_result)


class AppointmentGuruBackend(object):

    def authenticate(self, request, username=None, password=None):
        path = '/api/auth/login/'
        data = {
            "username": username,
            "password": password
        }
        return ag_authenticate(path, data)

    # def get_user(self, user_id):
    #     #todo: get from API
    #     user_from_result(result)


class AppointmentGuruOTPBackend(object):

    def authenticate(self, request, phone_number=None, otp=None):
        path = '/api/auth/otp/'
        data = {
            "phone_number": phone_number,
            "otp": otp
        }
        return ag_authenticate(path, data)

class AppointmentGuruPhoneBackend(object):

    def authenticate(self, request, phone_number=None, password=None):
        path = '/api/auth/phone/token/'
        data = {
            "phone_number": phone_number,
            "password": password
        }
        return ag_authenticate(path, data)