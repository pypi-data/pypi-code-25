# System Imports
from typing import TypeVar

# Third-Party Imports
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base

# Local Source Imports

B = TypeVar('B', bound='Base')
Base = declarative_base()

def create_tables(engine: Engine):
    Base.metadata.create_all(engine)
