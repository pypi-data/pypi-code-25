from __future__ import absolute_import

import pytest
import webtest
import six

from bottle import Bottle, request

from odinweb import bottle
from odinweb.constants import Method, Type
from odinweb.data_structures import PathParam


def test_request_proxy():
    test_app = Bottle(catchall=False)
    app = webtest.TestApp(test_app)

    @test_app.route('/', method='POST')
    def test_method():
        target = bottle.RequestProxy(request)
        assert target.method == Method.POST
        assert set(target.query.getlist('a')) == {'1', '3'}
        assert set(target.query.getlist('b')) == {'2'}
        assert target.body == "123" if six.PY2 else b'123'
        assert target.content_type == 'text/html'
        assert target.origin == "http://localhost:9000"
        return 'OK'

    result = app.post('/?a=1&b=2&a=3', expect_errors=False, content_type="text/html",
                      headers={"Origin": "http://localhost:9000"}, params='123')
    assert result.body == 'OK' if six.PY2 else b'OK'


@pytest.mark.parametrize('path_node, expected', (
    (PathParam('foo'), "<foo:int>"),
    (PathParam('foo', Type.String), "<foo:re:[-\w.~,!%]+>"),
    (PathParam('foo', Type.Boolean), "<foo:bool>"),
    (PathParam('foo', None), "<foo>"),
))
def test_node_formatter(path_node, expected):
    actual = bottle.Api.node_formatter(path_node)
    assert actual == expected


class TestApi(object):
    def test_merge_api_and_request(self):
        test_app = Bottle(catchall=False)
        app = webtest.TestApp(test_app)
        target = bottle.Api()

        @target.operation('{foo:String}')
        def sample_operation(request, foo):
            assert isinstance(request, bottle.RequestProxy)
            assert foo == 'eek'
            return 'OK'

        test_app.merge(target)

        result = app.get('/api/eek', expect_errors=False)
        assert result.body == '"OK"' if six.PY2 else b'"OK"'
