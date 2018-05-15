"""
Backlog API Library errors
"""


class BaseBacklogError(Exception):
    """
    Base exception class for backlog exception
    """
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class InternalError(BaseBacklogError):
    """
    Error due to program bug etc
    """
    def __init__(self):
        super().__init__('Error due to program bug etc')


class LicenceError(BaseBacklogError):
    """
    This functin can not be used with licence
    """
    def __init__(self):
        super().__init__('This function can not be used with license')


class LicenceExpiredError(BaseBacklogError):
    """
    Licence has already expired
    """
    def __init__(self):
        super().__init__('Licence has already expired')


class AccessDeniedError(BaseBacklogError):
    """
    Access denied
    """
    def __init__(self):
        super().__init__('Access denied')


class UnauthorizedOperationError(BaseBacklogError):
    """
    Unauthorized operation is invoked by the user
    """
    def __init__(self):
        super().__init__('Unauthorized operation is invoked by the user')


class NoResourceError(BaseBacklogError):
    """
    Requested resource dose not exist
    """
    def __init__(self):
        super().__init__('Requested resource dose not exist')


class InvalidRequestError(BaseBacklogError):
    """
    Request parameter is invalid
    """
    def __init__(self):
        super().__init__('Request parameter is invalid')


class SpaceOverCapacityError(BaseBacklogError):
    """
    Space capacity limit exceeded
    """
    def __init__(self):
        super().__init__('Space capacity limit exceeded')


class ResourceOverflowError(BaseBacklogError):
    """
    Resource capacity limit exceeded
    """
    def __init__(self):
        super().__init__('Resource capacity limit exceeded')


class TooLargeFileError(BaseBacklogError):
    """
    File size exceeds limit
    """
    def __init__(self):
        super().__init__('File size exceeds limit')


class AuthenticationError(BaseBacklogError):
    """
    Certification failed
    """
    def __init__(self):
        super().__init__('Certification failed')


class FailedCreateInstance(BaseBacklogError):
    """
    Args of from_json method must be dict
    """
    def __init__(self):
        super().__init__('Can not create instance from json')
