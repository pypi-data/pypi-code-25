import hashlib

from auth.auth_exceptions import UserAlreadyExistException, UserNotExistException, \
    PasswordMissmatchException, PasswordTooShortException, NotLoggedInError, NotPermittedError

class User:

    def __init__(self, username, password):
        self.username = username
        self.pwd = self.encr_pwd(password)
        self.logged_in = False

    def encr_pwd(self, password):
        '''
        Encrypt the password with the username and return
        the sha digest.
        '''
        hash_string = (self.username + password)
        hash_string = hash_string.encode("utf8")
        return hashlib.sha256(hash_string).hexdigest()

    def check_pwd(self, string):
        encrypted = self.encr_pwd(string)
        return encrypted == self.pwd


class Authenticator:
    """
    Logged in/out user, add user to auth system
    """

    def __init__(self):
        self.auth_users = {}

    def login(self, username, password):
        try:
            user = self.auth_users[username]
        except KeyError:
            raise UserNotExistException
        else:
            if not user.check_pwd(password):
                raise PasswordMissmatchException(username)
            user.logged_in = True
            return True

    def add_user(self, username, password):
        if username in self.auth_users:
            raise UserAlreadyExistException(username)
        if len(password) < 6:
            raise PasswordTooShortException(username)
        self.auth_users[username] = User(username, password)

    def is_logged_in(self, username):
        if username in self.auth_users:
            return self.auth_users[username].logged_in
        return False

authenticator = Authenticator()

class Authorizator:

    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.permissions = {}

    def create_perm(self, perm_name):
        try:
            perm_set = self.permissions[perm_name]
        except KeyError:
            self.permissions[perm_name] = set()

    def grant_permission(self, username, perm_name):
        try:
            perm_set = self.permissions[perm_name]
        except KeyError:
            raise PermissionError('Permisson doesn\'t exist')
        else:
            if username not in self.authenticator.auth_users:
                raise UserNotExistException(username)
            perm_set.add(username)

    def check_permisson(self, username, perm_name):
        if not self.authenticator.is_logged_in(username):
            raise NotLoggedInError(username)
        try:
            perm_set = self.permissions[perm_name]
        except KeyError:
            raise PermissionError('Permisson doesn\'t exist')
        else:
            if not username in perm_set:
                raise NotPermittedError(username, perm_name)
            return True

authorizator = Authorizator(authenticator)
