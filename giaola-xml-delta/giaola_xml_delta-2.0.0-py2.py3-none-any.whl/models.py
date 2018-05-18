#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String, Unicode, Integer, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


def update_updated_count(context):
    count = context.current_parameters['updated_count'] or 0
    return count + 1

class ListingBaseMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    storage_key = Column(String(100), primary_key=True, index=True)
    type = Column(String(20), primary_key=True, index=True)
    network_key = Column(String(20))
    data = Column(JSON)

    sent = Column(Boolean, default=False)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return "<Change(id='%s')>" % (self.storage_key)

    @classmethod
    def factory(cls, storage_key, network_key, type, data):
        storage_key = '-'.join([data.get(key) for key in storage_key.split(',')])
        network_key = str(data.get(network_key))
        return cls(storage_key=storage_key, network_key=network_key, type=type, data=data)


class Listing(ListingBaseMixin, Base):
    pass


class ListingTemp(ListingBaseMixin, Base):
    pass


class NetworkError(Base):
    __tablename__ = 'network_error'

    id = Column(Integer, primary_key=True)

    url = Column(String(200))
    method = Column(String(50))
    headers = Column(JSON)
    json = Column(JSON)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def factory(cls, method, url, headers, body):
        return cls(method=method,
                   url=url,
                   headers=headers,
                   json=body)
