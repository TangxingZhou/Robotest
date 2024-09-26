import logging
from typing import List
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from service.base import BaseAPI
from service.instance_.api import moc_api_request
from service.instance_.billing.models import *
from service.admin.billing.voucher.models import VoucherStatus, VoucherRecordStatus

logger = logging.getLogger(__name__)


class BillingAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/DescribeBillingAccountStat', 'POST')
    def get_stat(self):
        return {}

    @moc_api_request('/DescribeBillingMonthly', 'POST')
    def get_billing_monthly(self,
                            start_time=None,
                            end_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            offset=0,
                            limit=12):
        if start_time is None:
            start_time = f"{(datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') + relativedelta(months=-6)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
        payload = {
            "filters":
                {
                    "start_time": start_time,
                    "end_time": end_time
                },
            "offset": offset,
            "limit": limit
        }
        return payload

    @moc_api_request('/DescribeBillingMonthlyGraph', 'POST')
    def get_billing_monthly_graph(self,
                                  _type: BillingTrendType = BillingTrendType.InstancePlanType,
                                  start_time=None,
                                  end_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')):
        if start_time is None:
            start_time = f"{(datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') + relativedelta(months=-6)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
        payload = {
            "filters":
                {
                    "type": _type.value,
                    "start_time": start_time,
                    "end_time": end_time
                }
        }
        return payload

    @moc_api_request('/DescribeTransactions', 'POST')
    def get_transactions(self,
                         _id=None,
                         start_time=None,
                         end_time=None,
                         offset=0,
                         limit=20):
        filters = {}
        if _id:
            filters['transaction_id'] = _id
        if start_time and end_time:
            filters['start_time'] = start_time
            filters['end_time'] = end_time
        payload = {
            "filters": filters,
            "offset": offset, "limit": limit
        }
        return payload

    @moc_api_request('/DescribeBillingDetails', 'POST')
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
        filters = {}
        if instance_id:
            filters['instance_id'] = instance_id
        if billing_id:
            filters['billing_id'] = billing_id
        if start_time and end_time:
            filters['start_time'] = start_time
            filters['end_time'] = end_time
        if items:
            filters['billing_items'] = [i.value for i in items]
        if types:
            filters['billing_types'] = [i.value for i in types]
        if status:
            filters['status'] = [i.value for i in types]
        payload = {
            "filters": filters,
            "group_by": {dimension: dimension.value, period: period.value},
            "offset": offset, "limit": limit
        }
        return payload


class VoucherAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/ChargeVoucher', 'POST')
    def charge(self, code):
        payload = {"voucher_code": code}
        return payload

    @moc_api_request('/DescribeVouchers', 'POST')
    def details(self,
                start_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                end_time=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                status: List[VoucherStatus] = None,
                sorter_field='expiration_time',
                sorter_desc=False,
                offset=0,
                limit=10):
        payload = {
            "filters": {
                "start_time": start_time,
                "end_time": end_time,
                "status": [s.value for s in status] if status is not None else []
            },
            "sorter": {
                "field": sorter_field,
                "desc": sorter_desc
            },
            "offset": offset,
            "limit": limit
        }
        return payload

    @moc_api_request('/DescribeVoucherStat', 'POST')
    def get_stat(self, code):
        return {}

    @moc_api_request('/DescribeVoucherRecords', 'POST')
    def get_records(self,
                    voucher_id=None,
                    status: VoucherRecordStatus = None,
                    offset=0,
                    limit=10):
        filters = {}
        if voucher_id:
            filters['voucher_id'] = voucher_id
        if status:
            filters['status'] = status.value
        payload = {
            "filters": filters,
            "offset": offset,
            "limit": limit
        }
        return payload
