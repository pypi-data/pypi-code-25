# encoding: utf-8
from __future__ import unicode_literals
from rest_framework.pagination import BasePagination
from .utils import coreapi


class Result(object):
    def __init__(self, dataset=None, serializer=None):
        self.errors = []
        self._error = self.errors.append
        self.serializer = serializer
        self.dataset = None
        self.msg = None

    def data(self, dataset):
        self.dataset = dataset
        return self

    def error(self, key, value, **kwargs):
        self._error(dict(kwargs, name=key, value=value))
        return self

    def perm(self, reason):
        self.msg = reason
        return self

    def __nonzero__(self):
        return not self.errors

    def response(self):
        raise NotImplementedError

    def __call__(self, status=200, serialize=False, **kwargs):
        return self.response(status=status, serialize=serialize, **kwargs)

    def __bool__(self):
        return not self.errors


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

        start, end, pagesize, iTotalRecords, split = getPageParams(request, keys)
        if not isinstance(keys, list): # py3兼容 dict_values不是list
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

class Valid(object):
    def __init__(self, method, **kwargs):
        """
        status 是一个属性，而不是一个方法
        """
        self.method = method
        self.status = 200
        self.msg = None
        self.kwargs = kwargs

    def __str__(self):
        return '<Valid: %s>' % self.method

    def __repr__(self):
        return '<Valid: %s>' % self.method

    def __call__(self, *args, **kwargs):
        return getattr(self, self.method)(*args, **kwargs)


    def enum(self, map):
        map = {str(x): str(y) for x, y in map}
        reverseMap = {str(y): x for x, y in map.items()}

        def inner(data):
            return (map.get(data) and data) or reverseMap.get(data)

        return dict(method=inner, description=map)

class MethodProxy(object):
    kwargs = {}

    def __init__(self, valid_class=None):
        self.valid_class = valid_class

    def __call__(self, *args, **kwargs):
        self.kwargs = kwargs
        return self

    def __getattr__(self, key):
        return self.valid_class(key, **self.kwargs)
