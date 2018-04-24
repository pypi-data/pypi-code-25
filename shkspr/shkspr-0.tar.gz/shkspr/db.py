import os
import pymongo
import secrets
import hashlib


TOKEN_SIZE = 64
SALT_SIZE = 64
HASH_ALG = hashlib.sha512


class MongoDataBase:
    def __init__(self):
        MONGO_URL = os.environ.get('MONGODB_URI',
                                   "mongodb://localhost:27017/shakespeare")
        dbname = MONGO_URL.split('/')[-1]
        self.db = pymongo.MongoClient(MONGO_URL)[dbname]

    def login_user(self, uname, pwd):
        cred = self.db.credentials.find_one({"uname": uname})
        if cred is None:
            return False, None
        data = cred['salt'] + pwd.encode()
        hsh = HASH_ALG(data).digest()
        if hsh != cred['hsh']:
            return False, None
        token = secrets.token_bytes(TOKEN_SIZE)
        self.db.tokens.insert_one({"token": token,
                                   "uname": uname})
        return True, token

    def logout_user(self, token):
        # NOTE: Providing the uname too makes it harder
        # To brute force the logout
        self.db.tokens.find_one_and_delete({"token": token})

    def create_user(self, uname, pwd):
        if self.db.credentials.find_one({"uname": uname}) is not None:
            return False, 'User exists'
        salt = secrets.token_bytes(SALT_SIZE)
        data = salt + pwd.encode()
        hsh = HASH_ALG(data).digest()
        self.db.credentials.insert_one({"uname": uname,
                                        "hsh": hsh,
                                        "salt": salt})
        return True, 'ok'

    def is_logged_in(self, token):
        return self.db.tokens.find_one({"token": token}) is not None


DB = MongoDataBase()
