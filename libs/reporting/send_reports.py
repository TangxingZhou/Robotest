import sys
import os
import importlib
from datetime import datetime, timedelta, timezone
from libs.reporting.smtp import EmailReport
from libs.reporting.robot_results_parser import RobotResultsParser
from libs.reporting.database_writer import DatabaseWriter
from libs.databases.sqlite import Sqlite
from libs.results.jira_service import JiraService
from libs.results.ftp_service import FTPService


class SendReports(object):

    def __init__(self, sources, robot_options):
        self.__db = None
        self.__tr_name = ''
        self.__tr_id = ''
        self.__ts_id = ''
        self.__exec_dir = os.getcwd()
        self.__robot_variables = self.get_variables_from_robot_options(robot_options)
        self.__save_db = self.get_variable(self.__robot_variables, 'ReportToDB', 'N')
        self.__send_email = self.get_variable(self.__robot_variables, 'SendEmail', 'N')
        self.__email_receivers = [s.strip() for s in
                                  self.get_variable(self.__robot_variables, 'EmailReceivers', 'qa@126.com')
                                      .strip().split(',') if s != '']
        self.__update_jira = self.get_variable(self.__robot_variables, 'UpdateJira', 'N')
        env = self.get_variable(self.__robot_variables, 'ENV', 'QA').upper()
        browser = self.get_variable(self.__robot_variables, 'Browser', 'Chrome')
        int_or_ext = self.get_variable(self.__robot_variables, 'IntExt', 'Internal')
        db_type = 'SQL_SERVER'
        if 'outputdir' in robot_options:
            test_run = self._parse_results_to_sqlite_db(robot_options['outputdir'])
            project, sub_project = self.__get_project_name(os.path.normpath(robot_options['outputdir']), 'out')
        else:
            test_run = self._parse_results_to_sqlite_db('')
            project, sub_project = self.__get_project_name(os.path.normpath(sources[0]), 'tests')
        self.__project_variables_module = importlib.import_module('.variables', 'resources.{}'.format(project))
        if self.__update_jira == 'Y':
            self.__jira = JiraService(getattr(self.__project_variables_module, 'Jira_Host'),
                                      getattr(self.__project_variables_module, 'Jira_Project_Key'))
            self.__jira.log_in(self.get_variable(self.__robot_variables, 'LoginID'),
                               self.get_variable(self.__robot_variables, 'LoginPWD'))
        if self.__save_db == 'Y':
            db_info = tuple(map(lambda var: getattr(self.__project_variables_module, var),
                                map(lambda x: db_type + '_' + x, ['HOST', 'USER', 'PSW', 'DB', 'PORT'])))
            ftp_info = tuple(map(lambda var: getattr(self.__project_variables_module, var),
                                map(lambda x: 'FTP' + '_' + x, ['HOST', 'USER', 'PSW'])))
            # self.__db = SaveTestResults(*db_info)
            self.__ftp = FTPService(*ftp_info)
            for root, dirs, files in os.walk(os.path.join('out', project, sub_project, 'snapshots')):
                self.__snapshots = [os.path.join('out', project, sub_project, 'snapshots', f) for f in files]
            if self.__db is None:
                sys.stdout.write('[Report ERROR]: The connection to {} is not established @{}.'.format(db_type, ', '.join(db_info)))
                sys.exit(1)
            else:
                tr_starttime, tr_endtime = tuple(
                    map(lambda t: self.convert_datetime_timezone(datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f'), 8, 0),
                        (test_run[4], test_run[5])))
                self.__tr_name = '-'.join((project, sub_project, env, tr_starttime.strftime('%Y-%m-%d %H-%M-%S')))
                # self.__tr_id = self.__db.get_tr_id(self.__tr_name, env)
                # self.__db.update_tr_time((tr_starttime.strftime('%Y-%m-%d %H:%M:%S'),
                #                           tr_endtime.strftime('%Y-%m-%d %H:%M:%S'), self.__tr_name))
                self.__ts_id = self.__db.get_ts_id('{}_{}'.format(int_or_ext, browser), int_or_ext, browser)
                if len(self.__snapshots) > 0:
                    self.__ftp.cwd(os.path.join(
                        '/', 'AutomationResults', '{}_results'.format(project.lower()), 'Screenshot', self.__tr_name,
                        '{}_{}'.format(int_or_ext, browser)).replace('\\', '/'))
                self._store_results_to_db(test_run[0], True)
            self.__send_email_report(True if self.__send_email == 'Y' else False,
                                     teamcity_build_number=self.get_variable(self.__robot_variables, 'BuildNumber', '0'),
                                     teamcity_build_id=self.get_variable(self.__robot_variables, 'BuildID', '0'),
                                     teamcity_build_type_id=self.get_variable(self.__robot_variables, 'BuildTypeID', '0'),
                                     teamcity_build_results_tab=self.get_variable(self.__robot_variables, 'BuildResultsTab', 'buildResultSummary'))
            # self.__db.close()
            self.__ftp.close()
        self.__parser.close()

    @classmethod
    def __get_project_name(cls, path, start_dir):
        if path.startswith(start_dir):
            paths = os.path.relpath(path, start_dir).split(os.path.sep)
            if len(paths) == 1:
                if paths[0].startswith('.'):
                    sys.stdout.write('Cannot get project name from path {}.'.format(path))
                    sys.exit(1)
                else:
                    return paths[0], ''
            else:
                return paths
        else:
            sys.stdout.write('The path {} should start with {}.'.format(path, start_dir))
            sys.exit(1)

    @classmethod
    def convert_datetime_timezone(cls, time, source, target):
        return time.replace(tzinfo=timezone(timedelta(hours=source))).astimezone(timezone(timedelta(hours=target)))

    @classmethod
    def get_variables_from_robot_options(cls, options):
        variables = {}
        for pair in options['variable']:
            k, v = pair.split(':', 1)
            variables[k] = v
        return variables

    @classmethod
    def get_variable(cls, variables, key, default=''):
        if key in variables:
            return variables[key]
        else:
            return default

    def _store_results_to_db(self, tr_id, save_db=False):
        if save_db:
            jira_project_key = getattr(self.__project_variables_module, 'Jira_Project_Key')
            snapshots = {}
            uploaded_snapshots = []
            for snapshot in self.__snapshots:
                snapshots[snapshot] = os.path.getctime(snapshot)
            for test in self.__parser.get_tests_of_test_run(tr_id):
                for tag in tuple(map(lambda t: t[1], self.__parser.get_tags_of_test(test[0]))):
                    if tag.startswith(jira_project_key) and hasattr(self, '_SendReports__jira') and self.__jira.log_in:
                        self.__jira.update_test_status_in_cycle('Regression', 'Automation', tag, test[4])
                # self.__parser.publish_keywords.clear()
                tc_name = '_'.join((test[2], test[3]))
                # tc_id = self.__db.get_tc_id(tc_name)
                test_keywords = self.__parser.get_keywords_of_test(tr_id, test[0])
                for test_keyword in test_keywords:
                    self.__parser.get_child_keywords_of_keyword(test_keyword[0])
                for index, keyword in enumerate(self.__parser.publish_keywords):
                    if keyword[0] in tuple(map(lambda k: k[0], test_keywords)):
                        # TODO
                        pass
                    else:
                        pass
                    if keyword[2] == 'PASS':
                        keyword_status = 1
                    elif keyword[2] == 'FAIL':
                        keyword_status = 2
                    else:
                        keyword_status = 3
                    if keyword[4] is None:
                        keyword_message = ''
                    else:
                        keyword_message = keyword[4]
                    keyword_starttime = self.convert_datetime_timezone(
                        datetime.strptime(keyword[5], '%Y%m%d %H:%M:%S.%f'), 8, 0).strftime('%Y-%m-%d %H:%M:%S')
                    # TODO: Update the keyword status
                    for k, v in snapshots.items():
                        kw_starttime = datetime.strptime(self.__parser.publish_keywords[-1 - index][5], '%Y%m%d %H:%M:%S.%f').timestamp()
                        kw_endtime = datetime.strptime(self.__parser.publish_keywords[-1 - index][6], '%Y%m%d %H:%M:%S.%f').timestamp()
                        if tc_name in k and k not in uploaded_snapshots and kw_starttime <= v and kw_endtime >=v:
                            uploaded_snapshots.append(k)
                            self.__ftp.upload(k, '{}_{}.png'.format(tc_name, len(self.__parser.publish_keywords) - index))
                for k, v in snapshots.items():
                    if tc_name in k and k not in uploaded_snapshots:
                        uploaded_snapshots.append(k)
                        self.__ftp.upload(k, '{}_{}.png'.format(tc_name, len(self.__parser.publish_keywords)))

    def _parse_results_to_sqlite_db(self, output_dir):
        test_run = ()
        verbose_stream = sys.stdout
        output_xml_path = os.path.join(output_dir, 'output.xml')
        conn = Sqlite(os.path.join(output_dir, 'robot_results.db'), verbose_stream)
        _sqlite = DatabaseWriter(conn.connection, verbose_stream)
        self.__parser = RobotResultsParser(_sqlite, verbose_stream)
        try:
            test_run = self.__parser.xml_to_db(output_xml_path)
            _sqlite.commit()
        except Exception as e:
            sys.stderr.write('[Sqlite ERROR]: {}\n\n'.format(e))
            exit(1)
        return test_run

    def __send_email_report(self, send_email=False, **kwargs):
        if send_email:
            email_info = tuple(map(lambda var: getattr(self.__project_variables_module, var),
                                   map(lambda x: 'REPORT_EMAIL' + '_' + x, ['HOST', 'FROM'])))
            email_smtp = EmailReport(*email_info, self.__email_receivers)
            email_smtp.send(self.__db.db_client, self.__tr_id, self.__tr_name, **kwargs)
