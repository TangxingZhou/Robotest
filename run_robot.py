#!/usr/bin/env python3
import os
import sys
import argparse
import re
from robot.run import run_cli
from robot.run import RobotFramework
from robot.conf import RobotSettings
from robot.model import ModelModifier
from robot.output import LOGGER
from robot.utils import unic
from robot.running.builder import TestSuiteBuilder
from libs.pabot import pabot
from libs.celery.tasks import run_test

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
        self.__suite_sources = []

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
                    arguments = self.__robot_args + [
                        '--variable', 'Project:{}'.format(project),
                        '--variable', 'Sub_Project:{}'.format(sub_project),
                        '--outputdir', os.path.join('out', project, sub_project),
                        '--prerunmodifier',
                        '{}:{}'.format('libs.robot.prerun.Modifier', int(test_id.groups()[0]) - 1),
                        suite_relpath
                    ]
                    # TODO
                    res = run_test.delay(arguments)

    def parse_arguments(self, cli_args):
        options, arguments = super(Robot, self).parse_arguments(cli_args)
        self.__robot_args = cli_args[:-len(arguments)]
        return options, arguments


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
        if args.master_mode:
            if args.worker_mode:
                raise argparse.ArgumentError(
                    parser._actions[1],
                    'Cannot service as master and worker mode at the same time.'
                )
            else:
                Robot().execute_cli(robot_arguments + unknown)
        else:
            if args.worker_mode:
                run_as_worker('celery', '-A', 'libs.celery', 'worker', '-l', 'info')
            else:
                project, sub_project = get_project_info_from_suite_source(unknown[-1])
                robot_output_dir = os.path.join('out', project, sub_project)
                robot_arguments.extend([
                    '--variable', 'Project:{}'.format(project),
                    '--variable', 'Sub_Project:{}'.format(sub_project),
                    '--outputdir', robot_output_dir
                ])
                robot_arguments.extend(unknown)
                if args.robot_processes == 1:
                    origin_rc = run_cli(robot_arguments, exit=False)
                    if args.rerun is True and origin_rc != 0:
                        rerun_robot_options = [
                            '--nostatusrc',
                            '--rerunfailed', os.path.join(robot_output_dir, 'output.xml'),
                            '--output', 'rerun',
                            '--log', 'rerun',
                            '--report', 'NONE'
                        ]
                        if '--debugfile' in robot_arguments:
                            robot_arguments[robot_arguments.index('--debugfile') + 1 ] = 'rerun.log'
                        run_cli(rerun_robot_options + robot_arguments)
                    else:
                        sys.exit(origin_rc)
                else:
                    pabot_options = ['--processes', '{}'.format(args.robot_processes)]
                    if args.verbose:
                        pabot_options.append('--verbose')
                    pabot_options.extend(robot_arguments)
                    pabot.main(pabot_options)


if __name__ == '__main__':
    main()
