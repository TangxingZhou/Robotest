import math
from typing import List
from enum import Enum
from service.models import BaseModel
from service.utils import objects_should_be_equal
from service.database.models import SQLType
from service.mo.models import StatementInfo


class SQLStatus(Enum):
    Running = 'Running'
    Success = 'Success'
    Failed = 'Failed'


class QueryDetail(BaseModel):

    openapi_types = {
        'bytes_scan': 'int',
        'cu': 'float',
        'database': 'str',
        'duration': 'int',
        'query_type': 'service.database.models.SQLType',
        'request_at': 'datetime',
        'response_at': 'datetime',
        'result_count': 'int',
        'rows_read': 'int',
        'session_id': 'str',
        'transaction_id': 'str',
        'statement': 'str',
        'statement_id': 'str',
        'status': 'service.database.query_history.models.SQLStatus',
        'user': 'str',
    }

    attribute_map = {
        'bytes_scan': 'bytes_scan',
        'cu': 'cu',
        'database': 'database',
        'duration': 'duration',
        'query_type': 'query_type',
        'request_at': 'request_at',
        'response_at': 'response_at',
        'result_count': 'result_count',
        'rows_read': 'rows_read',
        'session_id': 'session_id',
        'transaction_id': 'transaction_id',
        'statement': 'statement',
        'statement_id': 'statement_id',
        'status': 'status',
        'user': 'user',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bytes_scan: int = kwargs.get('bytes_scan')
        self.cu: float = kwargs.get('cu')
        self.database = kwargs.get('database')
        self.duration: int = kwargs.get('duration')
        self.query_type: SQLType = SQLType(kwargs.get('query_type')) if kwargs.get('query_type') else None
        self.request_at = kwargs.get('request_at')
        self.response_at = kwargs.get('response_at')
        self.result_count: int = kwargs.get('result_count', 0)
        self.rows_read: int = kwargs.get('rows_read')
        self.session_id = kwargs.get('session_id')
        self.transaction_id = kwargs.get('transaction_id', '')
        self.statement = kwargs.get('statement')
        self.statement_id = kwargs.get('statement_id')
        self.status: SQLStatus = SQLStatus(kwargs.get('status'))
        self.user = kwargs.get('user')

    def __eq__(self, other):
        if self.result_count is None:
            self.result_count = 0
        if self.transaction_id is None:
            self.transaction_id = ''
        if isinstance(other, self.__class__):
            return objects_should_be_equal(self.to_dict(), other.to_dict())
        elif isinstance(other, StatementInfo):
            other = other.to_dict()
            for c in ('account', 'host', 'node_type', 'node_uuid', 'err_code', 'statement_type', 'statement_tag',
                      'statement_fingerprint', 'error', 'exec_plan', 'stats', 'sql_source_type', 'role_id', 'aggr_count'):
                other.pop(c)
            # CU 是float类型，查询历史接口查询到的与statement_info表查询到的有一点误差
            self_dict = self.to_dict()
            math.isclose(self_dict.pop('cu'), other.pop('cu'), abs_tol=1e-4)
            return objects_should_be_equal(self_dict, other)
        elif isinstance(other, dict):
            return objects_should_be_equal(self.to_dict(), other)
        else:
            return False


class QueryHistory(BaseModel):

    openapi_types = {
        'end': 'str',
        'limit': 'int',
        'offset': 'int',
        'total': 'int',
        'start': 'str',
        'records': 'list[service.database.query_history.models.QueryDetail]',
        'code': 'str',
        'msg': 'str'
    }

    attribute_map = {
        'end': 'data.end',
        'limit': 'data.limit',
        'offset': 'data.offset',
        'total': 'data.total',
        'start': 'data.start',
        'records': 'data.query_list',
        'code': 'code',
        'msg': 'msg|message'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.end = kwargs.get('end')
        self.limit: int = kwargs.get('limit')
        self.offset: int = kwargs.get('offset')
        self.total: int = kwargs.get('total')
        self.start = kwargs.get('start')
        self.records: List[QueryDetail] = kwargs.get('records') if kwargs.get('records') else []

    @staticmethod
    def _sort(list_object: List, primary, secondary='request_at'):
        for i in range(len(list_object) - 1):
            for j in range(i + 1, len(list_object)):
                if getattr(list_object[j], primary) == getattr(list_object[i], primary):
                    if getattr(list_object[i], secondary) > getattr(list_object[j], secondary):
                        list_object[i], list_object[j] = list_object[j], list_object[i]
                else:
                    break
        return list_object


class QueryResult(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit: int = kwargs.get('limit')
        self.offset = kwargs.get('offset')
        self.total = kwargs.get('total')
        self.columns = kwargs.get('columns', [])
        self.rows = []
        for i, r in enumerate(kwargs.get('result', [])):
            row = {}
            if len(r) == len(self.columns):
                for j, c in enumerate(r):
                    if c.get('Valid') is True:
                        row[self.columns[j]['name']] = c.get('String')
                    else:
                        raise ValueError(f"Value of column[{j}] '{self.columns[j]['name']}' in row[{i}] '{r}' is not valid.")
            else:
                raise ValueError(f"Column values in row[{i}] '{r}' do not match columns schema '{self.columns}'.")
            self.rows.append(row)

    def get_column_type(self, column_name=''):
        _types = {}
        for c in self.columns:
            _types[c['name']] = c['type']
        if column_name:
            return _types.get(column_name)
        else:
            return _types
