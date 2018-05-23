

class AuthException(Exception):

    def __init__(self, username, user=None):
        super().__init__(username, user)
        self.username = username
        self.user = user


class UserAlreadyExistException(AuthException):
    pass


class UserNotExistException(AuthException):
    pass


class NotLoggedInError(AuthException):
    pass


class PasswordMissmatchException(AuthException):
    pass


class PasswordTooShortException(AuthException):
    pass


class PermissionError(Exception):
    pass


class NotPermittedError(Exception):
    pass