import pprint
import logging
from enum import Enum
from service.error import APIError

logger = logging.getLogger(__name__)


class BaseModel:

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            self.code = kwargs.get('code')
        if 'msg' in kwargs or 'message' in kwargs:
            self.msg = kwargs.get('msg', kwargs.get('message'))

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
        result = {}

        for attr in dir(self):
            if attr in ('openapi_types', 'attribute_map', 'err'):
                continue
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                value = getattr(self, attr)
                if isinstance(value, list):
                    result[attr] = list(map(
                        lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                        value
                    ))
                elif hasattr(value, "to_dict"):
                    result[attr] = value.to_dict()
                elif isinstance(value, dict):
                    result[attr] = dict(map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict") else item,
                        value.items()
                    ))
                elif isinstance(value, Enum):
                    result[attr] = value.value
                else:
                    result[attr] = value
        return result

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
