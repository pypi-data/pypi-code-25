# System Imports
from typing import Any, Dict, Tuple

# Third-Party Imports
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm.session import Session, sessionmaker

# Local Source Imports

__author__ = 'H.D. "Chip" McCullough IV'

class Context(object):
    """ Database Context class. """

    def __init__(self, settings: dict, *args, **kwargs):
        self.__engine: Engine = create_engine(URL(**settings))
        self.__sessionmaker: sessionmaker = sessionmaker(bind=self.__engine, autoflush=True)
        self.__args: Tuple[Any, ...] = args
        self.__kwargs: Dict[str, Any] = kwargs

    def __call__(self) -> Session:
        """ Calling an instance of Context will return a new SQL Alchemy :class:`Session <Session>` object.

        Usage::
            >>> db = Context(settings={...})
            >>> session = db()

        Equivalent To::
            >>> db = Context(settings={...})
            >>> session_factory = db.sessionmaker
            >>> session = session_factory()
        :returns: A new Session instance
        :rtype: Session
        """
        return self.sessionmaker()

    def __del__(self):
        """ Called when an instance of Context is about to be destroyed. """
        pass

    def __repr__(self) -> str:
        """ A String representation of the :class:`Context <Context>`.
        
        :returns: String representation of :class:`Context <Context>` object.
        :rtype: str
        """
        return '<class Context at {hex_id}>'.format(hex_id=hex(id(self)))

    def __str__(self) -> str:
        """ An informal, User-Friendly representation of the :class:`Context <Context>`.
        
        :returns: User-Friendly String representation of :class:`Context <Context>`.
        :rtype: str
        """
        return str(self.__engine)

    def __unicode__(self):
        """ An informal, User-Friendly representation of the :class:`Context <Context>`.

        :returns: User-Friendly String representation of :class:`Context <Context>`.
        :rtype: str
        """
        return str(self.__engine)

    def __nonzero__(self) -> bool:
        """ Called by built-in function `bool`, or when a truth-value test occurs. """
        pass

    @property
    def engine(self) -> Engine:
        return self.__engine

    @property
    def sessionmaker(self) -> sessionmaker:
        return self.__sessionmaker

    @property
    def arguments(self) -> Tuple[Any, ...]:
        return self.__args

    @property
    def keyword_arguments(self) -> dict:
        return self.__kwargs
