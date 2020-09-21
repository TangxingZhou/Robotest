from __future__ import absolute_import, unicode_literals

import os
from .celery import robot
from robot.run import run_cli


@robot.task
def run_test(arguments):
    for index, arg in enumerate(arguments):
        arg = arg.replace('\\', os.path.sep)
        arg = arg.replace('/', os.path.sep)
        arguments[index] = os.path.normpath(arg)
    return run_cli(['--variable', 'TASKID:' + run_test.request.id] + arguments, exit=False)
