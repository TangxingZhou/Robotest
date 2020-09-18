from . import Database
from sqlalchemy import create_engine

__author__ = 'Tangxing Zhou'


class Mssql(Database):

    def __init__(self, **kwargs):
        super(Mssql, self).__init__(**kwargs)
        try:
            user = kwargs.pop('user', 'SA')
            password = kwargs.pop('password')
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 1433)
            db = kwargs.pop('db')
            kwargs.pop('engine')
        except KeyError as e:
            raise Exception('[DataBase Access Error]: "{}" is not set for mssqlserver connection.'.format(e))
        self._engine = create_engine('mssql+pyodbc://{}:{}@{}:{}/{}'.format(user, password, host, port, db), **kwargs)
        self.connect()
