from __future__ import absolute_import
from sanic_restful.utils import PY3
try:
    from rapidjson import dumps
except ImportError:
    from json import dumps

from sanic.response import text


def output_json(app, data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    settings = app.config.get('RESTFUL_JSON', {})

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    if app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', not PY3)

    # always end the json dumps with a new line
    dumped = dumps(data, **settings) + "\n"

    resp = text(dumped, code, content_type="application/json")
    resp.headers.update(headers or {})
    return resp
