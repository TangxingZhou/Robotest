from __future__ import absolute_import, unicode_literals

from celery import Celery
from settings import CELERY_CONFIG

robot = Celery('robot', include=['libs.celery.tasks'])

# Optional configuration, see the application user guide.
robot.conf.update(**CELERY_CONFIG)

if __name__ == '__main__':
    robot.start()
