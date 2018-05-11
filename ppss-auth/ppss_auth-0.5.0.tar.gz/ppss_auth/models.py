from sqlalchemy import (
    Table,
    Column,
    Index,
    Integer,
    Text,
    Unicode,UnicodeText,
    DateTime,
    ForeignKey,
    desc, asc,UniqueConstraint
)
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

from datetime import datetime,timedelta

import logging,uuid,hashlib

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

from constants import Conf


l = logging.getLogger('ppssauth.models')


def initdb(session,createdefault=False):
    Base.metadata.create_all(session.get_bind() )
    if createdefault:
        user = PPSsuser(username = u'admin').setPassword(u'admin')
        group = PPSsgroup(name = u"admin")
        perm = PPSspermission(name = u"admin")
        user.groups.append(group)
        group.permissions.append(perm) 
        session.add(user)
        session.add(group)
        session.add(perm)
        return user,group
    return None,None

ppssuserlkppssgroup = Table('ppssuser_lk_ppssgroup', Base.metadata,
    Column('user_id',UnicodeText,ForeignKey('ppss_user.id')),
    Column('group_id',Integer,ForeignKey('ppss_group.id') )
)
ppssgrouplkppsspermission = Table('ppssgroup_lk_ppsspermission', Base.metadata,
    Column('group_id',UnicodeText,ForeignKey('ppss_group.id')),
    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
)
#ppssuserlkppsspermission = Table('ppssuser_lk_ppsspermission', Base.metadata,
#    Column('user_id',UnicodeText,ForeignKey('ppss_user.id')),
#    Column('permission_id',Integer,ForeignKey('ppss_permission.id') )
#)


class PPSsuser(Base):
    __tablename__   = 'ppss_user'
    id              = Column(Integer, primary_key=True)
    username        = Column(Unicode(128))
    password        = Column(Unicode(1024))
    creationdt      = Column(DateTime,default=datetime.now())
    lastlogin       = Column(DateTime)
    enabled         = Column(Integer,default=1)
    magicnumber     = Column(Text(),default=uuid.uuid5(uuid.uuid4(),"bidibibodibibu" ).hex )   #Conf.saltforhash
    createdby       = Column(Integer)
    disabledby      = Column(Integer)

    groups = relationship("PPSsgroup",secondary=ppssuserlkppssgroup, backref=backref('users'))

    @classmethod
    def checkLogin(cls,user,password,dbsession):
        s = hashlib.sha512(password)
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==s.hexdigest()).all()
        return res[0] if len(res)==1 else None

    @classmethod
    def checkCryptedLogin(cls,user,password,dbsession):
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==password).all()
        return res[0] if len(res)==1 else None

    def setPassword(self,password):
        s = hashlib.sha512(password)
        self.password=s.hexdigest()
        return self

class PPSsgroup(Base):
    __tablename__   = 'ppss_group'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))
    enabled= Column(Integer,default=1)
    
    permissions = relationship("PPSspermission",secondary=ppssgrouplkppsspermission  ,backref=backref('groups'))

class PPSspermission(Base):
    __tablename__   = 'ppss_permission'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128))

