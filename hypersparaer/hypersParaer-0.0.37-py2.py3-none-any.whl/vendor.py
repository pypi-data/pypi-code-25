# encoding: utf-8

from functools import partial
import collections

from django.db.models import QuerySet, Model
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet as _ViewSet
from rest_framework.compat import coreapi
from rest_framework.exceptions import APIException
from rest_framework.views import APIView as _APIView
from rest_framework import exceptions, permissions, status
from paraer import Result as __Result, para_ok_or_400


class Result(__Result):
    def __init__(self, data=None, errors=None, serializer=None,
                 paginator=None):
        self.serializer = serializer
        self.data = data
        self._fields = {}
        self._message = None
        self.paginator = paginator
        self._code = '200000'

    def error(self, key, value, **kwargs):
        self._code = '200002'
        value = [{'code': '200002', 'message': value}]
        self._fields[key] = value
        return self

    def __call__(self, status=200, serialize=True, **kwargs):
        """
        @serialize 是否对data做序列化
        @status     返回的http status code
        :return:
        {
            "code":"200000",
            "message":"......",
            "result":{
                "summary":{},
                "items":[{...},{...},{...}]
            },
            "page":{"current":1,"pagesize":10,"total":16},
            "fields":{
                    "field1":[{"code":"","message":""}]
                    "field2":[{"code":"","message":""}]
            }
        }
        """
        data = self.data or {}
        should_serialize = self.serializer and serialize
        response = dict(code=self._code)
        if isinstance(data, collections.Iterable) and not (isinstance(
                data, dict)):  # list 方法返回可迭代对象
            if should_serialize and (data and isinstance(data[0], Model)):
                data = self.serializer(data, many=True).data
            response = self.paginator.paginate_queryset(
                data, self.paginator.request)
        elif should_serialize and isinstance(data, Model):
            response['result'] = self.serializer(data).data
        else:
            response['result'] = data
        # 参数错误
        if self._fields:
            response['fields'] = self._fields
        if self._message:
            response['message'] = self._message
        return Response(response, **kwargs)

    def __bool__(self):
        return not self._fields

    def redirect(self, path='', status=403, **kwargs):
        data = dict(code='200302')

        if not path and status in [403, 404]:
            path = '/#/error?code={}'.format(status)
        data.update(url=path)

        # reason
        reason = kwargs.get('reason', '')
        if isinstance(reason, dict):
            for k, v in reason.items():
                reason = '对{}{}'.format(k, v)
        reason and data.update(reason=reason)
        return Response(data, status=200)


def getPageParams(request, keys):
    page = str(request.GET.get('page', 1))
    page = int(page.isdigit() and page or 1)
    pagesize = str(request.GET.get('pagesize', 10))
    split = pagesize.isdigit()
    pagesize = min(int(pagesize.isdigit() and pagesize or 10), 100)
    iTotalRecords = len(keys)
    startRecord = (page - 1) * pagesize
    endRecord = iTotalRecords if iTotalRecords - startRecord < pagesize else startRecord + pagesize

    return startRecord, endRecord, pagesize, iTotalRecords, split


class PageNumberPager(BasePagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'

    def paginate_queryset(self, keys, request, **kwargs):
        """

        :param keys:
        :param request:
        :param kwargs:
        :return:
        """
        result = {
            'code': '200000',
            'page': {
                'current': 0,
                'pagesize': 10,
                'total': 0
            }
        }

        start, end, pagesize, iTotalRecords, split = getPageParams(
            request, keys)
        if not isinstance(keys, list):  # py3兼容 dict_values不是list
            keys = list(keys)

        if split:
            keys = keys[start:end]
        else:
            pagesize = iTotalRecords

        result['page']['current'] = start
        result['page']['total'] = iTotalRecords
        result['page']['pagesize'] = pagesize
        result['items'] = keys
        return result

    def get_schema_fields(self, view):
        fields = [
            coreapi.Field(
                name=self.page_query_param,
                required=False,
                location='query',
                description=u'分页参数：当为空时，获取全量数据',
                type='integer')
        ]
        if self.page_size_query_param is not None:
            fields.append(
                coreapi.Field(
                    name=self.page_size_query_param,
                    required=False,
                    location='query',
                    description=u'分页参数：当为空时，获取全量数据，当传值时，支持[10, 25, 50, 100]分页',
                    type='integer'))
        return fields


class MixinView(object):
    __result_class = Result
    serializer_class = None
    pagination_class = PageNumberPager

    @property
    def result_class(self):
        paginator = self.paginator
        paginator.request = self.request
        return partial(
            self.__result_class,
            serializer=self.serializer_class,
            paginator=paginator)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator


class NotAuthenticatedException(APIException):
    status_code = status.HTTP_200_OK


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        path = '/#/login'
        NotAuthenticatedException.default_detail = dict(
            code='200302', url=path)
        raise NotAuthenticatedException


class ViewSet(MixinView, _ViewSet):
    permission_classes = (IsAuthenticated, )


class APIView(MixinView, _APIView):
    permission_classes = (IsAuthenticated, )
    pass


class UnAuthApiView(MixinView, _APIView):
    pass
