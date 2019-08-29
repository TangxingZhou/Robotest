__author__ = 'Tangxing Zhou'


class DatabaseWriter(object):

    def __init__(self, connection, verbose_stream):
        self._connection = connection
        self.__cursor = self._connection.cursor()
        self._verbose = self.__verbose(verbose_stream)
        self._init_schema()

    def _init_schema(self):
        self._verbose('- Initializing database schema')
        self._create_table_test_runs()
        self._create_table_test_run_status()
        self._create_table_test_run_errors()
        self._create_table_test_tag_status()
        self._create_table_suites()
        self._create_table_suite_status()
        self._create_table_tests()
        self._create_table_test_status()
        self._create_table_keywords()
        self._create_table_keyword_status()
        self._create_table_messages()
        self._create_table_test_tags()
        self._create_table_keyword_tags()
        self._create_table_arguments()

    def _create_table_test_runs(self):
        self._create_table('test_runs', {
            'hash': 'TEXT NOT NULL',
            'imported_at': 'DATETIME NOT NULL',
            'source_file': 'TEXT',
            'started_at': 'DATETIME',
            'finished_at': 'DATETIME',
        }, ('hash',))

    def _create_table_test_run_status(self):
        self._create_table('test_run_status', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'name': 'TEXT NOT NULL',
            'elapsed': 'INTEGER',
            'failed': 'INTEGER NOT NULL',
            'passed': 'INTEGER NOT NULL'
        }, ('test_run_id', 'name'))

    def _create_table_test_run_errors(self):
        self._create_table('test_run_errors', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'level': 'TEXT NOT NULL',
            'timestamp': 'DATETIME NOT NULL',
            'content': 'TEXT NOT NULL'
        }, ('test_run_id', 'level', 'content'))

    def _create_table_test_tag_status(self):
        self._create_table('test_tag_status', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'name': 'TEXT NOT NULL',
            'critical': 'INTEGER NOT NULL',
            'elapsed': 'INTEGER',
            'failed': 'INTEGER NOT NULL',
            'passed': 'INTEGER NOT NULL',
        }, ('test_run_id', 'name'))

    def _create_table_suites(self):
        self._create_table('suites', {
            'suite_key': 'TEXT NOT NULL',
            'parent_id': 'INTEGER REFERENCES suites',
            'parent_suite': 'TEXT NOT NULL',
            'name': 'TEXT NOT NULL',
            'source': 'TEXT',
            'doc': 'TEXT'
        }, ('name', 'source'))

    def _create_table_suite_status(self):
        self._create_table('suite_status', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'suite_id': 'INTEGER  NOT NULL REFERENCES suites',
            'elapsed': 'INTEGER NOT NULL',
            'failed': 'INTEGER NOT NULL',
            'passed': 'INTEGER NOT NULL',
            'status': 'TEXT NOT NULL'
        }, ('test_run_id', 'suite_id'))

    def _create_table_tests(self):
        self._create_table('tests', {
            'suite_id': 'INTEGER NOT NULL REFERENCES suites',
            'test_key': 'TEXT NOT NULL',
            'name': 'TEXT NOT NULL',
            'timeout': 'TEXT',
            'doc': 'TEXT'
        }, ('suite_id', 'name'))

    def _create_table_test_status(self):
        self._create_table('test_status', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'test_id': 'INTEGER  NOT NULL REFERENCES tests',
            'status': 'TEXT NOT NULL',
            'elapsed': 'INTEGER NOT NULL'
        }, ('test_run_id', 'test_id'))

    def _create_table_keywords(self):
        self._create_table('keywords', {
            'suite_id': 'INTEGER REFERENCES suites',
            'test_id': 'INTEGER REFERENCES tests',
            'keyword_key': 'TEXT NOT NULL',
            'parent_id': 'INTEGER REFERENCES keywords',
            'name': 'TEXT NOT NULL',
            'type': 'TEXT NOT NULL',
            'library': 'TEXT',
            'timeout': 'TEXT',
            'doc': 'TEXT'
        })

    def _create_table_keyword_status(self):
        self._create_table('keyword_status', {
            'test_run_id': 'INTEGER NOT NULL REFERENCES test_runs',
            'keyword_id': 'INTEGER NOT NULL REFERENCES keywords',
            'status': 'TEXT NOT NULL',
            'starttime': 'TEXT NOT NULL',
            'endtime': 'TEXT NOT NULL',
            'elapsed': 'INTEGER NOT NULL'
        })

    def _create_table_messages(self):
        self._create_table('messages', {
            'keyword_id': 'INTEGER NOT NULL REFERENCES keywords',
            'level': 'TEXT NOT NULL',
            'timestamp': 'DATETIME NOT NULL',
            'content': 'TEXT NOT NULL'
        }, ('keyword_id', 'level', 'content'))

    def _create_table_test_tags(self):
        self._create_table('test_tags', {
            'test_id': 'INTEGER NOT NULL REFERENCES tests',
            'name': 'TEXT NOT NULL'
        }, ('test_id', 'name'))

    def _create_table_keyword_tags(self):
        self._create_table('keyword_tags', {
            'keyword_id': 'INTEGER NOT NULL REFERENCES keywords',
            'tag': 'TEXT NOT NULL'
        }, ('keyword_id', 'tag'))

    def _create_table_arguments(self):
        self._create_table('arguments', {
            'keyword_id': 'INTEGER NOT NULL REFERENCES keywords',
            'content': 'TEXT NOT NULL'
        }, ('keyword_id', 'content'))

    def _create_table(self, table_name, columns, unique_columns=()):
        definitions = ['id INTEGER PRIMARY KEY']
        for column_name, properties in columns.items():
            definitions.append('{} {}'.format(column_name, properties))
        if unique_columns:
            unique_column_names = ', '.join(unique_columns)
            definitions.append('CONSTRAINT unique_{} UNIQUE ({})'.format(table_name, unique_column_names))
        sql_statement = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table_name, ', '.join(definitions))
        self.__cursor.execute(sql_statement)

    def rename_table(self, old_name, new_name):
        sql_statement = 'ALTER TABLE {} RENAME TO {}'.format(old_name, new_name)
        self.__cursor.execute(sql_statement)

    def drop_table(self, table_name):
        sql_statement = 'DROP TABLE {}'.format(table_name)
        self.__cursor.execute(sql_statement)

    def copy_table(self, from_table, to_table, columns_to_copy):
        column_names = ', '.join(columns_to_copy)
        sql_statement = 'INSERT INTO {}({}) SELECT {} FROM {}'.format(to_table, column_names, column_names, from_table)
        self.__cursor.execute(sql_statement)

    def fetch_id(self, table_name, criteria):
        sql_statement = 'SELECT id FROM {} WHERE '.format(table_name)
        sql_statement += ' AND '.join('{}=?'.format(key) for key in criteria.keys())
        self.__cursor.execute(sql_statement, list(criteria.values()))
        res = self.__cursor.fetchone()
        if not res:
            raise Exception('Query did not yield id, even though it should have.'
                            '\nSQL statement was:\n{}\nArguments were:\n{}'.format(sql_statement, list(criteria.values())))
        return res[0]

    def fetch_records(self, table_columns, **criteria):
        columns = [key for key in table_columns.keys() if key != '__table__']
        sql_statement = 'SELECT {} FROM {} WHERE '.format(', '.join(columns), table_columns['__table__'])
        sql_statement += ' AND '.join('{}=?'.format(key) for key in criteria.keys())
        self.__cursor.execute(sql_statement, list(criteria.values()))
        records = []
        for out in self.__cursor.fetchall():
            params = {}
            for index, field in enumerate(columns):
                if isinstance(out[index], table_columns[field]):
                    params[field] = out[index]
                else:
                    raise TypeError('The type of \'{}\' should be {} but it\'s {}.'.
                                    format(field, table_columns[field], type(out[index])))
            records.append(type('dict2obj', (dict,), params)())
        return records

    def insert(self, table_name, criteria):
        sql_statement = self._format_insert_statement(table_name, list(criteria.keys()))
        self.__cursor.execute(sql_statement, list(criteria.values()))
        return self.__cursor.lastrowid

    def insert_or_ignore(self, table_name, criteria):
        sql_statement = self._format_insert_statement(table_name, list(criteria.keys()), 'IGNORE')
        self.__cursor.execute(sql_statement, list(criteria.values()))
        return self.__cursor.lastrowid

    def insert_many_or_ignore(self, table_name, column_names, values):
        sql_statement = self._format_insert_statement(table_name, column_names, 'IGNORE')
        self.__cursor.executemany(sql_statement, values)

    def select(self, query, params=()):
        self.__cursor.execute(query, params)
        return self.__cursor.fetchall()

    @classmethod
    def _format_insert_statement(cls, table_name, column_names, on_conflict='ABORT'):
        return 'INSERT OR {} INTO {} ({}) VALUES ({})'.format(
            on_conflict,
            table_name,
            ','.join(column_names),
            ','.join('?' * len(column_names))
        )

    def commit(self):
        self._verbose('- Committing changes into database')
        self._connection.commit()

    def close(self):
        self.__cursor.close()
        self._connection.close()

    @classmethod
    def __verbose(cls, stream):
        def fun(message):
            if stream:
                stream.write('\n{:<10}{}{}'.format('DataBase', ' ' * 2, message))

        return fun
