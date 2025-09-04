import os.path
from service.base import BaseAPI
from service.api import moc_api_request
from service.moi.connect.export.models import *

logger = logging.getLogger(__name__)


class ExportAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/byoa/api/v1/export/task/list', 'POST')
    def task_list(self, page=1, page_size=10):
        return {"limit": page_size, "offset": page - 1}

    @moc_api_request('/byoa/api/v1/export/task/info', 'POST')
    def task_info(self, _id):
        return {"id": _id}

    @moc_api_request('/byoa/api/v1/export/task/files', 'POST')
    def task_files(self, _id, page=1, page_size=10):
        return {"task_id": _id, "limit": page_size, "offset": page - 1}

    @moc_api_request('/byoa/api/v1/export/task/create', 'POST')
    def export(self,
               task_name,
               creator,
               connector_id,
               connector_name,
               _type: ConnectorSourceType,
               config: ExportConfig,
               files: List[ExportFile],
               merge_title_to_text=True):
        payload = {
            "task_name": task_name,
            "creator": creator,
            "connector_id": connector_id,
            "connector_name": connector_name,
            "type": _type.value,
            "config": {
                "merge_title_to_text": merge_title_to_text,
                f"{getattr(config, '_type_name')}": config.to_dict()
            },
            "files": [{"file_id": f.id, "full_path": f.full_path, "is_raw": False} for f in files],
        }
        return payload

    @moc_api_request('/byoa/api/v1/export/task/delete', 'POST')
    def delete_task(self, _id):
        return {'id': _id}
