from service.base import BaseAPI
from service.api import moc_api_request
from service.moi.data_center.models import *

logger = logging.getLogger(__name__)


class DataCenterAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/catalog/tree', 'POST')
    def get_tree(self):
        return {}

    @moc_api_request('/catalog/create', 'POST')
    def create_directory(self, name):
        return {'name': name}

    @moc_api_request('/catalog/list', 'POST')
    def get_directories(self):
        return {}

    @moc_api_request('/catalog/database/create', 'POST')
    def create_database(self, name, catalog_id):
        return {'name': name, 'catalog_id': catalog_id}

    @moc_api_request('/catalog/database/list', 'POST')
    def get_databases(self, directory_id):
        return {'id': directory_id}

    @moc_api_request('/catalog/volume/create', 'POST')
    def create_volume(self, name, database_id):
        return {'name': name, 'database_id': database_id}

    @moc_api_request('/catalog/database/children', 'POST')
    def get_volumes(self, database_id):
        return {'id': database_id}

    @moc_api_request('/catalog/file/list', 'POST')
    def get_files(self, job_id):
        return {'id': job_id}

    @moc_api_request('/byoa/api/v1/explore/volumes/{volume_id}/files/{file_id}/blocks', 'POST')
    def get_blocks(self, job_id, volume_id, file_id):
        return {'id': job_id}, [], {'volume_id': volume_id, 'file_id': file_id}

    @moc_api_request('/byoa/api/v1/explore/volumes/{volume_id}/files/{file_id}/jobs', 'GET')
    def get_jobs(self, volume_id, file_id):
        return None, [], {'volume_id': volume_id, 'file_id': file_id}

    @moc_api_request('/byoa/api/v1/explore/volumes/{volume_id}/files/{file_id}', 'POST')
    def get_file(self, volume_id, file_id):
        return None, [], {'volume_id': volume_id, 'file_id': file_id}

    @moc_api_request('/catalog/file/preview_stream', 'POST')
    def preview_stream(self, volume_id, file_id):
        return {'volume_id': volume_id, 'file_id': file_id}

    @moc_api_request('/byoa/api/v1/explore/volumes/{}/files/{}/parse_result', 'GET')
    def get_layout(self, volume_id, file_id):
        return None, [('file_type', 'layout')], {'volume_id': volume_id, 'file_id': file_id}

    @moc_api_request('/catalog/file/delete', 'POST')
    def delete_file(self, file_id):
        return {'id': file_id}

    @moc_api_request('/byoa/api/v1/explore/volumes/{volume_id}/files/{file_id}/raws', 'GET')
    def get_raw(self, volume_id, file_id):
        return None, [], {'volume_id': volume_id, 'file_id': file_id}
