import os
import allure
import requests
import time
import threading
from cloud.k8s.client import logger
from service.api import MOCApiClient
from service.error import APIError
from kubernetes.client import Configuration
from fixture.internal.instance import env


class APIClient:

    clients = {}
    client_lock = threading.Lock()

    def __init__(self):
        self.login_instance_platform()
        # self.login_admin_platform()
        threading.Thread(target=self.refresh_login_token, args=(self.login_admin_platform,), daemon=True).start()

    @classmethod
    def login_instance_platform(cls, email=env.get_config('email'), password=env.get_config('password'), remember=1):
        payload = {
            'email': email,
            'password': password,
            'remember': remember
        }
        res = requests.post(f"{env.get_config('auth_url')}/login", json=payload)
        assert res.status_code == 200 and res.json().get('code') == 'OK', 'Failed to login to instance_ platform'
        api_client = MOCApiClient(Configuration(host=env.get_config('instance_url')))
        api_client.set_default_header('Access-Token', res.headers.get('Refresh-Token'))
        api_client.set_default_header('Uid', res.json().get('data').get('uid'))
        with cls.client_lock:
            cls.clients[email] = api_client

    @classmethod
    @allure.step('登录实例的数据库管理平台')
    def login_db_platform(cls, url, account_name, username='admin', password=os.getenv('INSTANCE_PASSWORD', 'Admin123')):
        payload = {
            'account_name': account_name,
            'username': username,
            'password': password
        }
        res = requests.post(f"{url}/auth/login", json=payload, cookies=None)
        assert res.status_code == 200, f"{url}/auth/login is not accessible."
        err = APIError(**res.json())
        if err.is_ok():
            api_client = MOCApiClient(Configuration(host=url))
            api_client.set_default_header('Access-Token', res.headers.get('Access-Token'))
            api_client.set_default_header('Uid', res.json().get('data').get('uid'))
            api_client.set_default_header('X-Instance-Id', account_name.replace('_', '-'))
            with cls.client_lock:
                cls.clients[account_name.replace('_', '-')] = api_client
        else:
            logger.warning(f"Failed to login db platform for instance_ '{account_name.replace('_', '-')}'")
            return err

    @classmethod
    def login_admin_platform(cls, username=env.get_config('management_platform_user'), password=env.get_config('management_platform_password')):
        payload = {
            'username': username,
            'password': password
        }
        res = requests.post(
            f"{env.get_config('management_platform_url')}/login",
            json=payload)
        assert res.status_code == 200 and res.json().get('code') == 0, 'failed to login management platform'
        api_client = MOCApiClient(Configuration(host=env.get_config('management_platform_url')))
        api_client.set_default_header('Access-Token', res.headers.get('Access-Token'))
        api_client.set_default_header('Uid', res.headers.get('Uid'))
        with cls.client_lock:
            cls.clients['admin'] = api_client

    @classmethod
    def refresh_login_token(cls, func, interval=10 * 60, *args, **kwargs):
        while True:
            func(*args, **kwargs)
            time.sleep(interval)
