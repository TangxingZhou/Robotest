from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'robot_results.db'
    },
    'mysql': {
        # 'ENGINE': 'django.db.backends.mysql',
        'db': 'robot',
        'user': 'root',
        'passwd': '123456',
        'host': '172.26.0.13',
        'port': 3306
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
