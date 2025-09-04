import logging
from service.api import MOCApiClient
from kubernetes.client import Configuration
from service.api import moc_api_request
from service.moi.connect.connectors.models import DifyConnectorConfig

logger = logging.getLogger(__name__)


class DifyAPI:

    def __init__(self, dify_connector: DifyConnectorConfig, api_client=None):
        if api_client is None:
            api_client = MOCApiClient(Configuration(
                host=dify_connector.api_url,
                api_key={'authorization': dify_connector.api_key},
                api_key_prefix={'authorization': 'Bearer'}
            ))
        self.api_client = api_client

    @moc_api_request('/datasets', 'POST', status_code=200)
    def create_empty_dataset(self, name):
        return {'name': name}

    @moc_api_request('/datasets', 'GET')
    def get_datasets(self,
                     keyword='',
                     page=1,
                     page_size=30):
        query_params = [
            ('page', page),
            ('limit', page_size)
        ]
        if keyword:
            query_params.append(('keyword', keyword))
        return None, query_params

    @moc_api_request('/datasets/{id}/documents', 'GET')
    def get_documents(self,
                     dataset_id: str,
                     keyword='',
                     page=1,
                     page_size=10):
        query_params = [
            ('keyword', keyword),
            ('page', page),
            ('limit', page_size)
        ]
        return None, query_params, {'id': dataset_id}

    @moc_api_request('/datasets/{dataset_id}/documents/{doc_id}/segments', 'GET')
    def get_segments(self,
                     dataset_id: str,
                     doc_id: str,
                     keyword='',
                     page=1,
                     page_size=10):
        query_params = [
            ('keyword', keyword),
            ('enabled', 'all'),
            ('page', page),
            ('limit', page_size)
        ]
        return None, query_params, {'dataset_id': dataset_id, 'doc_id': doc_id}

    @moc_api_request('/datasets/{id}', 'DELETE')
    def delete_dataset(self, _id):
        return None, [], {'id': _id}
