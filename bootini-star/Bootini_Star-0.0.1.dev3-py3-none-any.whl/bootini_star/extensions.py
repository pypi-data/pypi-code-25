"""
Defining some objects here avoids circular imports.
"""
__author__ = 'Ralph Seichter'

import logging
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('bootini_star')
log.setLevel(logging.INFO)

login_manager = LoginManager()

db = SQLAlchemy()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])
