from sqlalchemy import Column, PrimaryKeyConstraint, Table
from sqlalchemy.ext.declarative.base import declared_attr

__author__ = 'H.D. "Chip" McCullough IV'

# class AutoTable(object):
#     @classmethod
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__
#
#     @classmethod
#     def __table_cls__(cls, *args, **kwargs):
#         for obj in args[1:]:
#             if (isinstance(obj, Column) and obj.primary_key) \
#                     or (isinstance(obj, PrimaryKeyConstraint)):
#                 return Table(*args, **kwargs)
#
#         return None