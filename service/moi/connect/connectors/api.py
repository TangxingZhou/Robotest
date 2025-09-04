from service.base import BaseAPI
from service.api import moc_api_request
from service.moi.connect.connectors.models import *

logger = logging.getLogger(__name__)


class ConnectorAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/connectors/list', 'GET')
    def list(self,
             keyword='',
             source_type: List[ConnectorSourceType] = None,
             usage_type: List[ConnectorUsageType] = None,
             status: List[ConnectorStatus] = None,
             order_by: str | ConnectorListOrderBy = '',
             is_desc: bool = False,
             page=1,
             page_size=10):
        query_params = [
            ('keyword', keyword),
            ('order_by', order_by.value if isinstance(order_by, Enum) else order_by),
            ('is_desc', is_desc),
            ('page', page),
            ('page_size', page_size)
        ]
        if source_type is not None:
            for s in source_type:
                if s is not None:
                    query_params.append(('source_type_list', s.value))
        if usage_type is not None:
            for s in usage_type:
                if s is not None:
                    query_params.append(('usage_type', s.value))
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status_list', s.value))
        return None, query_params

    @moc_api_request('/connectors/validate', 'POST')
    def validate(self,
                 name,
                 config: ConnectorConfig,
                 source_type: ConnectorSourceType = ConnectorSourceType.OSS):
        payload = {
            "name": name,
            "source_type": source_type.value,
            "config": {getattr(config, '_type_name'): config.to_dict()} if getattr(config, '_type_name') else config.to_dict()
        }
        return payload

    @moc_api_request('/connectors', 'POST')
    def create(self,
               name,
               config: ConnectorConfig,
               source_type: ConnectorSourceType = ConnectorSourceType.OSS,
               usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        payload = {
            "name": name,
            "source_type": source_type.value,
            "usage_type": [t.value for t in usage_type],
            "config": {getattr(config, '_type_name'): config.to_dict()} if getattr(config, '_type_name') else config.to_dict()
        }
        return payload

    @moc_api_request('/connectors/{id}', 'PUT')
    def update(self,
               _id,
               name,
               config: ConnectorConfig,
               source_type: ConnectorSourceType = ConnectorSourceType.OSS,
               usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        payload = {
            "name": name,
            "source_type": source_type.value,
            "usage_type": [t.value for t in usage_type],
            "config": {getattr(config, '_type_name'): config.to_dict()} if getattr(config, '_type_name') else config.to_dict()
        }
        return payload, [], {'id': _id}

    @moc_api_request('/connectors/mo/check_table_name', 'POST')
    def check_mo_table_name(self, _id, database, table):
        return {"connector_id": _id, "database": database, "table": table}

    @moc_api_request('/connectors/{id}', 'DELETE')
    def delete(self, _id):
        return None, [], {'id': _id}
