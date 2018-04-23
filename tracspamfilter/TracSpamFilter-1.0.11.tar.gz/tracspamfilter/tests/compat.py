# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

import StringIO

from trac.perm import PermissionCache
from trac.test import Mock, MockPerm, locale_en
from trac.util.datefmt import utc
from trac.web.api import _RequestArgs, Request
from trac.web.session import DetachedSession

try:
    from trac.test import MockRequest
except ImportError:
    def MockRequest(env, **kwargs):
        """Request object for testing. Keyword arguments populate an
        `environ` dictionary and the callbacks.

        If `authname` is specified in a keyword arguments a `PermissionCache`
        object is created, otherwise if `authname` is not specified or is
        `None` a `MockPerm` object is used and the `authname` is set to
        'anonymous'.

        The following keyword arguments are commonly used:
        :keyword args: dictionary of request arguments
        :keyword authname: the name of the authenticated user, or 'anonymous'
        :keyword method: the HTTP request method
        :keyword path_info: the request path inside the application

        Additionally `format`, `locale`, `lc_time` and `tz` can be
        specified as keyword arguments.

        :since: 1.0.11
        """

        authname = kwargs.get('authname')
        if authname is None:
            authname = 'anonymous'
            perm = MockPerm()
        else:
            perm = PermissionCache(env, authname)

        args = _RequestArgs()
        args.update(kwargs.get('args', {}))

        environ = {
            'trac.base_url': env.abs_href(),
            'wsgi.url_scheme': 'http',
            'HTTP_ACCEPT_LANGUAGE': 'en-US',
            'PATH_INFO': kwargs.get('path_info', '/'),
            'REQUEST_METHOD': kwargs.get('method', 'GET'),
            'REMOTE_ADDR': '127.0.0.1',
            'REMOTE_USER': authname,
            'SCRIPT_NAME': '/trac.cgi',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
        }

        status_sent = []
        headers_sent = {}
        response_sent = StringIO.StringIO()

        def start_response(status, headers, exc_info=None):
            status_sent.append(status)
            headers_sent.update(dict(headers))
            return response_sent.write

        req = Mock(Request, environ, start_response)
        req.status_sent = status_sent
        req.headers_sent = headers_sent
        req.response_sent = response_sent

        from trac.web.chrome import Chrome
        req.callbacks.update({
            'arg_list': None,
            'args': lambda req: args,
            'authname': lambda req: authname,
            'chrome': Chrome(env).prepare_request,
            'form_token': lambda req: kwargs.get('form_token'),
            'languages': Request._parse_languages,
            'lc_time': lambda req: kwargs.get('lc_time', locale_en),
            'locale': lambda req: kwargs.get('locale'),
            'incookie': Request._parse_cookies,
            'perm': lambda req: perm,
            'session': lambda req: DetachedSession(env, authname),
            'tz': lambda req: kwargs.get('tz', utc),
            'use_xsendfile': False,
            'xsendfile_header': None,
            '_inheaders': Request._parse_headers
        })

        return req