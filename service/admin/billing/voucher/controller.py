import allure
from service.base import BaseController
from service.admin.billing.voucher.api import *
from service.admin.billing.voucher.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class BillingVoucherController(BaseController):
    _api_class = VoucherAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('创建代金券')
    def create(self,
               value,
               count,
               effective_time,
               effective_period,
               expiration_time,
               source: VoucherSource = VoucherSource.RechargeBonus):
        res = self.api.create(value,
                              count,
                              effective_time,
                              effective_period,
                              expiration_time,
                              source)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"

    @allure.step('查询卡券列表')
    def list(self,
             _id=None,
             face_value_min=None,
             face_value_max=None,
             org_id=None,
             start_time=None,
             end_time=None,
             activated: bool = None,
             status: List[VoucherStatus] = None,
             sorter_field='expiration_time',
             sorter_desc=False,
             page=1,
             page_size=10):
        res = self.api.list(_id,
                            face_value_min,
                            face_value_max,
                            org_id,
                            start_time,
                            end_time,
                            activated,
                            status,
                            sorter_field,
                            sorter_desc,
                            page,
                            page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return Vouchers(**res['data'])

    @allure.step('查找新建的代金券')
    def list_created(self, face_value, effective_time, sorter_field='effective_time', sorter_desc=True):
        return self.list(face_value_min=face_value,
                         face_value_max=face_value,
                         start_time=effective_time,
                         end_time=effective_time,
                         activated=False,
                         sorter_field=sorter_field,
                         sorter_desc=sorter_desc)

    @allure.step('查看代金券激活码')
    def get_activation_code(self, _id):
        res = self.api.get_activation_code(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return Voucher(**res['data'])
        # return res['data']['activation_code']

    @allure.step('查看卡券使用情况')
    def get_records(self,
                    voucher_id=None,
                    org_id=None,
                    start_time=None,
                    end_time=None,
                    status: VoucherRecordStatus = None,
                    page=1,
                    page_size=10):
        res = self.api.get_records(voucher_id,
                                   org_id,
                                   start_time,
                                   end_time,
                                   status,
                                   page,
                                   page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return VoucherRecords(**res['data'])
