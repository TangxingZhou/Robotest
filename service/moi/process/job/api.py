from service.base import BaseAPI
from service.api import moc_api_request
from service.moi.process.job.models import *

logger = logging.getLogger(__name__)


class JobAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/byoa/api/v1/workflow_job', 'GET')
    def list(self,
             keyword='',
             file_types: List[FileType] = None,
             files_count_ge=1,
             order_by: SortField = SortField.StartTime,
             is_desc: bool = True,
             page_num=1,
             page_size=20,
             # source_file_id: str = None,
             # target_volume_id: str = None,
             # workflow_branch_id: str = None,
             # workflow_branch_name: str = None,
             **kwargs):
        query_params = [
            ('count_ge', files_count_ge),
            ('sort_field', order_by.value),
            ('sort_order', 'descend' if is_desc else 'ascend'),
            ('page_num', page_num),
            ('page_size', page_size)
        ]
        if keyword:
            query_params.append(('name_search', keyword))
        for k, v in kwargs.items():
            if v:
                query_params.append((k, v))
        if file_types is not None:
            for s in file_types:
                if s is not None:
                    query_params.append(('file_types', s.value))
        return None, query_params

    @moc_api_request('/byoa/api/v1/workflow_job/{id}', 'GET')
    def get(self, job_id):
        return None, [], {'id': job_id}

    @moc_api_request('/byoa/api/v1/workflow_job/{id}/files', 'GET')
    def get_files(self, job_id, status: List[FileStatus] = None , page_num=1, page_size=20):
        query_params = [
            ('job_id', job_id),
            ('page_num', page_num),
            ('page_size', page_size)
        ]
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status', s.value))
        return None, query_params, {'id': job_id}

    @moc_api_request('/byoa/api/v1/workflow_job/{id}/files', 'POST')
    def retry_files(self, job_id, files: List):
        return files, [], {'id': job_id}

    @moc_api_request('/byoa/api/v1/workflow_job/any/find_files', 'GET')
    def find_files(self,
                   page_num=1,
                   page_size=20,
                   **kwargs):
        query_params = [
            ('page_num', page_num),
            ('page_size', page_size)
        ]
        for k, v in kwargs.items():
            if v:
                query_params.append((k, v))
        return None, query_params
