# encoding: utf-8
from __future__ import print_function, division, absolute_import

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, LargeBinary, ForeignKey, Float, DateTime,
                        UniqueConstraint, Date, Index, Table)
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()


class SiteDbo(Base):

    __tablename__ = 'site'

    site_id = Column(Integer(), primary_key=True)
    name = Column(String(), unique=True, index=True, nullable=False)
    description = Column(String())
    street = Column(String())
    postcode = Column(String())
    city = Column(String())
    coord_x = Column(String())
    coord_y = Column(String())
    coord_z = Column(String())

    def __str__(self):
        return ("<SiteDbo name={name}, city={city}, x={coord_x}, y={coord_y}, "
                "z={coord_z}, description={description}>").format(**vars(self))


class SignalCommentAssociation(Base):

    __tablename__ = 'signals_comments_association'

    signal_id = Column(Integer, ForeignKey('signal.signal_id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comment.comment_id'), primary_key=True)
    signal = relationship("SignalDbo", back_populates="comments")
    comment = relationship("CommentDbo", back_populates="signals")


class SignalSignalQualityAssociation(Base):

    __tablename__ = 'signals_signal_quality_association'

    signal_id = Column(Integer, ForeignKey('signal.signal_id'), primary_key=True)
    signal_quality_id = Column(Integer, ForeignKey('signal_quality.signal_quality_id'), primary_key=True)
    signal = relationship("SignalDbo", back_populates="signal_qualities")
    signal_quality = relationship("SignalQualityDbo", back_populates="signals")



class SignalDbo(Base):
    """(formerly known as fact table)
    Contains the measured value of a given parameter taken a at a specific time, site
    """

    __tablename__ = 'signal'

    signal_id = Column(Integer(), primary_key=True)
    value = Column(Float(), nullable=False)
    timestamp = Column(DateTime(), nullable=False)

    parameter_id = Column(ForeignKey("parameter.parameter_id"), nullable=False)
    source_id = Column(ForeignKey("source.source_id"), nullable=False)
    site_id = Column(ForeignKey("site.site_id"), nullable=True)

    coord_x = Column(String())
    coord_y = Column(String())
    coord_z = Column(String())

    site = relationship("SiteDbo", backref=backref("signals"))
    source = relationship("SourceDbo", backref=backref("signals"))
    parameter = relationship("ParameterDbo", backref=backref("signals"))

    comments = relationship("SignalCommentAssociation", back_populates="signal")
    signal_qualities = relationship("SignalSignalQualityAssociation", back_populates="signal")

    __table_args__ = (Index("signal_index", "coord_x", "coord_y", "coord_z",
                            "site_id", "parameter_id", "source_id"), )

    def __str__(self):
        return ("<SourceDbo signal_id={signal_id}, parameter_id={parameter_id}, "
                "value={value}, timestamp={timestamp}, site={site_id}>").format(**vars(self))

    def resolved_columns(self):
        return (self.signal_id, self.timestamp, self.value, self.parameter.name, self.source.name,
                getattr(self.site, "name", ""), self.coord_x, self.coord_y, self.coord_z)

    @staticmethod
    def resolved_column_names():
        return ("id", "timestamp", "value", "parameter", "source", "site", "x", "y", "z")


class PictureDbo(Base):

    __tablename__ = 'picture'

    picture_id = Column(Integer(), primary_key=True)
    site_id = Column(ForeignKey("site.site_id"), nullable=False)
    filename = Column(String(), nullable=False)
    description = Column(String())
    timestamp = Column(DateTime())
    data = Column(LargeBinary())

    site = relationship("SiteDbo", backref=backref("pictures"))
    constraint = UniqueConstraint('site_id', 'filename')

    def __str__(self):
        return ("<PictureDbo filename={filename}, timestamp={timestamp}, "
                "description={description}>").format(**vars(self))


class SourceDbo(Base):

    __tablename__ = 'source'

    source_id = Column(Integer(), primary_key=True)
    source_type_id = Column(ForeignKey("source_type.source_type_id"), nullable=False)
    name = Column(String(), unique=True, index=True, nullable=False)
    description = Column(String())
    serial = Column(String())
    manufacturer = Column(String())
    manufacturing_date = Column(Date())

    source_type = relationship("SourceTypeDbo", backref=backref("sources"))

    def __str__(self):
        return ("<SourceDbo name={name}, serial={serial}, "
                "description={description}>").format(**vars(self))


class SourceTypeDbo(Base):

    __tablename__ = 'source_type'

    source_type_id = Column(Integer(), primary_key=True)
    name = Column(String(), unique=True, index=True, nullable=False)
    description = Column(String())

    def __str__(self):
        return "<SourceTypeDbo name={name}, description={description}>".format(**vars(self))


class SpecialValueDefinitionDbo(Base):

    __tablename__ = 'special_value_definition'

    special_value_definition_id = Column(Integer(), primary_key=True)
    source_type_id = Column(ForeignKey("source_type.source_type_id"), nullable=False)
    description = Column(String())
    categorical_value = Column(String(), nullable=False)
    numerical_value = Column(Float(), nullable=False)

    source_type = relationship("SourceTypeDbo", backref=backref("special_values"))

    def __str__(self):
        return ("<SpecialValueDefinitionDbo categorical_value={categorical_value}, "
                "numerical_value={numerical_value}>").format(**vars(self))


class ParameterDbo(Base):

    __tablename__ = 'parameter'

    parameter_id = Column(Integer(), primary_key=True)
    name = Column(String(), unique=True, index=True, nullable=False)
    description = Column(String())
    unit = Column(String(), nullable=False)

    def __str__(self):
        return ("<ParameterDbo name={name}, unit={unit}, description={description}>"
                .format(**vars(self)))


class ParameterAveragingDbo(Base):

    __tablename__ = 'parameter_averaging'

    parameter_averaging_id = Column(Integer(), primary_key=True)
    parameter_id = Column(ForeignKey("parameter.parameter_id"), nullable=False)
    source_id = Column(ForeignKey("source.source_id"), nullable=False)
    integration_length_x = Column(Float())
    integration_length_y = Column(Float())
    integration_angle = Column(Float())
    integration_time = Column(Float())

    constraint = UniqueConstraint('parameter_id', 'source_id')

    parameter = relationship("ParameterDbo", backref=backref("averaging"))
    source = relationship("SourceDbo", backref=backref("averaging"))


class CommentDbo(Base):

    __tablename__ = 'comment'

    comment_id = Column(Integer(), primary_key=True)
    signal_id = Column(ForeignKey("signal.signal_id"), nullable=False)
    text = Column(String(), nullable=False)
    timestamp = Column(DateTime(), nullable=False, default=datetime.now())
    author = Column(String())

    signals = relationship("SignalCommentAssociation", back_populates="comment")


class SignalQualityDbo(Base):

    __tablename__ = 'signal_quality'

    signal_quality_id = Column(Integer(), primary_key=True)
    signal_id = Column(ForeignKey("signal.signal_id"), nullable=False)
    quality_id = Column(ForeignKey("quality.quality_id"), nullable=False)
    timestamp = Column(DateTime(), nullable=False, default=datetime.now())
    author = Column(String())

    signals = relationship("SignalSignalQualityAssociation", back_populates="signal_quality")


class QualityDbo(Base):

    __tablename__ = 'quality'

    quality_id = Column(Integer(), primary_key=True)
    flag = Column(String(), nullable=False)
    method = Column(String())


class ProjectDbo(Base):

    __tablename__ = 'project'

    project_id = Column(Integer(), primary_key=True)
    title = Column(String(), nullable=False)
    description = Column(String())
