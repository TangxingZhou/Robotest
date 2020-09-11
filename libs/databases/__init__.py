import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .mysql import Mysql
from .sqlite import Sqlite
Base = declarative_base()


class Database(object):

    def __init__(self, **kwargs):
        self._verbose = self.__verbose(kwargs.pop('verbose_stream', sys.stdout))
        self.__Session = sessionmaker()
        self.session = None
        self._engine = None

    def connect(self):
        self._verbose('- Establishing database connection')
        self.__Session.configure(bind=self._engine)
        self.session = self.__Session()
        self._verbose('- Initializing database tables')
        Base.metadata.create_all(self._engine)

    def insert(self, obj):
        self.session.add(obj)

    def select(self):
        pass

    def delete(self, obj):
        self.session.delete(obj)

    def commit(self):
        self._verbose('- Committing changes into database\n')
        self.session.commit()

    def rollback(self):
        self._verbose('- Rollback changes into database\n')
        self.session.rollback()

    def close(self):
        self._verbose('- Closing database connection')
        self.session.close()

    @classmethod
    def __verbose(cls, stream):
        def fun(message):
            if stream:
                stream.write('{:<10}{}{}'.format(cls.__name__, ' ' * 2, message))
        return fun
