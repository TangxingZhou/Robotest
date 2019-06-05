#!/usr/bin/env python3
import sys, argparse
from robot.run import run_cli
from libs.pabot import pabot

MAX_ROBOT_PROCESSES = 5


def args_parser(name, description=None, usage='usage: %(prog)s [options] args'):
    parser = argparse.ArgumentParser(prog=name, description=description, usage=usage)
    parser.add_argument( '--processes', action='store', required=False, type=int, choices=range(1, MAX_ROBOT_PROCESSES + 1), dest='robot_processes', help='Run robot in parallel.')
    parser.add_argument('--verbose', action='store_true', required=False, default=True, dest='verbose', help='Show the verbose information, on is by default.')
    return parser


def main():
    parser = args_parser(
        sys.argv[0].rpartition('/')[2],
        description='Run robotframework.\nAuthor: Tangxing Zhou\nE-mail: zhoutangxing@126.com')
    if len(sys.argv) is 1:
        parser.print_help()
        sys.exit(1)
    else:
        pass
    # args = parser.parse_args()
    args, unknown = parser.parse_known_args()
    robot_processes = args.robot_processes
    verbose = args.verbose
    if robot_processes is None:
        run_arguments = unknown
        run_cli(run_arguments)
    else:
        run_arguments = ['--processes', '{}'.format(robot_processes)]
        if verbose:
            run_arguments.extend(['--verbose'])
        run_arguments.extend(unknown)
        pabot.main(run_arguments)


if __name__ == '__main__':
    main()
