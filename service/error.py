import re
from enum import Enum


class APIError:

    def __init__(self, **kwargs):
        self.code = kwargs.get('code')
        self.msg = kwargs.get('msg', kwargs.get('message', ''))

    def __eq__(self, other):
        if isinstance(other, Enum):
            return self.code == other.name and True if re.match(re.compile(other.value), self.msg) else False
        elif isinstance(other, APIError):
            return self.code == other.code and self.msg == other.msg
        elif isinstance(other, dict):
            return self.code == other.get('code') and self.msg == other.get('msg')
        else:
            return False

    def is_ok(self):
        return self.code in (0, '0', 'OK', 'ok') and self.msg.upper() == 'OK'

    def __repr__(self):
        return f"APIError(code='{self.code}', msg='{self.msg}')"
