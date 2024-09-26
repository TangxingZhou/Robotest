import logging
from service.base import BaseAPI
from service.api import moc_api_request

logger = logging.getLogger(__name__)


class OrganizationAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/orgs', 'GET')
    def get_organizations(self,
                          _id=None,
                          name=None,
                          creator=None,
                          page=1,
                          page_size=15):
        query_params = [
            ('id', _id),
            ('name', name),
            ('creator', creator),
            ('page', page),
            ('page_size', page_size)
        ]
        return None, query_params

    @moc_api_request('/orgs', 'PUT')
    def update_free_instance_limit(self, _id, free_instance_limit):
        payload = {"id": _id, "free_instance_limit": free_instance_limit}
        return payload

    @moc_api_request('/orgs', 'PUT')
    def update_remark(self, _id, remark=''):
        payload = {"id": _id, "remark": remark}
        return payload

    @moc_api_request('/operation_logs', 'GET')
    def get_operation_logs(self, _id, page=1, page_size=15):
        query_params = [
            ('biz_id', _id),
            ('biz_type', 'org'),
            ('page', page),
            ('page_size', page_size)
        ]
        return None, query_params
