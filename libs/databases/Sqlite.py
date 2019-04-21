# Connect to sqlite and execute SQL queries.
# https://www.sqlite.org/index.html

import sqlite3

__author__ = 'Tangxing Zhou'


class Sqlite(object):

    def __init__(self, db_file_path, verbose_stream):
        self._verbose = self.__verbose(verbose_stream)
        self.connection = self._connect(db_file_path)
        self._configure()

    def _connect(self, db_file_path):
        self._verbose('- Establishing database connection')
        return sqlite3.connect(db_file_path)

    def _configure(self):
        self._set_pragma('page_size', 4096)
        self._set_pragma('cache_size', 10000)
        self._set_pragma('synchronous', 'NORMAL')
        self._set_pragma('journal_mode', 'WAL')

    def _set_pragma(self, name, value):
        sql_statement = 'PRAGMA {}={}'.format(name, value)
        self.connection.execute(sql_statement)

    def close(self):
        self._verbose('- Closing database connection')
        self.connection.close()

    @classmethod
    def __verbose(cls, stream):
        def fun(message):
            if stream:
                stream.write('{:<10}{}{}'.format('DataBase', ' ' * 2, message))
        return fun
