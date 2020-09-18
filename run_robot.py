#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import re
import importlib
from robot.run import run_cli
from robot.run import RobotFramework
from robot.conf import RobotSettings
from robot.model import ModelModifier
from robot.output import LOGGER
from robot.utils import unic
from robot.running.builder import TestSuiteBuilder
import settings
from libs.pabot import pabot
from libs.celery.tasks import run_test
from libs.reporting.robot_output_xml import *
from libs.reporting.email_report import *

EXEC_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_ROBOT_PROCESSES = 5


def args_parser(name, description=None, usage='usage: %(prog)s [options] args'):
    parser = argparse.ArgumentParser(prog=name, description=description, usage=usage)
    parser.add_argument('--worker', action='store_true', required=False, default=False, dest='worker_mode',
                        help='Run tests in worker mode, normal mode by default.')
    parser.add_argument('--master', action='store_true', required=False, default=False, dest='master_mode',
                        help='Run tests in master mode, normal mode by default.')
    parser.add_argument('--processes', action='store', required=False, type=int, default=1,
                        choices=range(1, MAX_ROBOT_PROCESSES + 1), dest='robot_processes',
                        help='Run robot in parallel.')
    parser.add_argument('--rerun', action='store_true', required=False, default=False, dest='rerun',
                        help='Rerun the tests fail, it\'s false by default.')
    parser.add_argument('--db', action='store', required=False, default='sqlite', dest='database',
                        help='Store the test results into the database, it\'s sqlite by default.')
    parser.add_argument('--verbose', action='store_true', required=False, default=False, dest='verbose',
                        help='Show the verbose information, off is by default.')
    return parser


def get_project_info_from_suite_source(suite_source):
    project, sub_project = 'Unknown', ''
    suite_entry = os.path.abspath(suite_source)
    if os.path.exists(suite_entry):
        if os.path.isfile(suite_entry):
            paths = os.path.relpath(os.path.dirname(suite_entry), os.path.join(EXEC_DIR, 'tests')).split(os.path.sep)
        elif os.path.isdir(suite_entry):
            paths = os.path.relpath(suite_entry, os.path.join(EXEC_DIR, 'tests')).split(os.path.sep)
        else:
            paths = ['Unknown', '']
        if len(paths) == 1:
            if not paths[0].startswith('.'):
                project = paths[0]
        else:
            project, sub_project = paths[0], paths[1]
    return project, sub_project


class Robot(RobotFramework):

    def __init__(self):
        super(Robot, self).__init__()
        self.__robot_args = []
        self.tasks_id = []

    def main(self, datasources, **options):
        settings = RobotSettings(options)
        LOGGER.register_console_logger(**settings.console_output_config)
        LOGGER.info('Settings:\n%s' % unic(settings))
        builder = TestSuiteBuilder(settings['SuiteNames'], settings.extension, settings.rpa, settings.run_empty_suite)
        suite = builder.build(*datasources)
        settings.rpa = suite.rpa
        if settings.pre_run_modifiers:
            suite.visit(ModelModifier(settings.pre_run_modifiers,
                                      settings.run_empty_suite, LOGGER))
        suite.configure(**settings.suite_config)
        self.visit_tests(suite)
        return 0

    def visit_tests(self, suite):
        if suite.suites:
            for mysuite in suite.suites:
                self.visit_tests(mysuite)
        else:
            for test in suite.tests:
                test_id = re.search(r't(\d+)', test.id)
                if test_id:
                    suite_relpath = os.path.relpath(suite.source, EXEC_DIR)
                    project, sub_project = get_project_info_from_suite_source(suite_relpath)
                    task_id = str(uuid1())
                    arguments = self.__robot_args + [
                        '--variable', 'Project:{}'.format(project),
                        '--variable', 'Sub_Project:{}'.format(sub_project),
                        '--outputdir', os.path.join('out', project, sub_project),
                        '--prerunmodifier',
                        '{}:{}'.format('libs.robot.prerun.Modifier', int(test_id.groups()[0]) - 1),
                        '--variable', 'TASKID:{}'.format(task_id),
                        suite_relpath
                    ]
                    # TODO
                    self.tasks_id.append(task_id)
                    res = run_test.delay(arguments)

    def parse_arguments(self, cli_args):
        options, arguments = super(Robot, self).parse_arguments(cli_args)
        self.__robot_args = cli_args[:-len(arguments)]
        return options, arguments


def get_report_database(name, database):
    if name in database:
        db_engine = database[name]['engine']
        db_class = name[0].upper() + name[1:]
        try:
            db_cls = getattr(importlib.import_module(db_engine), db_class)
            return db_cls(**database[name])
        except Exception as e:
            sys.stdout.write('[Database ERROR]: Fails to connect to database {}\n{}\n'.format(name, e))


