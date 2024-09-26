import allure
from service.base import BaseController
from service.admin.organization.api import *
from service.admin.organization.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class OrganizationController(BaseController):
    _api_class = OrganizationAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('查询组织')
    def get_organizations(self,
                          _id=None,
                          name=None,
                          creator=None,
                          page=1,
                          page_size=15):
        res = self.api.get_organizations(_id, name, creator, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return [Organization(**o) for o in res['data']['orgs']]

    @allure.step('修改免费实例最大个数')
    def update_free_instance_limit(self, _id, free_instance_limit):
        res = self.api.update_free_instance_limit(_id, free_instance_limit)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('修改备注信息')
    def update_remark(self, _id, remark=''):
        res = self.api.update_remark(_id, remark)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"

    @allure.step('查看操作日志')
    def get_operation_logs(self, _id, page=1, page_size=15):
        res = self.api.get_operation_logs(_id, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return res['data']
