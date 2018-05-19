#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.pagination import PageNumberPagination


class FlytrapPagination(PageNumberPagination):
    page_size_query_param = 'size'
