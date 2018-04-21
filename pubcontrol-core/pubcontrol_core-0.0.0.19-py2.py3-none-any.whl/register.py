from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DATETIME, BLOB, BigInteger, Table, and_, UnicodeText

from sqlalchemy.types import Integer
from sqlalchemy.dialects import mysql, sqlite
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.dialects.sqlite import BLOB

from jutil.processing import DictQuery
from jutil.database.sqlalchemy import get_or_create, filter_string_junction, add_elements

from pubcontrol.database import MySQLDatabase, BASE, LongBlob, BigInt

import datetime

from abc import abstractmethod


publication_author_junction = Table(
    'publication_author_junction',
    BASE.metadata,
    Column('authorID', BigInt, ForeignKey('author.authorID'), primary_key=True),
    Column('publicationID', BigInt, ForeignKey('publication.publicationID'), primary_key=True)
)

publication_tag_junction = Table(
    'publication_tag_junction',
    BASE.metadata,
    Column('publicationID', BigInt, ForeignKey('publication.publicationID'), primary_key=True),
    Column('tagID', BigInt, ForeignKey('tag.tagID'), primary_key=True)
)

publication_category_junction = Table(
    'publication_category_junction',
    BASE.metadata,
    Column('publicationID', BigInt, ForeignKey('publication.publicationID'), primary_key=True),
    Column('CategoryID', BigInt, ForeignKey('category.categoryID'), primary_key=True)
)

publication_citation_junction = Table(
    'publication_citation_junction',
    BASE.metadata,
    Column('publicationID', BigInt, ForeignKey('publication.publicationID'), primary_key=True),
    Column('citationID', BigInt, ForeignKey('publication.publicationID'), primary_key=True)
)


class Publication(BASE):

    __tablename__ = 'publication'
    #__table_args__ = {'sqlite_autoincrement': True}

    publicationID = Column(BigInt, primary_key=True)
    doi = Column(String(200))
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    published = Column(DATETIME)

    originID = Column(BigInt, ForeignKey('origin.originID'))
    journalID = Column(BigInt, ForeignKey('journal.journalID'))
    collaborationID = Column(BigInt, ForeignKey('collaboration.collaborationID'))

    origin = relationship(
        'Origin',
        uselist=False,
        back_populates='publication',
    )
    collaboration = relationship(
        'Collaboration',
        uselist=False,
        back_populates='publications'
    )
    journal = relationship(
        'Journal',
        uselist=False,
        back_populates='publications'
    )
    authors = relationship(
        "Author",
        secondary=publication_author_junction,
        back_populates='publications'
    )
    categories = relationship(
        'Category',
        secondary=publication_category_junction,
        back_populates='publications'
    )
    tags = relationship(
        'Tag',
        secondary=publication_tag_junction,
        back_populates='publications'
    )
    citedby = relationship(
        'Publication',
        secondary=publication_citation_junction,
        primaryjoin='Publication.publicationID == publication_citation_junction.c.publicationID',
        secondaryjoin='Publication.publicationID == publication_citation_junction.c.citationID'
    )

    def add_citation(self, publication):
        if publication not in self.citedby:
            self.citedby.append(publication)


class Author(BASE):

    __tablename__ = 'author'
    #__table_args__ = {'sqlite_autoincrement': True}

    authorID = Column(BigInt, primary_key=True)
    first_name = Column(UnicodeText)
    last_name = Column(UnicodeText)

    publications = relationship(
        'Publication',
        secondary=publication_author_junction,
        back_populates='authors'
    )


class Collaboration(BASE):

    __tablename__ = 'collaboration'

    collaborationID = Column(BigInt, primary_key=True)
    name = Column(UnicodeText)

    publications = relationship(
        'Publication',
        back_populates='collaboration'
    )


class Tag(BASE):

    __tablename__ = 'tag'
    #__table_args__ = {'sqlite_autoincrement': True}

    tagID = Column(BigInt, primary_key=True)
    content = Column(UnicodeText)
    description = Column(String(500))

    publications = relationship(
        'Publication',
        secondary=publication_tag_junction,
        back_populates='tags'
    )


class Journal(BASE):

    __tablename__ = 'journal'
    #__table_args__ = {'sqlite_autoincrement': True}

    journalID = Column(BigInt, primary_key=True)
    name = Column(String(500))
    volume = Column(String(200))

    publications = relationship(
        'Publication',
        back_populates='journal'
    )


