#!/usr/bin/env python3
import os, sys, argparse
from robot.run import run_cli
from libs.pabot import pabot

MAX_ROBOT_PROCESSES = 5


def args_parser(name, description=None, usage='usage: %(prog)s [options] args'):
    parser = argparse.ArgumentParser(prog=name, description=description, usage=usage)
    parser.add_argument('--processes', action='store', required=False, type=int, default=1,
                        choices=range(1, MAX_ROBOT_PROCESSES + 1), dest='robot_processes',
                        help='Run robot in parallel.')
    parser.add_argument('--rerun', action='store_true', required=False, default=False, dest='rerun',
                        help='Rerun the tests fail, it\'s false by default.')
    parser.add_argument('--verbose', action='store_true', required=False, default=False, dest='verbose',
                        help='Show the verbose information, off is by default.')
    return parser


def main():
    parser = args_parser(
        sys.argv[0].rpartition('/')[2],
        description='Run tests with robot.\n'
                    'Author: Tangxing Zhou\n'
                    'Company: Transwarp\n'
                    'E-mail: tangxing.zhou@transwarp.io'
    )
    robot_arguments = [
        '--pythonpath', os.path.dirname(os.path.abspath(__file__)),
        '--listener', 'libraries.robot.listeners.Listener2',
        '--exclude', 'Skip',
        '--debugfile', 'debug.log'
    ]
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        exec_dir = os.path.dirname(os.path.abspath(__file__))
        robot_entry = os.path.join(exec_dir, sys.argv[-1])
        if os.path.exists(robot_entry):
            if os.path.isfile(robot_entry):
                robot_path = os.path.relpath(os.path.dirname(robot_entry), exec_dir)
            elif os.path.isdir(robot_entry):
                robot_path = os.path.relpath(robot_entry, exec_dir)
            else:
                sys.stdout.write('[Robot ERROR]: The start path {} is invalid.\n'.format(sys.argv[-1]))
                sys.exit(1)
            paths = os.path.relpath(robot_path, 'tests').split(os.path.sep)
            if len(paths) == 1:
                if paths[0].startswith('.'):
                    robot_output_dir = 'out/'
                else:
                    robot_output_dir = os.path.join('out', paths[0])
            else:
                robot_output_dir = os.path.join('out', paths[0], paths[1])
        else:
            sys.stdout.write('[Robot ERROR]: The start path is not specified or doesn\'t exists.\n')
            sys.exit(1)
    args, unknown = parser.parse_known_args()
    robot_arguments.extend(['--outputdir', robot_output_dir])
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
                robot_arguments[robot_arguments.index('--debugfile') + 1] = 'rerun.log'
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