def send_email_report(project, sub_project='', *executions_ids):
    if len(executions_ids) == 0:
        return
    elif len(executions_ids) == 1:
        report_id = executions_ids[0]
    else:
        report_id = '-'.join([str(min(executions_ids)), str(max(executions_ids))])
    robot_build, all_statistics, suites_statistics, tags_statistics, tests_statistics = \
        RobotResult.retrieve_report(EXEC_DIR, project, sub_project, report_id)
    try:
        email_template = os.path.normpath(settings.EMAIL['template'])
        email_client = EmailReport(*[settings.EMAIL[k] for k in ('server', 'user', 'password', 'recipients')])
    except Exception as e:
        sys.stderr.write('[Email ERROR]: Fails to retrieve email info from {}\n{}\n'.format(
            os.path.normpath(os.path.join(EXEC_DIR, 'settings.py')), e
        ))
        return
    try:
        email_content = EmailReport.render(
            email_template_file=email_template,
            out_email_file=os.path.join(EXEC_DIR, 'out', project, 'email_report.html'),
            build=robot_build,
            statistics=(
                {'title': 'Total Statistics', 'records': all_statistics},
                {'title': 'Statistics by Tag', 'records': tags_statistics},
                {'title': 'Statistics by Suite', 'records': suites_statistics}
            ),
            tests=tests_statistics
        )
        email_subject = '{title} - #{id} - {result}'.format(
            title=' '.join(['[' + robot_build['project'] + ']', robot_build['name']]),
            id=robot_build['id'],
            result=robot_build['result']
        )
        email_client.send(subject=email_subject, content=email_content)
    except Exception as e:
        sys.stderr.write('[Email ERROR]: Fails to send out report email\n{}\n'.format(e))
    finally:
        email_client.quit()


def run_as_worker(*args):
    from celery.bin.celery import main as _main
    sys.exit(_main(args))


def main():
    parser = args_parser(
        sys.argv[0].rpartition('/')[2],
        description='Run tests with robot.\n'
                    'Author: Tangxing Zhou\n'
                    'Company: Transwarp\n'
                    'E-mail: tangxing.zhou@transwarp.io'
    )
    venv_pythonpath = os.path.join(
        EXEC_DIR,
        '.venv', 'lib',
        'python{major}.{minor}'.format(major=sys.version_info.major, minor=sys.version_info.minor), 'site-packages'
    )
    robot_arguments = [
        # '--pythonpath', EXEC_DIR,
        '--listener', 'libs.robot.listeners.Listener2',
        '--exclude', 'Skip',
        '--debugfile', 'debug.log'
    ]
    if os.path.isdir(venv_pythonpath):
        robot_arguments.extend(['--pythonpath', venv_pythonpath])
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        args, unknown = parser.parse_known_args()
        project, sub_project = get_project_info_from_suite_source(unknown[-1])
        robot_output_dir = os.path.join('out', project, sub_project)
        shutil.rmtree(robot_output_dir)
        robot_arguments.extend(['--variable', 'ReportDB:'+args.database])
        if args.worker_mode:
            if args.master_mode:
                raise argparse.ArgumentError(
                    parser._actions[1],
                    'Cannot service as master and worker mode at the same time.'
                )
            else:
                run_as_worker('celery', '-A', 'libs.celery', 'worker', '-l', 'info')
        else:
            RobotResult(get_report_database(args.database, settings.DATABASES).session)
            if args.master_mode:
                robot = Robot()
                robot.execute_cli(robot_arguments + unknown)
                send_email_report(project, sub_project,
                                  *RobotResult.retrieve_executions_id(*robot.tasks_id))
            else:
                robot_arguments.extend([
                    '--variable', 'Project:{}'.format(project),
                    '--variable', 'Sub_Project:{}'.format(sub_project),
                    '--outputdir', robot_output_dir
                ] + unknown)
                if args.robot_processes == 1:
                    task_id = str(uuid1())
                    tasks_id = [task_id]
                    run_rc = run_cli(['--variable', 'TASKID:{}'.format(task_id)] + robot_arguments, exit=False)
                    if args.rerun is True and run_rc != 0:
                        rerun_task_id = str(uuid1())
                        tasks_id.append(rerun_task_id)
                        rerun_robot_options = [
                            '--nostatusrc',
                            '--rerunfailed', os.path.join(robot_output_dir, 'output.xml'),
                            '--output', 'rerun',
                            '--log', 'rerun',
                            '--report', 'rerun'
                        ]
                        if '--debugfile' in robot_arguments:
                            robot_arguments[robot_arguments.index('--debugfile') + 1] = 'rerun.log'
                        run_rc = run_cli(rerun_robot_options + ['--variable', 'TASKID:' + rerun_task_id] +
                                         robot_arguments, False)
                    send_email_report(project, sub_project, *RobotResult.retrieve_executions_id(*tasks_id))
                    sys.exit(run_rc)
                else:
                    pabot_options = ['--processes', '{}'.format(args.robot_processes)]
                    if args.verbose:
                        pabot_options.append('--verbose')
                    pabot_options.extend(robot_arguments)
                    pabot.main(pabot_options)
            RobotResult.close()


if __name__ == '__main__':
    main()
