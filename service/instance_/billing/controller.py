from fixture.internal.instance import env
from service.base import BaseController
from service.instance_.billing.api import *
from service.instance_.billing.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class BillingController(BaseController):
    _api_class = BillingAPI

    def __init__(self, account=env.get_config('email'), api_client=None):
        super().__init__(account, api_client)

    def get_stat(self):
        res = self.api.get_stat()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return AccountStat(**res['data'])

    def get_billing_monthly(self,
                            start_time,
                            end_time,
                            offset=0,
                            limit=12):
        res = self.api.get_billing_monthly(start_time, end_time, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return MonthlyBilling(**res['data'])

    def get_billing_monthly_graph(self,
                                  _type: BillingTrendType = BillingTrendType.InstancePlanType,
                                  start_time='',
                                  end_time=''):
        res = self.api.get_billing_monthly_graph(_type, start_time, end_time)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return BillingTrend(**res['data'])

    def get_transactions(self,
                         _id=None,
                         start_time=None,
                         end_time=None,
                         offset=0,
                         limit=20):
        res = self.api.get_transactions(_id, start_time, end_time, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Transaction(**res.get('data'))

    def get_billings(self,
                     instance_id=None,
                     billing_id=None,
                     start_time=None,
                     end_time=None,
                     dimension: BillingDimension = BillingDimension.BillingItem,
                     period: BillingPeriod = BillingPeriod.Hourly,
                     items: List[BillingItem] = None,
                     types: List[BillingType] = None,
                     status: List[BillingStatus] = None,
                     offset=0,
                     limit=20):
        res = self.api.get_billings(instance_id, billing_id, start_time, end_time, dimension, period, items, types, status, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Billing(**res.get('data'))


class VoucherController(BaseController):
    _api_class = VoucherAPI

    def __init__(self, account=env.get_config('email'), api_client=None):
        super().__init__(account, api_client)

    @property
    def provider(self):
        return self.api.provider

    @property
    def region(self):
        return self.api.region

    def charge(self, code):
        res = self.api.charge(code)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    def details(self,
                start_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                status: List[VoucherStatus] = None,
                sorter_field='expiration_time',
                sorter_desc=False,
                offset=0,
                limit=10):
        res = self.api.details(start_time, end_time, status, sorter_field, sorter_desc, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Voucher(**res['data'])

    def get_stat(self):
        res = self.api.get_stat()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return AccountStat(**res['data'])

    def get_records(self,
                    voucher_id=None,
                    status: VoucherRecordStatus = None,
                    offset=0,
                    limit=10):
        res = self.api.get_records(voucher_id, status, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return VoucherRecord(**res['data'])
