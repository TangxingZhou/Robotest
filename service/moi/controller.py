import allure
from service.api_client import APIClient
from service.base import BaseController
from service.moi.api import *
from service.database.models import *
from service.error import APIError
from fixture.internal.instance import env

logger = logging.getLogger(__name__)


class MOIController(BaseController):
    _api_class = MOIAPI

    def __init__(self, _id=None, user=env.get_config('workspace_platform_user'), api_client=None):
        super().__init__(f"{_id}:{user if user else 'admin'}", api_client)

    @property
    def workspace_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Workspace-Id')

    @property
    def user_name(self) -> str:
        return self.api.api_client.default_headers.get('X-User-Name')

    @allure.step('退出工作区')
    def logout(self):
        res = self.api.logout()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        with APIClient.client_lock:
            APIClient.clients.pop(self.api.api_client.default_headers.get('X-Workspace-Id'))

    @allure.step('刷新')
    def refresh(self):
        res = self.api.refresh()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('查看账号详情')
    def get_user_info(self):
        res = self.api.get_user_info()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']

    @allure.step('查看实例详情')
    def get_instance_info(self):
        res = self.api.get_instance_info()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return InstanceInfo(**res['data'])

    def get_mo_client(self, password=env.get_config('workspace_platform_password')) -> MOClient:
        return self.get_instance_info().mo_client(password)
