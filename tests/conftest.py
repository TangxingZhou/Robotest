import os
import logging
import pytest
from cloud.k8s.client import K8sClient
from cloud.k8s.k8s_api import K8sApi
from service.api_client import APIClient
from fixture.internal.email import Email

logger = logging.getLogger(__name__)
database_platform_obj = DatabasePlatform()


def pytest_sessionstart(session):
    _root_handlers = [h for h in logging.root.handlers if type(h).__name__ == '_FileHandler']
    for logger_name in ('sqlalchemy.engine.Engine', 'sqlalchemy.pool.impl.QueuePool'):
        for h in _root_handlers:
            if not logging.getLogger(logger_name).handlers:
                logging.getLogger(logger_name).addHandler(h)
    logging.getLogger('kubernetes.client.rest').addFilter(lambda record: False if 'response body: %s' == record.msg else True)


def pytest_runtest_setup(item):
    logger.info(f'{item.nodeid} 测试用例开始执行......')


def pytest_runtest_teardown(item):
    logger.info(f'{item.nodeid} 测试用例执行结束......')


@pytest.fixture(name='api_clients', scope='session', autouse=True)
def api_clients():
    return APIClient()


def init_k8s_client(name):
    env = Environment()
    k8s_config = env.get_config(f'k8s_{name}_config')
    try:
        k8s_host = env.get_config(f'k8s_{name}_host')
    except Exception:
        k8s_host = None
    try:
        k8s_ca_cert = env.get_config(f'k8s_{name}_ca_cert')
    except Exception:
        k8s_ca_cert = None
    try:
        k8s_user_cert = env.get_config(f'k8s_{name}_user_cert')
    except Exception:
        k8s_user_cert = None
    try:
        k8s_user_key = env.get_config(f'k8s_{name}_user_key')
    except Exception:
        k8s_user_key = None
    if k8s_config:
        if os.path.isfile(os.path.expanduser(os.path.expandvars(k8s_config))):
            k8s_client = K8sClient(name, k8s_config)
        else:
            kube_configs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                             'cloud', 'kube-configs')
            if not os.path.isdir(kube_configs_path):
                os.makedirs(kube_configs_path)
            config_path = os.path.join(kube_configs_path, f'config.{name}')
            with open(config_path, 'w+') as config_file:
                config_file.write(k8s_config)
            os.chmod(config_path, 0o644)
            k8s_client = K8sClient(name, config_path)
    else:
        k8s_client = K8sClient(name)
        if k8s_host and k8s_ca_cert and k8s_user_cert and k8s_user_key:
            k8s_client.customize(name, k8s_host, k8s_ca_cert, k8s_user_cert, k8s_user_key)
    return k8s_client


@pytest.fixture(name='k8s_api', scope='session')
def k8s_api():
    init_k8s_client('controller')
    return K8sApi(init_k8s_client('unit'))


@pytest.fixture(name='k8s_unit_client', scope='session')
def k8s_unit_client():
    return init_k8s_client('unit')


@pytest.fixture(name='k8s_controller_client', scope='session')
def k8s_controller_client():
    return init_k8s_client('controller')