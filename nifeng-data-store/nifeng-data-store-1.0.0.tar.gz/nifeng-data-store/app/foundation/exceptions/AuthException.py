class AuthException(Exception):
    def __init__(self, err='数据库错误'):
        Exception.__init__(self, err)


class AuthorizationError(Exception):
    def __init__(self, err='Authorize error'):
        Exception.__init__(self, err)
