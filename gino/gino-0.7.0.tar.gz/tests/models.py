import os
import enum
import random
import string
from datetime import datetime

from gino import Gino
from gino.dialects.asyncpg import JSONB

DB_ARGS = dict(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASS', ''),
    database=os.getenv('DB_NAME', 'postgres'),
)
PG_URL = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
    **DB_ARGS)
db = Gino()


def random_name(length=8) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


class UserType(enum.Enum):
    USER = 'USER'


class User(db.Model):
    __tablename__ = 'gino_users'

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column(db.Unicode(), default='noname')
    profile = db.Column(JSONB(), nullable=False, server_default='{}')
    type = db.Column(
        db.Enum(UserType),
        nullable=False,
        default=UserType.USER,
    )
    name = db.StringProperty()
    age = db.IntegerProperty(default=18)
    balance = db.IntegerProperty(default=0)
    birthday = db.DateTimeProperty(
        default=lambda i: datetime.utcfromtimestamp(0))
    team_id = db.Column(db.ForeignKey('gino_teams.id'))

    @balance.after_get
    def balance(self, val):
        if val is None:
            return 0.0
        return float(val)

    def __repr__(self):
        return '{}<{}>'.format(self.nickname, self.id)


class Friendship(db.Model):
    __tablename__ = 'gino_friendship'

    my_id = db.Column(db.BigInteger(), primary_key=True)
    friend_id = db.Column(db.BigInteger(), primary_key=True)

    def __repr__(self):
        return 'Friends<{}, {}>'.format(self.my_id, self.friend_id)


class Relation(db.Model):
    __tablename__ = 'gino_relation'

    name = db.Column(db.Text(), primary_key=True)


class Team(db.Model):
    __tablename__ = 'gino_teams'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(), default=random_name)
    parent_id = db.Column(db.ForeignKey('gino_teams.id'))
    company_id = db.Column(db.ForeignKey('gino_companies.id'))


class Company(db.Model):
    __tablename__ = 'gino_companies'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(), default=random_name)


def qsize(engine):
    # noinspection PyProtectedMember
    return engine.raw_pool._queue.qsize()
