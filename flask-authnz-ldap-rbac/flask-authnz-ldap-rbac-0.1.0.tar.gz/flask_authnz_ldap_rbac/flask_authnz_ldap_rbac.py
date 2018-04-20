from flask import request, abort

DEFAULT_GROUPS_VARIABLE = 'AUTHENTICATE_MEMBEROF'
DEFAULT_WRITE_METHODS = ['PUT', 'POST', 'DELETE', 'PATCH']
DEFAULT_READ_METHODS = ['OPTIONS', 'GET', 'HEAD']
DEFAULT_WRITE_GROUPS = []
DEFAULT_READ_GROUPS = ['ANY']


class GroupRBAC(object):
    """
    Enforces membership in a given LDAP group.

    :param app: The Flask app to be protected
    :param groups_variable: The environment variable that contains a list of the autenticated user's groups. Default: AUTHENTICATE_MEMBEROF
    :param write_methods: HTTP 'write' methods. Default: 'PUT', 'POST', 'DELETE', 'PATCH'
    :param read_methods: HTTP 'read' methods. Default: 'OPTIONS', 'GET', 'HEAD'
    :param write_groups: Groups allowed to make requests with 'write' methods. Default: None.
    :param read_groups: Groups allowed to make requests with 'read' methods. Default: ANY.

    The special group names 'ANY' and 'ANONYMOUS' allow any authenticated user, or unauthenticated users, respectively.
    """
    def __init__(self, app=None, **kwargs):
        self.app = app
        if app:
            self.init_app(app)

        self.groups_var = kwargs.get('groups_variable', DEFAULT_GROUPS_VARIABLE)
        self.write_methods = kwargs.get('write_methods', DEFAULT_WRITE_METHODS)
        self.read_methods = kwargs.get('read_methods', DEFAULT_READ_METHODS)
        self.write_groups = set(kwargs.get('write_groups', DEFAULT_WRITE_GROUPS))
        self.read_groups = set(kwargs.get('read_groups', DEFAULT_READ_GROUPS))

    def init_app(self, app):
        app.before_request(self._authorize)

    def _authorize(self):
        if request.method in self.write_methods:
            self._check_membership(self.write_groups)
        elif request.method in self.read_methods:
            self._check_membership(self.read_groups)
        else:
            abort(403)

    def _check_membership(self, grouplist):
        groups = request.environ.get(self.groups_var, None)

        if groups:
            if 'ANY' in grouplist:
                # Allow if method allows any authenticated user
                return

            groups = set(groups.split('; '))
            if len(groups.intersection(grouplist)):
                # Allow if member is in one or more required groups
                return

        if 'ANONYMOUS' in grouplist:
            # Allow if anonymous access is allowed
            return

        # Deny by default
        abort(403)
