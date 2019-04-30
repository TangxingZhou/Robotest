# Define the listeners for robotframework
# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

__author__ = 'Tangxing Zhou'

import os, sys
from datetime import datetime
from robot.libraries.BuiltIn import BuiltIn
from libs.databases.Sqlite import Sqlite
from libs.reporting import *


class Listener2(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, db_type):
        self.__db_type = db_type.upper()
        self.__db = None
        self.__db_info = ()
        self.__email_info = ()
        self.__run_type= 'Smoke'
        self.__report_to_db = 'N'
        self.__send_email_report = 'N'
        self.__exec_dir = os.path.abspath(__file__)
        self.__project = ''
        self.__sub_project = ''
        self.__tr_name = ''
        self.__tr_id = ''
        self.__ts_id = ''
        self.__tc_id = ''
        self.__start_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.__report_libs = []

    def start_suite(self, name, attrs):
        """
        Called when a test suite starts.

        Contents of the attribute dictionary:
        id: Suite id.s1 for the top level suite, s1-s1 for its first child suite, s1-s2 for the second child, and so on.
        longname: Suite name including parent suites.
        doc: Suite documentation.
        metadata: Free test suite metadata as a dictionary / map.
        source: An absolute path of the file / directory the suite was created from.
        suites: Names of the direct child suites this suite has as a list.
        tests: Names of the tests this suite has as a list.Does not include tests of the possible child suites.
        totaltests: The total number of tests in this suite. and all its sub - suites as an integer.
        starttime: Suite execution start time.
        :param name: Name of current suite.
        :param attrs: A dictionary / map contains the attributes for current suite.
        :return:
        """
        self.__exec_dir = BuiltIn().get_variable_value('${EXECDIR}')
        path_separator = BuiltIn().get_variable_value('${/}')
        env_name = BuiltIn().get_variable_value('${ENV}', 'QA').upper()
        BuiltIn().set_suite_variable('${ENV}', env_name)
        int_or_ext = BuiltIn().get_variable_value('${IntExt}', 'Internal')
        browser = BuiltIn().get_variable_value('${Browser}', 'Chrome')
        if os.path.isfile(attrs['source']):
            paths = os.path.relpath(os.path.dirname(attrs['source']), os.path.join(self.__exec_dir, 'tests')).split(path_separator)
        else:
            paths = os.path.relpath(attrs['source'], os.path.join(self.__exec_dir, 'tests')).split(path_separator)
        self.__project, self.__sub_project = paths
        BuiltIn().set_suite_variable('${Project}', self.__project)
        BuiltIn().set_suite_variable('${Sub Project}', self.__sub_project)
        keywords_dir = os.path.join('resources', self.__project, self.__sub_project, 'keywords')
        for root, dirs, files in os.walk(keywords_dir):
            for resource_file in files:
                BuiltIn().import_resource(os.path.join(root, resource_file).replace('\\', '/'))
                self.__report_libs.append(resource_file.split('.')[0])
        if attrs['id'] == 's1':
            self.__run_type = BuiltIn().get_variable_value('${RunType}', 'Smoke')
            self.__report_to_db = BuiltIn().get_variable_value('${ReportToDB}', 'N')
            self.__send_email_report = BuiltIn().get_variable_value('${SendEmail}', 'N')
            self.__start_time = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')
            BuiltIn().import_variables('${EXECDIR}/resources/${Project}/variables.py')
            self.__db_info = tuple(map(BuiltIn().get_variable_value, map(lambda x: '${' + self.__db_type + '_' + x + '}',
                                                                  ('HOST', 'USER', 'PSW', 'DB', 'PORT'))))
            self.__email_info = tuple(map(BuiltIn().get_variable_value, map(lambda x: '${' + 'REPORT_EMAIL_' + x + '}',
                                                                  ('HOST', 'FROM', 'TO'))))
            if self.__report_to_db == 'Y':
                self.__db = None
                if self.__db is not None:
                    self.__tr_name = '{project}-{sub_project}-{env}-{start_time}'.\
                        format(project=self.__project, sub_project=self.__sub_project, env=env_name,
                               start_time=self.__start_time.strftime('%Y-%m-%d %H-%M-%S'))

    def start_test(self, name, attrs):
        """
        Called when a test case starts.

        Contents of the attribute dictionary:
        id: Suite id.s1 for the top level suite, s1-s1 for its first child suite, s1-s2 for the second child, and so on.
        longname: Suite name including parent suites.
        doc: Suite documentation.
        tags: Test tags as a list of strings.
        critical: yes or no depending is test considered critical or not.
        template: The name of the template used for the test. An empty string if the test not templated.
        starttime: Test execution execution start time.
        :param name: Name of current test.
        :param attrs: A dictionary / map contains the attributes for current test.
        :return:
        """
        pass

    def start_keyword(self, name, attrs):
        """
        Called when a keyword starts.

        Contents of the attribute dictionary:
        type: String Keyword for normal keywords, Setup or Teardown for the top level keyword used as setup/teardown,
        For for for loops, and For Item for individual for loop iterations.
        NOTE: Keyword type reporting was changed in RF 3.0. See issue #2248 for details.
        kwname: Name of the keyword without library or resource prefix. New in RF 2.9.
        libname: Name of the library or resource the keyword belongs to, or an empty string
        when the keyword is in a test case file. New in RF 2.9.
        doc: Keyword documentation.
        args: Keyword's arguments as a list of strings.
        assign: A list of variable names that keyword's return value is assigned to. New in RF 2.9.
        tags: Keyword tags as a list of strings. New in RF 3.0.
        starttime: Keyword execution start time.
        :param name: The full keyword name containing possible library or resource name as a prefix. For example,
        MyLibrary.Example Keyword.
        :param attrs: A dictionary / map contains the attributes for current keyword.
        :return:
        """
        pass

    def end_keyword(self, name, attrs):
        """
        Called when a keyword ends.

        Contents of the attribute dictionary:
        type: String Keyword for normal keywords, Setup or Teardown for the top level keyword used as setup/teardown,
        For for for loops, and For Item for individual for loop iterations.
        NOTE: Keyword type reporting was changed in RF 3.0. See issue #2248 for details.
        kwname: Name of the keyword without library or resource prefix. New in RF 2.9.
        libname: Name of the library or resource the keyword belongs to, or an empty string
        when the keyword is in a test case file. New in RF 2.9.
        doc: Keyword documentation.
        args: Keyword's arguments as a list of strings.
        assign: A list of variable names that keyword's return value is assigned to. New in RF 2.9.
        tags: Keyword tags as a list of strings. New in RF 3.0.
        starttime: Same as with start_keyword.
        endtime: Keyword execution end time.
        elapsedtime: Total execution time in milliseconds as an integer
        status: Keyword status as string PASS or FAIL.
        :param name: The full keyword name containing possible library or resource name as a prefix. For example,
        MyLibrary.Example Keyword.
        :param attrs: A dictionary / map contains the attributes for current keyword.
        :return:
        """
        pass

    def end_test(self, name, attrs):
        """
        Called when a test case ends.

        Contents of the attribute dictionary:
        id: Suite id.s1 for the top level suite, s1-s1 for its first child suite, s1-s2 for the second child, and so on.
        longname: Suite name including parent suites.
        doc: Suite documentation.
        tags: Test tags as a list of strings.
        critical: yes or no depending is test considered critical or not.
        template: The name of the template used for the test. An empty string if the test not templated.
        starttime: Test execution execution start time.
        endtime: Test execution execution end time.
        elapsedtime: Total execution time in milliseconds as an integer
        status: Test status as string PASS or FAIL.
        message: Status message. Normally an error message or an empty string.
        :param name: Name of current test.
        :param attrs: A dictionary / map contains the attributes for current test.
        :return:
        """
        pass

    def end_suite(self, name, attrs):
        """
        Called when a test suite ends.

        Contents of the attribute dictionary:
        id: Suite id.s1 for the top level suite, s1-s1 for its first child suite, s1-s2 for the second child, and so on.
        longname: Suite name including parent suites.
        doc: Suite documentation.
        metadata: Free test suite metadata as a dictionary / map.
        source: An absolute path of the file / directory the suite was created from.
        starttime: Same as in start_suite.
        endtime: Suite execution end time.
        elapsedtime: Total execution time in milliseconds as an integer
        status: Suite status as string PASS or FAIL.
        statistics: Suite statistics (number of passed and failed tests in the suite) as a string.
        message: Error message if suite setup or teardown has failed, empty otherwise.
        :param name: Name of current suite.
        :param attrs:
        :return: A dictionary / map contains the attributes for current suite.
        """
        pass

    def log_message(self, message):
        """
        Called when an executed keyword writes a log message.

        message is a dictionary with the following contents:
        message: The content of the message.
        level: Log level used in logging the message.
        timestamp: Message creation time in format YYYY-MM-DD hh:mm:ss.mil.
        html: String yes or no denoting whether the message should be interpreted as HTML or not.
        :param message: A dictionary with the contents.
        :return:
        """
        pass

    def message(self, message):
        """
        Called when the framework itself writes a syslog message.

        message is a dictionary with the following contents:
        message: The content of the message.
        level: Log level used in logging the message.
        timestamp: Message creation time in format YYYY-MM-DD hh:mm:ss.mil.
        html: String yes or no denoting whether the message should be interpreted as HTML or not.
        :param message: A dictionary with the contents.
        :return:
        """
        pass

    def close(self):
        """
        Called when the whole test execution ends.
        :return:
        """
        if self.__report_to_db == 'Y':
            verbose_stream = sys.stdout
            output_xml_path = os.path.join(self.__exec_dir, 'out', self.__project, self.__sub_project, 'output.xml')
            _sqlite = Sqlite(os.path.join(self.__exec_dir, 'out', self.__project, self.__sub_project, 'robot_results.db'), verbose_stream)
            _sqlite_writer = DatabaseWriter(_sqlite.connection, verbose_stream)
            _robot_result_parser = RobotResultsParser(_sqlite_writer, verbose_stream)
            try:
                self.__tr_id = _robot_result_parser.xml_to_db(output_xml_path)
                _sqlite_writer.commit()
                for test in _robot_result_parser.get_tests_of_test_run(self.__tr_id):
                    self.__ts_id = test[1]
                    self.__tc_id = test[0]
                    for test_keyword in _robot_result_parser.get_keywords_of_test(self.__tr_id, self.__tc_id):
                        # TODO:
                        pass
            except Exception as e:
                sys.stderr.write('[Sqlite ERROR]: Invalid XML: {}\n\n'.format(e))
                exit(1)
            finally:
                _sqlite_writer.close()
                # self.__db.close()
        if self.__send_email_report == 'Y':
            # email_smtp = EmailReport(*self.__email_info)
            # email_smtp.send(self.__db.db_client, self.__tr_id, self.__tr_name)
            pass


class Listener3(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        pass

    def start_suite(self, data, result):
        pass

    def start_test(self, data, result):
        pass

    def end_test(self, data, result):
        pass

    def end_suite(self, data, result):
        pass

    def log_message(self, message):
        pass

    def message(self, message):
        pass

    def close(self):
        pass
