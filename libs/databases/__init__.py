import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class Database(object):

    def __init__(self, **kwargs):
        self._verbose = self.__verbose(kwargs.pop('verbose_stream', sys.stdout))
        self.__session = sessionmaker()
        self.session = None
        self._engine = None

    def connect(self):
        self.__session.configure(bind=self._engine)
        self.session = self.__session()
        if not database_exists(self._engine.url):
            create_database(self._engine.url)
        Base.metadata.create_all(self._engine)

    def insert(self, obj):
        self.session.add(obj)

    def select(self):
        pass

    def delete(self, obj):
        self.session.delete(obj)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

    @classmethod
    def __verbose(cls, stream):
        def fun(message):
            if stream:
                stream.write('{:<10}{}{}\n'.format(cls.__name__, ' ' * 2, message))
        return fun
