import logging
from service.base import BaseAPI
from service.api import moc_api_request

logger = logging.getLogger(__name__)


class DBInstanceAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/auth/logout', 'POST')
    def logout(self):
        return {}

    @moc_api_request('/auth/refresh', 'POST')
    def refresh(self):
        return {}

    @moc_api_request('/user/info', 'POST')
    def get_user_info(self):
        return {}

    @moc_api_request('/instance_/info', 'POST')
    def get_instance_info(self):
        return {}
