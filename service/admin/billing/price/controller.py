import allure
from service.base import BaseController
from service.admin.billing.price.api import *
from service.admin.billing.price.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class BillingStandardPriceController(BaseController):
    _api_class = StandardPriceAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('查看serverless实例标准价格')
    def get_serverless_price(self, page=1, page_size=20):
        res = self.api.get_price(page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        for c in res['data']['serverless']:
            if c['provider'] == self.provider and c['region'] == self.region:
                return ServerlessPrice(**c)

    @allure.step('查看standard实例标准价格')
    def get_standard_price(self, page=1, page_size=20):
        res = self.api.get_price(page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        for c in res['data']['standard']:
            if c['provider'] == self.provider and c['region'] == self.region:
                return StandardPrice(**c)

    @allure.step('查看standard实例规格')
    def get_capacities(self):
        res = self.api.get_capacities()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        for c in res['data']['data']:
            if c['provider'] == self.provider:
                return c['node_capacities']['capacities']

    @allure.step('查看standard实例购买时长')
    def get_periods(self):
        res = self.api.get_capacities()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        for c in res['data']['data']:
            if c['provider'] == self.provider:
                return c['periods']
