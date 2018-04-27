# coding: utf-8
from sqlalchemy import (Column, Integer, Unicode, DateTime, LargeBinary,
                        ForeignKey, create_engine, or_, and_)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import sessionmaker, relationship

from uuid import uuid4
from datetime import datetime
import json


@as_declarative()
class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class MonitorState(Base):
    monitor = Column(Unicode(50), nullable=False, unique=True)
    content = Column(LargeBinary(), nullable=False, default='{}')

    @classmethod
    def get_for_monitor(cls, session, monitor):
        state = (session
                    .query(cls)
                    .filter_by(monitor=monitor)
                    .one_or_none())

        return json.loads(state.content if state else '{}')

    @classmethod
    def set_for_monitor(cls, session, monitor, data):
        state = (session
                    .query(cls)
                    .filter_by(monitor=monitor)
                    .one_or_none())

        if not state:
            state = MonitorState()
            state.monitor = monitor
            session.add(state)

        state.content = json.dumps(data)


class MissingSinceTriggerState(Base):
    monitor = Column(Unicode(50), nullable=False, unique=True)
    last_triggered = Column(DateTime(), nullable=True, default=None)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def set_for_monitor(cls, session, monitor, last_triggered):
        state = (session
                    .query(cls)
                    .filter_by(monitor=monitor)
                    .one_or_none())

        if not state:
            state = cls()
            state.monitor = monitor
            session.add(state)

        state.last_triggered = last_triggered


class Event(Base):
    type = Column(Unicode(50), nullable=False)
    datetime = Column(DateTime(), nullable=False, default=datetime.now)
    body = Column(LargeBinary(), nullable=False)

    def __init__(self, session, type, data):
        self.type = type
        self.data = data
        session.add(self)

    def _get_data(self):
        return json.loads(self.body)

    def _set_data(self, data):
        self.body = json.dumps(data)

    data = property(_get_data, _set_data)

    @classmethod
    def get_by_filter(cls, session, filter, since, until):
        q = session.query(cls)

        if filter:
            terms = [t for t in filter.split(' ') if t]
            q = q.filter(or_(
                    and_(*(Event.type.contains(t) for t in terms)),
                    and_(*(Event.body.contains(t) for t in terms))))
        if since:
            q = q.filter(Event.id > since)
        if until:
            q = q.filter(Event.id < until)

        return q.order_by(Event.datetime.desc())

    @classmethod
    def get_last_executions(cls, session, types):
        return (session
                    .query(
                        cls.type,
                        func.max(cls.datetime)
                    )
                    .group_by(cls.type)
                    .filter(cls.type.in_(types))
                    .all())


class QueuedExecution(Base):
    monitor = Column(Unicode(50), nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship(Event, primaryjoin=(event_id == Event.id))

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    def __init__(self, session, monitor, event):
        self.monitor = monitor
        self.event = event
        session.add(self)


def create_all(url):
    engine = create_engine(url)
    Base.metadata.create_all(engine)


def create_session_factory(url):
    return sessionmaker(bind=create_engine(url))
