import logging
from fixture.internal.instance import env
from service.api import MOCApiClient
from service.api_client import APIClient
from service.utils import SingletonMeta

logger = logging.getLogger(__name__)


class BaseAPI(metaclass=SingletonMeta):
    _default = {}

    def __init__(self, key='default', api_client=None):
        logger.debug(f"Init MOC API instance of class '{self.__class__.__name__}' for account: {key}.")
        if api_client is None:
            api_client = MOCApiClient()
        self.api_client = api_client
        self.provider = env.get_config('provider')
        self.region = env.get_config('region')

    @property
    def api_client(self):
        return self._api_client

    @api_client.setter
    def api_client(self, api_client):
        self._api_client = api_client


class BaseController:
    _api_class = BaseAPI

    def __init__(self, key='default', api_client=None):
        self._api_client = api_client
        self.key = key

    @property
    def provider(self):
        return self.api.provider

    @property
    def region(self):
        return self.api.region

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        if key is None:
            key = 'default'
        self._key = key

    @property
    def api(self):
        if self.key == 'default':
            api_client = self._api_client
        else:
            with APIClient.client_lock:
                api_client = APIClient.clients.get(self.key)
            if not api_client:
                raise Exception(f"Have not logged in for api client of '{self.key}'.")
        _api = self._api_class(self.key, api_client)
        if api_client:
            _api.api_client = api_client
        return _api

    def __repr__(self):
        if self.key != 'default':
            return self.key
