"""
    User classes & helpers
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import sqlite3
import os
import binascii
import hashlib
from functools import wraps

from flask import current_app
from flask_login import current_user


class UserManager(object):

    def __init__(self, defaultAuthenticationMethod = "hash", path="."):
        self.defaultAuthenticationMethod = defaultAuthenticationMethod
        self.path = path
    def database(f):
        def _exec(self, *args, **argd):
            connection = sqlite3.connect(self.path + '/users.db')
            connection.execute("PRAGMA foreign_keys = ON")

            cursor = connection.cursor()

            returnVal = None

            try:
                cursor.execute('''create table if not exists Users 
                              (name TEXT PRIMARY KEY, password TEXT, 
                              authenticated INTEGER, active INTEGER, 
                              authentication_method TEXT)''')

                cursor.execute('''create table if not exists Roles 
                              (name TEXT, role TEXT, PRIMARY KEY (name, role), 
                              FOREIGN KEY(name) REFERENCES Users(name) ON DELETE CASCADE)''')

                returnVal = f(self, cursor, *args, **argd)
            except Exception, e:
                connection.rollback()
                raise
            else:
                connection.commit()  # or maybe not
            finally:
                connection.close()

            return returnVal

        return _exec


    @database
    def add_user(self, cursor, name, password, active=True, roles=[], authentication_method=None):

        if self.get_user(name) != None:
            return False

        dbpassword = ""
        if authentication_method is None:
            authentication_method = self.defaultAuthenticationMethod
        if authentication_method == 'hash':
            dbpassword = make_salted_hash(password)
        elif authentication_method == 'cleartext':
            dbpassword = password
        else:
            raise NotImplementedError(authentication_method)

        cursor.execute('INSERT INTO Users VALUES (?,?,?,?,?)', (name, dbpassword, False, active, authentication_method))
        for role in roles:
            cursor.execute('INSERT INTO Roles VALUES (?,?)', (name, role))


    @database
    def get_user(self, cursor, name):
        cursor.execute('SELECT * FROM Users WHERE name=?', (name,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            cursor.execute('SELECT * FROM Roles WHERE name=?', (name,))
            roleRows = cursor.fetchall()
            roles=[]
            for role in roleRows:
                roles.append(role[1])

            data = {};
            data["password"] = user[1]
            data["authenticated"] = user[2]
            data["active"] = user[3]
            data["authentication_method"] = user[4]
            data["roles"] = roles

            return User(self, user[0], data)

    @database
    def delete_user(self, cursor, name):
        cursor.execute('DELETE FROM Users WHERE name=?', (name,))
        if cursor.rowcount == 0:
            return False
        return True

    @database
    def update(self, cursor, name, userdata):

        pw = userdata["password"]
        auth = userdata["authenticated"]
        active = userdata["active"]
        authmethod = userdata["authentication_method"]
        roles = userdata["roles"]

        cursor.execute('''
        UPDATE Users
        SET password = ?, authenticated = ?,
            active = ?, authentication_method = ? 
        WHERE name = ?
        ''', (pw, auth, active, authmethod, name))

        cursor.execute('DELETE FROM Roles WHERE name=?', (name,))

        for role in roles:
            cursor.execute('INSERT INTO Roles VALUES (?,?)', (name, role))


class User(object):
    def __init__(self, manager, name, data):
        self.manager = manager
        self.name = name
        self.data = data

    def get(self, option):
        return self.data.get(option)

    def set(self, option, value):
        self.data[option] = value
        self.save()

    def save(self):
        self.manager.update(self.name, self.data)

    def is_authenticated(self):
        return self.data.get('authenticated')

    def is_active(self):
        return self.data.get('active')

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name

    def check_password(self, password):
        """Return True, return False, or raise NotImplementedError if the
        authentication_method is missing or unknown."""
        authentication_method = self.data.get('authentication_method', None)
        if authentication_method is None:
            authentication_method = self.manager.authentication_method
        # See comment in UserManager.add_user about authentication_method.
        if authentication_method == 'hash':
            result = check_hashed_password(password, self.get('hash'))
        elif authentication_method == 'cleartext':
            result = (self.get('password') == password)
        else:
            raise NotImplementedError(authentication_method)
        return result


def make_salted_hash(password, salt=None):
    if not salt:
        salt = os.urandom(64)
    d = hashlib.sha512()
    d.update(salt[:32])
    d.update(password)
    d.update(salt[32:])
    return binascii.hexlify(salt) + d.hexdigest()


def check_hashed_password(password, salted_hash):
    salt = binascii.unhexlify(salted_hash[:128])
    return make_salted_hash(password, salt) == salted_hash


def protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_app.config.get('PRIVATE') and not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)
    return wrapper

