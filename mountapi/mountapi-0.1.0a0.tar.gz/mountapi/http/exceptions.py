from mountapi.http import status


class HttpError(Exception):
    pass


class HttpClientError(HttpError):
    pass


class Http404(HttpError):
    status_code = status.NOT_FOUND_404
