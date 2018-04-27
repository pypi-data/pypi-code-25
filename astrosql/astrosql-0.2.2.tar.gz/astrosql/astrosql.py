import astropy.units as u
import numpy as np
import peewee
import pandas as pd
import re
import warnings
from pathlib import Path
from pwiz import Introspector
from astrosql.sqlconnector import connect
from pymysql import InternalError


class AstroSQL:

    def __init__(self, database, **kwargs):
        """

        Parameters
        ----------
        database : peewee.MySQLDatabase
             A MySQL peewee database see
             [documentation](http://docs.peewee-orm.com/en/latest/peewee/database.html#using-mysql)
        """
        if isinstance(database, peewee.MySQLDatabase):
            self.database = database
        elif isinstance(database, str):
            self.database = connect(database=database, **kwargs)
        else:
            raise ValueError('argument [database] is neither a peewee.MySQLDatabase, nor a string')

        self.tables = Introspector.from_database(self.database).generate_models(literal_column_names=True)
        if len(self.tables) == 0:
            warnings.warn("You're working with an empty database.", FutureWarning)

    def get_table(self, table):
        """

        Parameters
        ----------
        table : str, peewee.ModelBase
                Table queried in the database

        Returns
        -------
        peewee.Model
            A list of rows as dict

        """
        if isinstance(table, str):
            assert table in self.tables, "Sanity Check Failed: Table queried does not exist"
            table = self.tables[table]
        elif isinstance(table, peewee.ModelBase):
            table = table
        else:
            raise ValueError("argument [table] is neither a string or peewee.ModelBase")
        return table

    def dict2sql(self, table, data):
        """
        Write a (1, n) dictionary (single row dictionary) to mySQL.

        Parameters
        ----------
        table : str, peewee.ModelBase
                Table to be written to
        data : dict
                Data to be written, must match the columns of `table`

        """
        assert isinstance(data, dict), "argument [data] is not a Python dictionary"
        table = self.get_table(table)

        table.create(**data)

    def text2sql(self, table, file):
        """

        Parameters
        ----------
        table : str
        file : file, str, or pathlib.Path
        """
        # TODO: Fix column header which is not yet parseable

        raise DeprecationWarning

        if isinstance(file, str):
            assert Path(str).exists(), "{} is not a valid file path or does not exit".format(file)
        table = self.get_table(table)

        df = pd.read_csv(file, header=None, sep="\s+", comment='#')

        print("\nFirst few rows of data (", args.file,
              "):to be loaded: \n{}\n".format(df.head()))
        print("\nLast few rows of data (", args.file,
              "):to be loaded: \n{}\n".format(df.tail()))
        print("Writing to database.\nThis may take a while...")

        data = df.to_dict('records')
        table.insert_many(data)

    def get(self, table, **kwargs):
        kwargs = {k: v for k, v in kwargs.items()}
        table = self.get_table(table)
        query = table.select()

        if len(kwargs) == 0:
            return None

        if any([arg in kwargs for arg in ['ra', 'dec', 'radius']]):
            if all([arg in kwargs for arg in ['ra', 'dec', 'radius']]):
                ra = kwargs['ra']
                dec = kwargs['dec']
                radius = kwargs['radius']
                try:
                    query = query.where(
                        table.RA.between(ra - radius, ra + radius),
                        table.Dec.between(dec - radius, dec + radius)
                    )
                except AttributeError:
                    query = query.where(
                        table.centerRa.between(ra - radius, ra + radius),
                        table.centerDec.between(dec - radius, dec + radius)
                    )
            elif all([arg in kwargs for arg in ['ra', 'dec']]):
                ra = kwargs['ra']
                dec = kwargs['dec']
                try:
                    query = query.where(
                        table.RA == ra,
                        table.Dec == dec)

                except AttributeError:
                    query = query.where(
                        table.centerRa == ra,
                        table.centerDec == dec
                    )
            else:
                raise ValueError("Coordinate arguments must be in triples (RA, Dec, radius) or tuples (RA, Dec)")

        for key, value in [tup for tup in kwargs.items() if tup[0] not in ['ra', 'dec', 'radius']]:
            query = query.where(getattr(table, key) == value)

        print(query)

        data = list(query.dicts())
        return data

    def get_by_basename(self, table, basename):
        """
        Get data from SQL database by the unique key basename.

        Parameters
        ----------
        table : str, peewee.ModelBase
                Table queried in the database
        basename : str
                The base name queried from the unique key `basename` of the database

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        query = table.select().where(table.basename == basename)
        print(query.sql())

        data = list(query.dicts())
        return data

    def get_by_object(self, table, objname):
        """
        Get data from SQL database by the column `objname`

        Parameters
        ----------
        table : str, peewee.ModelBase
                Table queried in the database
        objname : str
                Object name queried from the `objname` column of the database

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        query = table.select().where(table.objname == objname)
        print(query.sql())

        data = list(query.dicts())
        return data

    def get_by_radec(self, table, ra, dec, radius):
        """
        Get data from SQL database within a square area of the sky determined by ra, dec, radius.

        Parameters
        ----------
        table : str, peewee.ModelBase
             Table queried in the database
        ra : float
             The right ascension in degrees corresponding to the center of the queried box
        dec : float
             The declination in degrees corresponding to the center of the queried box
        radius : float
             The radius in arc minutes which is the square radius of the queried box.

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        radius = radius * u.arcmin.to(u.deg) / np.cos((dec * u.deg).to(u.rad).value)

        try:
            query = table.select().where(
                table.RA.between(ra - radius, ra + radius),
                table.DEC.between(dec - radius, dec + radius)
            )
        except AttributeError:
            query = table.select().where(
                table.centerRa.between(ra - radius, ra + radius),
                table.centerDec.between(dec - radius, dec + radius)
            )

        print(query.sql())

        data = list(query.dicts())
        return data

    def get_by_sql(self, query):
        """
        Get data from SQL by an SQL select query.

        Parameters
        ----------
        query : str
                An SQL select `query`. `query` must end with a semicolon ';'

        Returns
        -------
        list
            A list of rows as dict
        """
        pattern = r"^SELECT [^;]*;$"
        assert len(self.tables) > 0, 'This database has no tables, there is nothing to select.'
        assert re.match(pattern, query), "Query is invalid. It must be in the form of a typical SQL select statement " \
                                         "like 'SELECT <expr> FROM <table> [...] ;"

        model = list(self.tables.values())[0]
        print(query)

        data = list(model.raw(query).dicts())
        return data
