import allure
from service.api_client import APIClient
from service.admin.account.api import *
from service.admin.account.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class AccountController(object):

    def __init__(self, api_client=None):
        if api_client is None:
            instance_api_client = APIClient.clients.get('admin')
            if instance_api_client:
                api_client = instance_api_client
            else:
                api_client = ApiClient()
        self.api = AccountAPI(api_client)

    @allure.step('查询账户')
    def get_accounts(self,
                     email=None,
                     _type: List[Type] = None,
                     source: List[Source] = None,
                     status: List[Status] = None,
                     page=1,
                     page_size=15):
        res = self.api.get_accounts(email, _type, source, status, page, page_size)
        assert APIError(**res).is_ok()
        return [Account(**a) for a in res['data']['accounts']]

    @allure.step('审批通过')
    def approval(self, _id, approved=True):
        res = self.api.approval(_id, approved)
        assert APIError(**res).is_ok()

    @allure.step('启用账户')
    def enable(self, _id):
        res = self.api.enable(_id)
        assert APIError(**res).is_ok()

    @allure.step('禁用账户')
    def disable(self, _id):
        res = self.api.disable(_id)
        assert APIError(**res).is_ok()

    @allure.step('修改类型')
    def update_type(self, _id, _type: Type):
        res = self.api.update_type(_id, _type)
        assert APIError(**res).is_ok()

    @allure.step('修改来源')
    def update_source(self, _id, source: Source):
        res = self.api.update_source(_id, source)
        assert APIError(**res).is_ok()
