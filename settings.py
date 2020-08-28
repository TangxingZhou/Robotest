import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'engine': 'libs.databases.sqlite',
        'db': 'robot_results.db'
    },
    'mysql': {
        'engine': 'libs.databases.mysql',
        'host': '172.26.0.13',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'robot_results'
    }
}

# https://docs.celeryproject.org/en/stable/userguide/configuration.html#configuration
CELERY_CONFIG = {
    'broker_url': 'amqp://guest@172.26.0.13:5672',
    'result_backend': 'db+mysql://root:123456@172.26.0.13:3306/tests',
    'task_serializer':'json',
    'result_serializer': 'json',
    'accept_content': ['application/json'],
    'timezone': 'Asia/Shanghai',
    'enable_utc': True
}
