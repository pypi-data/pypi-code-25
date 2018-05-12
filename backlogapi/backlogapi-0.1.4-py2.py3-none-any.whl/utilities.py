"""
Helper function for Backlog API
"""


from functools import wraps
import requests

from . import exceptions


def protect(roles):
    def _protect(func):
        @wraps(func)
        def __protect(self, *args, **kwargs):
            if self.__class__.__name__ == 'BacklogClient':
                role = self.role
            else:
                role = self.client.role
            if role not in roles:
                print(f'This process need {roles}')
                raise exceptions.UnauthorizedOperationError
            return func(self, *args, **kwargs)
        return __protect
    return _protect


def save_image_file(file_name, ext, content):
    with open('.'.join([file_name, ext]), 'wb') as f:
        f.write(content)


def is_connect_net():
    pass
