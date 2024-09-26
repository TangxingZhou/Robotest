import logging
from typing import List
from service.base import BaseAPI
from service.api import moc_api_request
from service.admin.account.models import *

logger = logging.getLogger(__name__)


class AccountAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/accounts', 'GET')
    def get_accounts(self,
                     email=None,
                     _type: List[Type] = None,
                     source: List[Source] = None,
                     status: List[Status] = None,
                     page=1,
                     page_size=15):
        query_params = [
            ('email', email),
            ('page', page),
            ('page_size', page_size)
        ]
        if _type is not None:
            for t in _type:
                if t is not None:
                    query_params.append(('type', t.value))
        if source is not None:
            for s in source:
                if s is not None:
                    query_params.append(('source', s.value))
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status', s.value))
        return None, query_params

    @moc_api_request('/accounts/approval', 'PUT')
    def approve(self, _id, approved=True):
        payload = {"id": _id, "approved": approved}
        return payload

    @moc_api_request('/accounts/status', 'PUT')
    def enable(self, _id):
        payload = {"id": _id, "status": 'normal'}
        return payload

    @moc_api_request('/accounts/status', 'PUT')
    def disable(self, _id):
        payload = {"id": _id, "status": Status.Blocked.value}
        return payload

    @moc_api_request('/accounts/{_id}/type', 'PUT')
    def update_type(self, _id, _type: Type):
        payload = {"type": _type.value}
        return payload, [], {'_id': _id}

    @moc_api_request('/accounts/{_id}/source', 'PUT')
    def update_source(self, _id, source: Source):
        payload = {"source": source.value}
        return payload, [], {'_id': _id}
