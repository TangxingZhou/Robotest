# Connect to sql server and execute SQL queries.
# http://www.pymssql.org/en/stable/

__author__ = 'Tangxing Zhou'

import pymssql


class SQLServer(object):

    def __init__(self, host, port, user, pwd, db, as_dict=True):
        self.server = '{}:{}'.format(host, port)
        self.__connection = pymssql.connect(self.server, user, pwd, db, as_dict=as_dict)
        self.__cursor = self.__connection.cursor()

    def __execute(self, sql, params=(), commit=False):
        self.__cursor.execute(sql, params)
        if commit:
            self.__connection.commit()

    def __execute_many(self, sql, params=(), commit=False):
        self.__cursor.executemany(sql, params)
        if commit:
            self.__connection.commit()

    def select(self, query, params=()):
        self.__execute(query, params)
        return self.__cursor.fetchall()

    def update(self, query, values=(), commit=True):
        self.__execute(query, values, commit)

    def merge(self, query, values=(), commit=True):
        self.__execute(query, values, commit)

    def insert(self, query, values=(), commit=True):
        self.__execute_many(query, values, commit)

    def call_sp(self, sp_name, params=(), filter_columns=None):
        rows = []
        self.__cursor.callproc(sp_name, params)
        if filter_columns is None:
            return [row for row in self.__cursor]
        else:
            for row in self.__cursor:
                for column in row:
                    if column not in filter_columns:
                        row.pop(column)
                rows.append(row)
            return rows

    def close(self):
        self.__cursor.close()
        self.__connection.close()
