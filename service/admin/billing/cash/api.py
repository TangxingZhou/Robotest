import logging
from typing import List
from service.base import BaseAPI
from service.api import moc_api_request
from service.admin.billing.cash.models import *

logger = logging.getLogger(__name__)


class CashAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/balance/recharge', 'POST')
    def recharge(self,
                 org_id,
                 amount,
                 channel: TransactionChannel = TransactionChannel.CorporateTransfer,
                 account='test',
                 remark=None):
        payload = {
            "org_id": org_id,
            "amount": amount,
            "transaction_channel": channel.value,
            "transaction_account": account
        }
        if remark:
            payload['remark'] = remark
        return payload

    @moc_api_request('/transaction/detail', 'GET')
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
        query_params = [
            ('transaction_id', _id),
            ('org_id', org_id),
            ('org_creator', org_creator),
            ('start_time', start_time),
            ('end_time', end_time),
            ('status', status.value),
            ('income_or_expense', income_or_expense),
            ('page', page),
            ('page_size', page_size)
        ]
        if transaction_type is not None:
            for t in transaction_type:
                if t is not None:
                    query_params.append(('transaction_type', t.value))
        if transaction_channel is not None:
            for c in transaction_channel:
                if c is not None:
                    query_params.append(('transaction_channel', c.value))
        return None, query_params
