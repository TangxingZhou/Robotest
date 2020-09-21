import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'sqlite': {
        'engine': 'libs.databases.sqlite',
        'db': os.path.join(BASE_DIR, 'out', 'robot_results.db')
    },
    'mysql': {
        'engine': 'libs.databases.mysql',
        'host': '172.26.0.13',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'robot_results'
    },
    'mssql': {
        'engine': 'libs.databases.mssql',
        'host': '172.26.0.13',
        'port': 1433,
        'user': 'SA',
        'password': 'Transwarp1234',
        'db': 'robot_results'
    }
}

EMAIL = {
    'server': 'smtp.126.com',
    'user': 'xxx@126.com',
    'password': 'xxxxxx',
    'recipients': 'a@126.com,b@126.com',
    'template': 'resources/reporting/templates/email_report.html'
}

# https://docs.celeryproject.org/en/stable/userguide/configuration.html#configuration
CELERY_CONFIG = {
    # 'broker_url': 'amqp://myuser:mypassword@hostname:5672/myvhost',
    # 'broker_url': 'amqp://guest@172.26.0.13:5672',
    # 'broker_url': 'redis://:password@hostname:6379/db_number',
    'broker_url': 'redis://172.26.0.13:6379',
    'result_backend': 'redis://172.26.0.13:6379',
    # 'result_backend': 'db+mysql://root:123456@172.26.0.13:3306/tests',
    'task_serializer':'json',
    'result_serializer': 'json',
    'accept_content': ['application/json'],
    'timezone': 'Asia/Shanghai',
    'enable_utc': False
}
