import logging
from typing import List
from service.base import BaseAPI
from service.api import moc_api_request
from service.admin.instance_.models import *

logger = logging.getLogger(__name__)


class InstanceAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/instances', 'GET')
    def get_instances(self,
                      _id=None,
                      name=None,
                      org_creator=None,
                      org_name=None,
                      payment: List[Payment] = None,
                      plan_charge_type: List[PlanChargeType] = None,
                      status: List[Status] = None,
                      page=1,
                      page_size=15):
        query_params = [
            ('instance_id', _id),
            ('name', name),
            ('org_creator', org_creator),
            ('org_name', org_name),
            ('page', page),
            ('page_size', page_size)
        ]
        if payment is not None:
            for p in payment:
                if p is not None:
                    query_params.append(('payment', p.value))
        if plan_charge_type is not None:
            for t in plan_charge_type:
                if t is not None:
                    query_params.append(('plan_charge_type', t.value))
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status', s.value))
        return None, query_params

    @moc_api_request('/instances', 'PUT')
    def update(self,
               _id,
               cu_limited_monthly: int = None,
               storage_limited: int = None,
               normal_max_cn: int = None,
               normal_min_cn: int = None,
               limited_max_cn: int = None,
               limited_min_cn: int = None,
               **kwargs):
        payload = {"id": _id}
        if cu_limited_monthly is not None:
            payload['cu_limited_monthly'] = cu_limited_monthly
        if storage_limited is not None:
            payload['storage_limited'] = storage_limited
        if normal_max_cn is not None:
            payload['normal_max_cn'] = normal_max_cn
        if normal_min_cn is not None:
            payload['normal_min_cn'] = normal_min_cn
        if limited_max_cn is not None:
            payload['limited_max_cn'] = limited_max_cn
        if limited_min_cn is not None:
            payload['limited_min_cn'] = limited_min_cn
        payload.update(**kwargs)
        return payload

    @moc_api_request('/instances/detail', 'GET')
    def get_detail(self, _id):
        """
        This API seems deprecated and should be removed. Will be replaced by get_instance.
        """
        query_params = [
            ('id', _id),
        ]
        return None, query_params

    @moc_api_request('/instances/{_id}', 'GET')
    def get_instance(self, _id):
        return None, [], {'_id': _id}

    @moc_api_request('/instances/{_id}/cu/logs', 'GET')
    def get_cu_logs(self, _id, _type='CUMonthly', page=1, page_size=100):
        query_params = [
            ('type', _type),
            ('page', page),
            ('page_size', page_size)
        ]
        return None, query_params, {'_id': _id}

    @moc_api_request('/operation_logs', 'GET')
    def get_operation_logs(self, _id, _type='instance_', page=1, page_size=15):
        query_params = [
            ('biz_id', _id),
            ('biz_type', _type),
            ('page', page),
            ('page_size', page_size)
        ]
        return None, query_params
