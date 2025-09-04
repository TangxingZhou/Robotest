from service.base import BaseAPI
from service.api import moc_api_request
from service.moi.process.workflow.models import *

logger = logging.getLogger(__name__)


class WorkflowAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/byoa/api/v1/workflow_meta', 'GET')
    def list(self,
             keyword='',
             file_types: List[FileType] = None,
             process_modes: List[ProcessMode] = None,
             status: List[WorkflowStatus] = None,
             priority: List[Priority] = None,
             order_by: SortField = SortField.CreateTime,
             is_desc: bool = True,
             offset=0,
             limit=20):
        query_params = [
            ('sort_field', order_by.value),
            ('sort_order', 'descend' if is_desc else 'ascend'),
            ('offset', offset),
            ('limit', limit)
        ]
        if keyword:
            query_params.append(('name_search', keyword))
        if file_types is not None:
            for s in file_types:
                if s is not None:
                    query_params.append(('file_types', s.value))
        if process_modes is not None:
            for s in process_modes:
                if s is not None:
                    query_params.append(('process_modes', s.interval + s.offset))
        if status is not None:
            for s in status:
                if s is not None:
                    query_params.append(('status', s.value))
        if priority is not None:
            for s in priority:
                if s is not None:
                    query_params.append(('priority', s.value))
        return None, query_params

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}', 'GET')
    def get(self, workflow_id):
        return None, [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}/branch', 'GET')
    def list_branches(self, workflow_id):
        return None, [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/branch/{id}', 'GET')
    def get_branch(self, branch_id):
        return None, [], {"id": branch_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}/base_info', 'PUT')
    def update_base_info(self, workflow_id, base_info: WorkflowBasic):
        return base_info.to_dict(), [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}/rerun', 'PUT')
    def rerun(self, workflow_id):
        return {}, [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}/stop', 'PUT')
    def stop(self, workflow_id):
        return {}, [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/branch/{id}', 'PUT')
    def update_branch(self, branch_id, workflow: ProcessFlow, branch_name='主要'):
        payload = {
            "branch_name": branch_name,
            "workflow": workflow.to_dict()
        }
        return payload, [], {"id": branch_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}/branch', 'POST')
    def create_branch(self, workflow_id, base_info: WorkflowBasic, workflow: ProcessFlow, branch_name='test'):
        payload = base_info.to_dict()
        payload.update({
            "branch_name": branch_name,
            "workflow": workflow.to_dict()
        })
        return payload, [], {"id": workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/name/check', 'GET')
    def check_workflow_name(self, name):
        query_params = [
            ('name', name)
        ]
        return None, query_params

    @moc_api_request('/byoa/api/v1/workflow_meta', 'POST')
    def create(self, base_info: WorkflowBasic, workflow: ProcessFlow, branch_name='主要'):
        payload = base_info.to_dict()
        payload.update({
            "branch_name": branch_name,
            "workflow": workflow.to_dict()
        })
        return payload

    @moc_api_request('/byoa/api/v1/workflow_meta/{id}', 'DELETE')
    def delete(self, workflow_id, delete_data: bool = False):
        query_params = [
            ('delete_data', delete_data)
        ]
        return None, query_params, {'id': workflow_id}

    @moc_api_request('/byoa/api/v1/workflow_meta/branch/{id}', 'DELETE')
    def delete_branch(self, branch_id, delete_data: bool = False):
        query_params = [
            ('delete_data', delete_data)
        ]
        return None, query_params, {'id': branch_id}
