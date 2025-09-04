import pprint
import logging
from enum import Enum
from service.error import APIError
from service.utils import obj_to_dict

logger = logging.getLogger(__name__)


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

