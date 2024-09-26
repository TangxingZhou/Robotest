import allure
from service.base import BaseController
from service.admin.billing.cash.api import *
from service.admin.billing.cash.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class BillingCashController(BaseController):
    _api_class = CashAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('现金充值')
    def recharge(self,
                 org_id,
                 amount,
                 channel: TransactionChannel = TransactionChannel.CorporateTransfer,
                 account='test',
                 remark=None):
        res = self.api.recharge(org_id, amount, channel, account, remark)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"

    @allure.step('查询现金收支记录')
    def get_details(self,
                    _id=None,
                    org_id=None,
                    org_creator=None,
                    start_time=None,
                    end_time=None,
                    status: TransactionStatus = None,
                    transaction_channel: List[TransactionChannel] = None,
                    transaction_type: List[TransactionTypeDetail] = None,
                    income_or_expense: TransactionType = None,
                    page=1,
                    page_size=10):
        if income_or_expense not in ('expense', 'income'):
            logging.warning(f"{income_or_expense} is invalid, must be one of 'expense', 'income'.")
        res = self.api.get_details(_id,
                                   org_id,
                                   org_creator,
                                   start_time,
                                   end_time,
                                   status,
                                   transaction_channel,
                                   transaction_type,
                                   income_or_expense,
                                   page,
                                   page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return CashRecords(**res['data'])
