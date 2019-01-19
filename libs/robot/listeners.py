# Define the listeners for robotframework
# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

__author__ = 'Tangxing Zhou'

import os
from datetime import datetime
from robot.libraries.BuiltIn import BuiltIn


class Listener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, db_type):
        self.__db_type = db_type.upper()
        self.__db = None

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
        if os.path.isdir(attrs['source']):
            dir_name = attrs['source']
        elif os.path.isfile(attrs['source']):
            dir_name = os.path.dirname(attrs['source'])
        else:
            dir_name = BuiltIn().get_variable_value('${EXECDIR}')
        paths = os.path.relpath(dir_name, os.path.join(BuiltIn().get_variable_value('${EXECDIR}'), 'tests/')). \
            split(BuiltIn().get_variable_value('${/}'))
        project = paths[0]
        BuiltIn().set_suite_variable('${Project}', project)
        BuiltIn().import_variables('resources/{}/variables.py'.format(project))
        db_login = tuple(map(BuiltIn().get_variable_value, map(lambda x: '${' + self.__db_type + x + '}',
                                                               ('_HOST', '_USER', '_PSW', '_DB', '_PORT'))))
        if attrs['id'] == 's1':
            start_time = datetime.strptime(attrs['starttime'], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d_%H-%M-%S')

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
        pass
