import pprint
import logging
from enum import Enum
from libs.apis.error import APIError
from libs.apis.api_client import ApiClient
from libs.apis.api_client import APIClient
from libs.apis.utils import SingletonMeta
from libs.apis.utils import obj_to_dict


logger = logging.getLogger(__name__)


class BaseAPI(metaclass=SingletonMeta):
    _default = {}

    def __init__(self, key='default', api_client=None):
        logger.debug(f"Init API instance of class '{self.__class__.__name__}' for account: {key}.")
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

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


class BaseModel:

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            self.code = kwargs.get('code')
        if 'msg' in kwargs or 'message' in kwargs:
            self.msg = kwargs.get('msg', kwargs.get('message'))
        self.__body = kwargs

    @property
    def err(self):
        if hasattr(self, 'code') and hasattr(self, 'msg'):
            api_err = APIError(code=getattr(self, 'code'), msg=getattr(self, 'msg'))
            if api_err.is_ok():
                return None
            else:
                return api_err
        else:
            return None

    def to_dict(self):
        return obj_to_dict(self)

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, self.__class__):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, self.__class__):
            return True

        return self.to_dict() != other.to_dict()


class BaseEnum(Enum):

    def __repr__(self):
        return f'{self.name}: {self.value}'
        # return self.value
