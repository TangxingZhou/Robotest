import logging
from service.base import BaseAPI
from service.api import moc_api_request

logger = logging.getLogger(__name__)


class StandardPriceAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/price', 'GET')
    def get_price(self, page=1, page_size=20):
        return None, [('page', page), ('page_size', page_size)]

    @moc_api_request('/capacities', 'GET')
    def get_capacities(self):
        return

    @moc_api_request('/periods', 'GET')
    def get_periods(self):
        return
