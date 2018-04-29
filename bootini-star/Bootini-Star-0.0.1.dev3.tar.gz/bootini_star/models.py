"""
Model classes and related helper functions. SQLAlchemy is used for ORM.
"""
__author__ = 'Ralph Seichter'

import json

import flask_login
from sqlalchemy import Column, DateTime, String, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from .extensions import db, log, login_manager, pwd_context


class utcnow(expression.FunctionElement):
    """Used by SQLAlchemy."""
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kwargs):
    """
    Return statement representing 'UTC now' in PostgreSQL dialect.
    Used by SQLAlchemy.
    """
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'mssql')
def mssql_utcnow(element, compiler, **kwargs):
    """
    Return statement representing 'UTC now' in Microsoft SQL Server dialect.
    Used by SQLAlchemy.
    """
    return 'GETUTCDATE()'


@compiles(utcnow, 'mysql')
def mysql_utcnow(element, compiler, **kwargs):
    """
    Return statement representing 'UTC now' in MySQL dialect.
    Used by SQLAlchemy.
    """
    return 'CURRENT_TIMESTAMP()'


class User(db.Model, flask_login.UserMixin):
    """
    Model class representing an application user.

    :type email: str
    :param email: Email address

    :type password: str
    :param password: Cleartext password

    :type uuid: str
    :param uuid: Unique string
    """
    __tablename__ = "users"

    email = Column(String(100), primary_key=True, nullable=False)
    password = Column(String(250), nullable=False)
    uuid = Column(String(40), nullable=False, unique=True)
    registered_at = Column(DateTime, nullable=False, server_default=utcnow())
    level = Column(SmallInteger, nullable=False, server_default='1')
    eve_characters = relationship('Character', backref='user', lazy=True)

    def __init__(self, email, password, uuid):
        self.email = email
        self.password = pwd_context.hash(password)
        self.uuid = uuid
        self.current_character = None

    # Required for flask_login
    def get_id(self):
        """Use email as ID (method required by Flask-Login)."""
        return self.email

    @property
    def current_character(self):
        return self.__current_character

    @current_character.setter
    def current_character(self, x):
        if not x or isinstance(x, Character):
            self.__current_character = x
        else:
            raise TypeError("expected argument of type '" +
                            Character.__name__ + "', found '" + x.__class__.__name__ + "'.")

    def load_character(self, character_id):
        self.current_character = character_loader(
            character_id, owner=self.uuid)
        return self.current_character


@login_manager.user_loader
def user_loader(email):
    """Load user from DB, return None if not found."""
    try:
        return User.query.filter_by(email=email).first()
    except:
        return None


class Character(db.Model):
    """
    Model class representing an EVE Online player character. Each application
    user can own multiple player characters. Character names are unique, but
    each character still has a technical ID.

    :type owner: str
    :param owner: Owner's UUID.

    :type id: int
    :param id: Character ID.

    :type name: str
    :param name: Character name.

    :type owner_hash: str
    :param owner_hash: Identifies the character owner for CCP.
    """
    __tablename__ = "characters"

    # Each EVE character is owned by an application user.
    owner = Column(String(40), ForeignKey('users.uuid'), nullable=False)
    # Use ESI character ID as primary key.
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    owner_hash = Column(String(50), nullable=False)
    # SSO authentication token data
    token_str = Column('token', String(500))

    def __init__(self, owner, id, name, owner_hash):
        self.owner = owner
        self.id = id
        self.name = name
        self.owner_hash = owner_hash

    def set_token(self, token_dict):
        """
        Store access token dictionary.

        :type token_dict: dict
        :param token_dict: Access token dictionary.
        """
        self.token_str = json.dumps(token_dict)

    def token_dict(self):
        """Retrieve access token dictionary."""
        return json.loads(self.token_str)


def character_loader(id, **kwargs):
    """Load a Character object."""
    try:
        log.debug('Load character ID=' + str(id))
        return Character.query.filter_by(id=id, **kwargs).first()
    except:
        return None


def character_list_loader(owner):
    """
    Load all Character objects for the given owner.

    :type owner: str
    :param owner: Owner's UUID.
    """
    return Character.query.filter_by(owner=owner).all()
