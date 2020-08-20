from __future__ import absolute_import, unicode_literals

from .celery import robot
from robot.run import run_cli


@robot.task
def run_test(arguments):
    return run_cli(arguments, exit=False)
