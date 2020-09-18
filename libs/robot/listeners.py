# Define the listeners for robotframework
# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

__author__ = 'Tangxing Zhou'

from robot.libraries.BuiltIn import BuiltIn
from libs.reporting.robot_output_xml import *
from libs.reporting.email_report import *

import allure_commons
from allure_commons.lifecycle import AllureLifecycle
from allure_commons.logger import AllureFileLogger
from allure_robotframework.allure_listener import AllureListener
from allure_robotframework.types import RobotKeywordType

DEFAULT_OUTPUT_PATH = os.path.join('out', 'allure')


class Listener2(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, logger_path=DEFAULT_OUTPUT_PATH):
        # self.__db = None
        self.__task_id = ''
        self.__email_info = ()
        self.__run_type = 'Smoke'
        self.__report_db = 'sqlite'
        # self.__merge_results = 'N'
        # self.__send_email_report = 'N'
        self.__exec_dir = os.path.abspath(__file__)
        self.__project = ''
        self.__sub_project = ''
        self.__execution_subject = '{name} - {env} - #{id} - {status}'
        self.__start_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.__report_libs = []
        self.__local_host = ''
        self.__build = {'id': None, 'url': None, 'name': None, 'result': None, 'duration': None, 'date': None}

        self.messages = Messages()
        self.logger = AllureFileLogger(logger_path)
        self.lifecycle = AllureLifecycle()
        self.listener = AllureListener(self.lifecycle)
        allure_commons.plugin_manager.register(self.logger)
        allure_commons.plugin_manager.register(self.listener)

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
        self.messages.start_context()
        self.listener.start_suite_container(name, attrs)
        if attrs['id'] == 's1':
            self.__exec_dir = BuiltIn().get_variable_value('${EXECDIR}')
            self.__local_host = BuiltIn().get_variable_value('${LOCAL_HOST}', socket.gethostname())
            self.__task_id = BuiltIn().get_variable_value('${TASKID}', str(uuid1()))
            self.__project = BuiltIn().get_variable_value('${Project}')
            self.__sub_project = BuiltIn().get_variable_value('${Sub_Project}')
            env_name = BuiltIn().get_variable_value('${ENV}', 'QA').upper()
            BuiltIn().set_suite_variable('${ENV}', env_name)
            int_or_ext = BuiltIn().get_variable_value('${IntExt}', 'Internal')
            browser = BuiltIn().get_variable_value('${Browser}', 'Chrome')
            self.__run_type = BuiltIn().get_variable_value('${RunType}', 'Smoke')
            self.__report_db = BuiltIn().get_variable_value('${ReportDB}', 'sqlite')
            # self.__merge_results = BuiltIn().get_variable_value('${MergeResults}', 'Y')
            # self.__send_email_report = BuiltIn().get_variable_value('${SendEmail}', 'N')
            self.__start_time = datetime.strptime(attrs['starttime'], '%Y%m%d %H:%M:%S.%f')
            self.__execution_subject = ' - '.join(['{name}', env_name, '#{id}', '{status}'])
            BuiltIn().import_variables('${EXECDIR}/resources/${Project}/variables.py')
            # BuiltIn().import_library(
            #     'libraries/TOS/ClientConfig.py',
            #     'host={}'.format(
            #         BuiltIn().get_variable_value('${KUBE_APISERVER_INSECURE_URL}', 'http://localhost:8080')
            #     )
            # )
            for k in self.__build.keys():
                self.__build[k] = BuiltIn().get_variable_value('${BUILD_' + k.upper() + '}')
            # keywords_dir = os.path.join('resources', self.__project, self.__sub_project, 'keywords')
            # for root, dirs, files in os.walk(keywords_dir):
            #     for resource_file in files:
            #         BuiltIn().import_resource(os.path.join(root, resource_file).replace('\\', '/'))
            #         self.__report_libs.append(resource_file.split('.')[0])
            # from run_robot import get_report_database
            # self.__db = get_report_database(self.__report_db, settings.DATABASES)

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
        self.messages.start_context()
        self.listener.start_test_container(name, attrs)
        self.listener.start_test(name, attrs)

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
        self.messages.start_context()
        keyword_type = attrs.get('type')
        # Todo fix value assign
        keyword_name = '{} = {}'.format(attrs.get('assign')[0], name) if attrs.get('assign') else name
        if keyword_type == RobotKeywordType.SETUP:
            self.listener.start_before_fixture(keyword_name)
        elif keyword_type == RobotKeywordType.TEARDOWN:
            self.listener.start_after_fixture(keyword_name)
        else:
            self.listener.start_keyword(name)

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
        messages = self.messages.stop_context()
        keyword_type = attrs.get('type')
        if keyword_type == RobotKeywordType.SETUP:
            self.listener.stop_before_fixture(attrs, messages)
        elif keyword_type == RobotKeywordType.TEARDOWN:
            self.listener.stop_after_fixture(attrs, messages)
        else:
            self.listener.stop_keyword(attrs, messages)

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
        messages = self.messages.stop_context()
        self.listener.stop_test(name, attrs, messages)
        self.listener.stop_test_container(name, attrs)

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
        self.messages.stop_context()
        self.listener.stop_suite_container(name, attrs)

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
        self.messages.push(message)

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
        execution_id = self.merge_results()
        self.__execution_subject = self.__execution_subject.format(
            name=' '.join(['[' + self.__project + ']', self.__sub_project]),
            id=execution_id if execution_id else 0,
            status='SUCCESS'
        )
        for plugin in [self.logger, self.listener]:
            name = allure_commons.plugin_manager.get_name(plugin)
            allure_commons.plugin_manager.unregister(name=name)

    def merge_results(self):
        output_dir = os.path.join(self.__exec_dir, 'out', self.__project, self.__sub_project)
        sys.stdout.write('{0:=^78}\n'.format('Merge Results For ' + self.__project))
        if os.path.isfile(os.path.join(output_dir, 'rerun.xml')):
            project_output = [os.path.join(output_dir, file) for file in ('output.xml', 'rerun.xml')]
            end_time = ExecutionResult(os.path.join(output_dir, 'rerun.xml')).suite.endtime
        else:
            project_output = [os.path.join(output_dir, file) for file in ('output.xml',)]
            end_time = ExecutionResult(os.path.join(output_dir, 'output.xml')).suite.endtime
        start_time = ExecutionResult(os.path.join(output_dir, 'output.xml')).suite.starttime
        rebot(
            *project_output, name=self.__project, log='log', output='output', xunit='xunit', stdout=sys.stdout,
            outputdir=os.path.join(self.__exec_dir, 'out'),
            starttime=start_time,
            endtime=end_time
        )
        return RobotResult.merge_results_into_db(
            os.path.join(self.__exec_dir, 'out', 'output.xml'),
            self.__task_id
        )


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


class Messages(object):
    def __init__(self):
        self._stack = []

    def start_context(self):
        self._stack.append([])

    def stop_context(self):
        return self._stack.pop() if self._stack else list()

    def push(self, message):
        self._stack[-1].append(message) if self._stack else self._stack.append([message])
