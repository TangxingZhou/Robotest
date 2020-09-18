# Connect to sqlite and execute SQL queries.
# https://www.sqlite.org/index.html

from . import Database
from sqlalchemy import create_engine

__author__ = 'Tangxing Zhou'


class Sqlite(Database):

    def __init__(self, **kwargs):
        super(Sqlite, self).__init__(**kwargs)
        try:
            db = kwargs.pop('db')
            kwargs.pop('engine')
        except KeyError as e:
            raise Exception('[DataBase Access Error]: "{}" is not set for sqlite3 connection.'.format(e))
        self._engine = create_engine('sqlite:///{}'.format(db), **kwargs)
        self.connect()
