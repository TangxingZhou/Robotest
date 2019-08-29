from __future__ import with_statement
from datetime import datetime
from hashlib import sha1
from robot.api import ExecutionResult
from sqlite3 import IntegrityError

__author__ = 'Tangxing Zhou'


class RobotResultsParser(object):

    def __init__(self, db, verbose_stream):
        self._verbose = self.__verbose(verbose_stream)
        self._db = db

    def xml_to_db(self, xml_file):
        self._verbose('--> Parsing {}'.format(xml_file))
        test_run = ExecutionResult(xml_file, include_keywords=True)
        hash_code = self._hash(xml_file)
        try:
            test_run_id = self._db.insert('test_runs', {
                'hash': hash_code,
                'imported_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'source_file': test_run.source,
                'started_at': self._format_robot_timestamp(test_run.suite.starttime),
                'finished_at': self._format_robot_timestamp(test_run.suite.endtime)
            })
        except IntegrityError:
            test_run_id = self._db.fetch_id('test_runs', {
                'source_file': test_run.source,
                'started_at': self._format_robot_timestamp(test_run.suite.starttime),
                'finished_at': self._format_robot_timestamp(test_run.suite.endtime)
            })
        self._parse_errors(test_run.errors.messages, test_run_id)
        self._parse_statistics(test_run.statistics, test_run_id)
        self._parse_suite(test_run.suite, test_run_id)
        return test_run_id

    @classmethod
    def _hash(cls, xml_file):
        block_size = 68157440
        hasher = sha1()
        with open(xml_file, 'rb') as f:
            chunk = f.read(block_size)
            while len(chunk) > 0:
                hasher.update(chunk)
                chunk = f.read(block_size)
        return hasher.hexdigest()

    def _parse_errors(self, errors, test_run_id):
        self._db.insert_many_or_ignore('test_run_errors',
            ('test_run_id', 'level', 'timestamp', 'content'),
            [(test_run_id, error.level, self._format_robot_timestamp(error.timestamp), error.message)
             for error in errors]
        )

    def _parse_statistics(self, statistics, test_run_id):
        self._parse_test_run_statistics(statistics.total, test_run_id)
        self._parse_tag_statistics(statistics.tags, test_run_id)

    def _parse_test_run_statistics(self, test_run_statistics, test_run_id):
        self._verbose('--> Parsing test run statistics')
        [self._parse_test_run_stats(stat, test_run_id) for stat in test_run_statistics]

    def _parse_tag_statistics(self, tag_statistics, test_run_id):
        self._verbose('  --> Parsing tag statistics')
        [self._parse_tag_stats(stat, test_run_id) for stat in tag_statistics.tags.values()]

    def _parse_tag_stats(self, stat, test_run_id):
        self._db.insert_or_ignore('test_tag_status', {
            'test_run_id': test_run_id,
            'name': stat.name,
            'critical': stat.critical,
            'elapsed': getattr(stat, 'elapsed', None),
            'failed': stat.failed,
            'passed': stat.passed
        })

    def _parse_test_run_stats(self, stat, test_run_id):
        self._db.insert_or_ignore('test_run_status', {
            'test_run_id': test_run_id,
            'name': stat.name,
            'elapsed': getattr(stat, 'elapsed', None),
            'failed': stat.failed,
            'passed': stat.passed
        })

    def _parse_suite(self, suite, test_run_id, parent_suite_id=None, parent_suite=''):
        self._verbose('--> Parsing suite: {}'.format(suite.name))
        try:
            suite_id = self._db.insert('suites', {
                'suite_key': suite.id,
                'parent_id': parent_suite_id,
                'parent_suite': parent_suite,
                'name': suite.name,
                'source': suite.source,
                'doc': suite.doc
            })
        except IntegrityError:
            suite_id = self._db.fetch_id('suites', {
                'name': suite.name,
                'source': suite.source
            })
        self._parse_suite_status(test_run_id, suite_id, suite)
        self._parse_suites(suite, test_run_id, suite_id, '{}.{}'.format(parent_suite, suite.name).strip('.'))
        self._parse_tests(suite.tests, test_run_id, suite_id)
        self._parse_keywords(suite.keywords, test_run_id, suite_id, None)

    def _parse_suite_status(self, test_run_id, suite_id, suite):
        self._db.insert_or_ignore('suite_status', {
            'test_run_id': test_run_id,
            'suite_id': suite_id,
            'passed': suite.statistics.all.passed,
            'failed': suite.statistics.all.failed,
            'elapsed': suite.elapsedtime,
            'status': suite.status
        })

    def _parse_suites(self, suite, test_run_id, parent_suite_id, parent_suite):
        [self._parse_suite(subsuite, test_run_id, parent_suite_id, parent_suite) for subsuite in suite.suites]

    def _parse_tests(self, tests, test_run_id, suite_id):
        [self._parse_test(test, test_run_id, suite_id) for test in tests]

    def _parse_test(self, test, test_run_id, suite_id):
        self._verbose('  --> Parsing test: {}'.format(test.name))
        try:
            test_id = self._db.insert('tests', {
                'suite_id': suite_id,
                'test_key': test.id,
                'name': test.name,
                'timeout': test.timeout,
                'doc': test.doc
            })
        except IntegrityError:
            test_id = self._db.fetch_id('tests', {
                'suite_id': suite_id,
                'name': test.name
            })
        self._parse_test_status(test_run_id, test_id, test)
        self._parse_tags(test.tags, test_id)
        self._parse_keywords(test.keywords, test_run_id, suite_id, test_id)

    def _parse_test_status(self, test_run_id, test_id, test):
        self._db.insert_or_ignore('test_status', {
            'test_run_id': test_run_id,
            'test_id': test_id,
            'status': test.status,
            'elapsed': test.elapsedtime
        })

    def _parse_tags(self, tags, test_id):
        self._db.insert_many_or_ignore('test_tags', ('test_id', 'name'), [(test_id, tag) for tag in tags])

    def _parse_keywords(self, keywords, test_run_id, suite_id, test_id, parent_keyword_id=None):
        [self._parse_keyword(keyword, test_run_id, suite_id, test_id, parent_keyword_id) for keyword in keywords]

    def _parse_keyword(self, keyword, test_run_id, suite_id, test_id, parent_keyword_id):
        keyword_id = self._db.insert_or_ignore('keywords', {
            'suite_id': suite_id,
            'test_id': test_id,
            'keyword_key': keyword.id,
            'parent_id': parent_keyword_id,
            'name': keyword.name,
            'type': keyword.type,
            'library': keyword.libname,
            'timeout': keyword.timeout,
            'doc': keyword.doc
        })
        self._parse_keyword_tags(keyword_id, keyword)
        self._parse_keyword_status(test_run_id, keyword_id, keyword)
        self._parse_messages(keyword.messages, keyword_id)
        self._parse_arguments(keyword.args, keyword_id)
        self._parse_keywords(keyword.keywords, test_run_id, suite_id, test_id, keyword_id)

    def _parse_keyword_tags(self, keyword_id, keyword):
        [self._parse_keyword_tag(keyword_id, tag) for tag in keyword.tags]

    def _parse_keyword_tag(self, keyword_id, tag):
        self._db.insert_or_ignore('keyword_tags', {
            'keyword_id': keyword_id,
            'tag': tag
        })

    def _parse_keyword_status(self, test_run_id, keyword_id, keyword):
        self._db.insert_or_ignore('keyword_status', {
            'test_run_id': test_run_id,
            'keyword_id': keyword_id,
            'status': keyword.status,
            'starttime': keyword.starttime,
            'endtime': keyword.endtime,
            'elapsed': keyword.elapsedtime
        })

    def _parse_messages(self, messages, keyword_id):
        self._db.insert_many_or_ignore('messages', ('keyword_id', 'level', 'timestamp', 'content'),
                                       [(keyword_id, message.level, self._format_robot_timestamp(message.timestamp),
                                         message.message) for message in messages]
                                       )

    def _parse_arguments(self, args, keyword_id):
        self._db.insert_or_ignore('arguments', {
            'keyword_id': keyword_id,
            'content': ', '.join(args)
        })

    def get_test_run(self, test_run_id):
        sql = '''
        SELECT * FROM test_runs
        WHERE id = {};
        '''
        return self._db.select(sql.format(test_run_id,))

    def get_suites_of_test_run(self, test_run_id):
        sql = '''
        SELECT ss.suite_id, s.name [suite_name], s.suite_key [suite_key], ss.status [status], ss.passed [passed], ss.failed [failed], ss.elapsed [elapsed], s.parent_id [parent_id], s.source [source], s.doc [doc] FROM suite_status ss
        JOIN suites s on s.id = ss.suite_id
        WHERE ss.test_run_id = {};
        '''
        return self._db.select(sql.format(test_run_id,))

    def get_suite(self, suite_id):
        sql = '''
        SELECT ss.suite_id, s.name [suite_name], s.suite_key [suite_key], ss.status [status], ss.passed [passed], ss.failed [failed], ss.elapsed [elapsed], s.parent_id [parent_id], s.source [source], s.doc [doc] FROM suite_status ss
        JOIN suites s on s.id = ss.suite_id
        WHERE ss.suite_id = {};
        '''
        return self._db.select(sql.format(suite_id, ))

    def get_tests_of_test_run(self, test_run_id):
        sql = '''
        SELECT ts.test_id, s.id [suite_id], s.name [suite_name], t.name [test_name], ts.status [test_status], t.doc [test_doc] FROM test_status ts
        JOIN tests t on ts.test_id = t.id
        JOIN suites s on s.id = t.suite_id
        WHERE ts.test_run_id = {};
        '''
        return self._db.select(sql.format(test_run_id,))

    def get_test(self, test_id):
        sql = '''
        SELECT ts.test_id, s.id [suite_id], s.name [suite_name], t.name [test_name], ts.status [test_status], t.doc [test_doc] FROM test_status ts
        JOIN tests t on ts.test_id = t.id
        JOIN suites s on s.id = t.suite_id
        WHERE ts.test_id = {};
        '''
        return self._db.select(sql.format(test_id,))

    def get_tags_of_test(self, test_id):
        sql = '''
        SELECT test_id, name FROM test_tags
        WHERE test_id = {};
        '''
        return self._db.select(sql.format(test_id,))

    def get_keywords_of_test(self, test_run_id, test_id):
        sql = '''
        SELECT kws.keyword_id, kw.name [keyword_name], kws.status [keyword_status], kw.library [keyword_library], 
        a.content [keyword_arguments], m.content [keyword_message], kws.starttime [keyword_starttime], kws.endtime [keyword_endtime] 
        FROM keyword_status kws
        JOIN keywords kw on kw.id = kws.keyword_id
        LEFT JOIN messages m on m.keyword_id = kws.keyword_id
        LEFT JOIN arguments a on a.keyword_id = kws.keyword_id
        WHERE kws.test_run_id = {}
        AND kw.type = 'kw'
        AND kw.test_id = {}
        AND parent_id is NULL;
        '''
        return self._db.select(sql.format(test_run_id, test_id))

    def get_child_keywords_of_keyword(self, keyword_id):
        sql = '''
        SELECT kws.keyword_id, kw.name [keyword_name], kws.status [keyword_status], kw.library [keyword_library], 
        a.content [keyword_arguments], m.content [keyword_message], kws.starttime [keyword_starttime], kws.endtime [keyword_endtime] 
        FROM keyword_status kws
        JOIN keywords kw on kw.id = kws.keyword_id
        LEFT JOIN messages m on m.keyword_id = kws.keyword_id
        LEFT JOIN arguments a on a.keyword_id = kws.keyword_id
        WHERE kw.type = 'kw'
        AND parent_id = {};
        '''
        return self._db.select(sql.format(keyword_id,))

    def get_keyword(self, keyword_id):
        sql = '''
        SELECT kws.keyword_id, kw.name [keyword_name], kws.status [keyword_status], kw.library [keyword_library], 
        a.content [keyword_arguments], m.content [keyword_message], kws.starttime [keyword_starttime], kws.endtime [keyword_endtime] 
        FROM keyword_status kws
        JOIN keywords kw on kw.id = kws.keyword_id
        LEFT JOIN messages m on m.keyword_id = kws.keyword_id
        LEFT JOIN arguments a on a.keyword_id = kws.keyword_id
        WHERE kw.type = 'kw'
        AND kws.keyword_id = {};
        '''
        return self._db.select(sql.format(keyword_id,))

    @classmethod
    def _format_robot_timestamp(cls, timestamp):
        return datetime.strptime(timestamp, '%Y%m%d %H:%M:%S.%f')

    def close(self):
        self._db.close()

    @classmethod
    def __verbose(cls, stream):
        def fun(message):
            if stream:
                stream.write('\n{:<10}{}{}'.format('', ' ' * 2, message))

        return fun
