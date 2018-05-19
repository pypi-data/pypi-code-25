#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# import json
# from json import JSONEncoder
# from rest_framework.fields import empty

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    pass


class BaseModelSerializer(serializers.ModelSerializer):
    pass
