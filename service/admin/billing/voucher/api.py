import logging
from typing import List
from service.base import BaseAPI
from service.api import moc_api_request
from service.admin.billing.voucher.models import *

logger = logging.getLogger(__name__)


class VoucherAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/vouchers', 'POST')
    def create(self,
               value,
               count,
               effective_time,
               effective_period,
               expiration_time,
               source: VoucherSource = VoucherSource.RechargeBonus):
        payload = {
            "face_value": value,
            "count": count,
            "effective_time": effective_time,
            "effective_period": effective_period,
            "expiration_time": expiration_time,
            "source": source.value
        }
        return payload

    @moc_api_request('/vouchers', 'GET')
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
        query_params = [
            ('id', _id),
            ('face_value_min', face_value_min),
            ('face_value_max', face_value_max),
            ('org_id', org_id),
            ('start_time', start_time),
            ('end_time', end_time),
            ('activated', activated),
            ('sorter_field', sorter_field),
            ('sorter_desc', sorter_desc),
            ('page', page),
            ('page_size', page_size)
        ]
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status', s.value))
        return None, query_params

    @moc_api_request('/vouchers/activation_code', 'GET')
    def get_activation_code(self, _id):
        return None, [('id', _id)]

    @moc_api_request('/vouchers/record', 'GET')
    def get_records(self,
                    voucher_id=None,
                    org_id=None,
                    start_time=None,
                    end_time=None,
                    status: VoucherRecordStatus = None,
                    page=1,
                    page_size=10):
        query_params = [
            ('voucher_id', voucher_id),
            ('org_id', org_id),
            ('start_time', start_time),
            ('end_time', end_time),
            ('status', status.value),
            ('page', page),
            ('page_size', page_size)
        ]
        return None, query_params
