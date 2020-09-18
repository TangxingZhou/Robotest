from . import Database
from sqlalchemy import create_engine


__author__ = 'Tangxing Zhou'


class Mysql(Database):

    def __init__(self, **kwargs):
        super(Mysql, self).__init__(**kwargs)
        try:
            user = kwargs.pop('user', 'root')
            password = kwargs.pop('password')
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 3306)
            db = kwargs.pop('db')
            kwargs.pop('engine')
        except KeyError as e:
            raise Exception('[DataBase Access Error]: "{}" is not set for mysql connection.'.format(e))
        self._engine = create_engine('mysql+mysqldb://{}:{}@{}:{}/{}'.format(user, password, host, port, db), **kwargs)
        self.connect()
