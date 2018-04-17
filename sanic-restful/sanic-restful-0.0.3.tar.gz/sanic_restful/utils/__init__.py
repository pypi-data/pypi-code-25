import sys

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from werkzeug.http import HTTP_STATUS_CODES

PY3 = sys.version_info > (3,)


def http_status_message(code):
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


def get_accept_mimetypes(request):
    accept_types = request.headers.get('accept', None)
    if accept_types is None:
        return {}
    split_types = str(accept_types).split(',')
    # keep the order they appear!
    return OrderedDict([((s, 1,), s,) for s in split_types])


def best_match_accept_mimetype(request, representations, default=None):
    if representations is None or len(representations) < 1:
        return default
    try:
        accept_mimetypes = get_accept_mimetypes(request)
        if accept_mimetypes is None or len(accept_mimetypes) < 1:
            return default
        # find exact matches, in the order they appear in the `Accept:` header
        for accept_type, qual in accept_mimetypes:
            if accept_type in representations:
                return accept_type
        # match special types, like "application/json;charset=utf8" where the first half matches.
        for accept_type, qual in accept_mimetypes:
            type_part = str(accept_type).split(';', 1)[0]
            if type_part in representations:
                return type_part
        # if _none_ of those don't match, then fallback to wildcard matching
        for accept_type, qual in accept_mimetypes:
            if accept_type == "*"\
               or accept_type == "*/*"\
               or accept_type == "*.*":
                return default
    except (AttributeError, KeyError):
        return default


def _endpoint_from_view_func(view_func):
    """Internal helper that returns the default endpoint for a given
    function.  This always is the function name.
    """
    assert view_func is not None, 'expected view func if endpoint ' \
                                  'is not provided.'
    return view_func.__name__
