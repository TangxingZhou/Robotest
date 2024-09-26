import allure
from service.api_client import APIClient
from service.base import BaseController
from service.database.api import *
from service.database.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class DBInstanceController(BaseController):
    _api_class = DBInstanceAPI

    def __init__(self, _id=None, api_client=None):
        super().__init__(_id, api_client)

    @property
    def instance_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Instance-Id')

    @allure.step('退出实例的数据库管理平台')
    def logout(self):
        res = self.api.logout()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        with APIClient.client_lock:
            APIClient.clients.pop(self.api.api_client.default_headers.get('X-Instance-Id'))

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