class Category(BASE):

    __tablename__ = 'category'
    #__table_args__ = {'sqlite_autoincrement': True}

    categoryID = Column(BigInt, primary_key=True)
    content = Column(UnicodeText)
    description = Column(String(500))

    publications = relationship(
        'Publication',
        secondary=publication_category_junction,
        back_populates='categories'
    )


class Origin(BASE):

    __tablename__ = 'origin'
    #__table_args__ = {'sqlite_autoincrement': True}

    originID = Column(BigInt, primary_key=True)
    id = Column(BigInteger)
    type = Column(String(300))
    name = Column(String(300))
    text = Column(Text)
    fetched = Column(DATETIME)
    raw = Column(LongBlob)

    publication = relationship(
        'Publication',
        back_populates='origin'
    )


class Register:
    """
    ABSTRACT BASE CLASS
    """

    @abstractmethod
    def insert_publication(self, obj):
        pass


class PublicationRegister(Register):

    def __init__(self, publication_builder_class, database_singleton_class):
        self.publication_builder_class = publication_builder_class
        self.database_class = database_singleton_class

        self.database = self.database_class()
        self.publication_builder = self.publication_builder_class(self.database)

    def insert_publication(self, obj):
        """
        CHANGELOG

        Removed the session.commit()
        :param obj:
        :return:
        """
        self.publication_builder.set(obj)
        publication = self.publication_builder.get()
        self.database.session.add(publication)
        self.database.session.commit()

    def select_by_origin(self, origin_name, origin_id):
        """
        CHANGELOG

        Added 14.04.2018
        A method to select publications by their secondary information about the origin id and type

        :param origin_name:
        :param origin_id:
        :return:
        """
        return self.database.session.query(Publication).\
            join(Publication.origin).\
            filter(and_(Origin.name == origin_name, Origin.id == origin_id)).all()

    def select_publication(self, publication_id):
        return self.database.session.query(Publication).filter(Publication.publicationID == publication_id).first()

    def query(self, *args, **kwargs):
        return self.database.session.query(*args, **kwargs)


class PublicationBuilder:
    """
    ABSTRACT BASE CLASS
    """
    @abstractmethod
    def set(self, obj):
        pass

    @abstractmethod
    def get(self):
        pass


class DictPublicationBuilder(DictQuery, PublicationBuilder):

    def __init__(self, database):
        DictQuery.__init__(self)
        self.database = database
        self.publication = None

        self.remaining_citations = {}

    def set(self, publication_dict):
        self.set_query_dict(publication_dict)

    def get(self):
        self.process()
        return self.publication

    @property
    def session(self):
        return self.database.session

    def query_exception(self, query, query_dict, default):
        return default

    def process(self):
        self.publication = Publication(
            doi=self.query_dict('doi', ''),
            title=self.query_dict('title', ''),
            description=self.query_dict('description', ''),
            published=self.query_dict('published', datetime.datetime.now())
        )
        self.publication.collaboration = self.collaboration()
        self.publication.origin = self.origin()
        self.publication.journal = self.journal()
        add_elements(self.publication.tags, self.tags())
        add_elements(self.publication.authors, self.authors())
        add_elements(self.publication.categories, self.categories())
        for publication in self.citations():
            self.publication.add_citation(publication)

        return self.publication, self.remaining_citations

    def origin(self):
        return Origin(**self.query_dict('origin', {}))

    def collaboration(self):
        return get_or_create(
            Collaboration,
            {'name': self.query_dict('collaboration', 'none')}
        )

    def journal(self):
        return get_or_create(Journal, self.query_dict('journal', {}))

    def authors(self):
        return list(map(lambda x: get_or_create(Author, x), self.query_dict('authors', [])))

    def tags(self):
        return list(map(lambda x: get_or_create(Tag, x), self.query_dict('tags', [])))

    def categories(self):
        return list(map(lambda x: get_or_create(Category, x), self.query_dict('categories', [])))

    def citations(self):
        # Changed 11.04.2018
        # This function did not work at all
        citation_publications = []
        for origin_id in self.query('citations'):
            citation_publications += Publication.query.filter(and_(
                Publication.origin.has(id=origin_id),
                Publication.origin.has(name=self.query_dict('origin/name', 'none'))
            )).all()
        return citation_publications
