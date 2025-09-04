import allure
from service.base import BaseController
from service.moi.process.workflow.api import WorkflowAPI
from service.moi.process.workflow.models import *
from service.error import APIError
from fixture.internal.instance import env
from service.utils import wait_and_filter

logger = logging.getLogger(__name__)


class WorkflowController(BaseController):
    _api_class = WorkflowAPI

    def __init__(self, _id=None, user=env.get_config('workspace_platform_user'), api_client=None):
        super().__init__(f"{_id}:{user if user else 'admin'}", api_client)

    @property
    def workspace_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Workspace-Id')

    @property
    def user_name(self) -> str:
        return self.api.api_client.default_headers.get('X-User-Name')

    @wait_and_filter()
    @allure.step('查看工作流列表')
    def list_workflows(self,
                       keyword='',
                       file_types: List[FileType] = None,
                       process_modes: List[ProcessMode] = None,
                       status: List[WorkflowStatus] = None,
                       priority: List[Priority] = None,
                       order_by: SortField = SortField.CreateTime,
                       is_desc: bool = True,
                       offset=0,
                       limit=20,
                       *args,
                       **kwargs):
        res = self.api.list(keyword, file_types, process_modes, status, priority, order_by, is_desc, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Workflow(**w) for w in res['data']['workflows']], res['data']['total']

    @allure.step('查看工作流详情')
    def get_workflow(self, workflow_id):
        res = self.api.get(workflow_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Workflow(**res['data'])

    @allure.step('查看工作流分支列表')
    def list_branches(self, workflow_id):
        res = self.api.list_branches(workflow_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Workflow(**w) for w in res['data']['workflows']], res['data']['total']

    @allure.step('查看工作流分支详情')
    def get_branch(self, branch_id):
        res = self.api.get_branch(branch_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Workflow(**res['data'])

    @allure.step('编辑工作流基础信息')
    def update_base_info(self,
                         base_info: WorkflowBasic,
                         workflow_id: str = None,
                         name: str = None,
                         source_volumes: Any = None,
                         target_volume: Any = None,
                         priority: Priority = None,
                         process_mode: ProcessMode = None,
                         process_scope: ProcessScope = None,
                         file_types: List[FileType] = None,
                         **files):
        # if source_volumes:
        #     kwargs['source_volumes'] = source_volumes
        # if target_volume:
        #     kwargs['target_volume'] = target_volume
        # if process_scope:
        #     kwargs['process_scope'] = process_scope
        # if 'id' in kwargs:
        #     kwargs.pop('id')
        # base_info = WorkflowBasic(
        #     name=name,
        #     # source_volumes=source_volumes,
        #     # target_volume=target_volume,
        #     priority=priority,
        #     process_mode=process_mode,
        #     # process_scope=process_scope,
        #     file_types=file_types,
        #     files=files,
        #     # create_target_volume_name='',
        #     **kwargs
        # )
        if name:
            base_info.name = name
        if source_volumes:
            base_info._source_volumes = source_volumes
        if target_volume:
            base_info._target_volume = target_volume
        if priority:
            base_info.priority = priority
        if process_mode:
            base_info.process_mode = process_mode
        if process_scope:
            base_info.process_scope = source_volumes
        if file_types:
            base_info.file_types = file_types
        if files:
            base_info.files = list(files)
        if isinstance(base_info, Workflow):
            base_info = base_info.get_basic_info()
        res = self.api.update_base_info(workflow_id if workflow_id else base_info.id, base_info)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('重新运行工作流')
    def rerun(self, workflow_id):
        res = self.api.rerun(workflow_id)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('停止工作流')
    def stop(self, workflow_id):
        res = self.api.stop(workflow_id)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('修改工作流分支')
    def update_branch(self,
                      branch_id,
                      workflow: ProcessFlow,
                      branch_name='主要'):
        res = self.api.update_branch(branch_id, workflow, branch_name)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('创建工作流分支')
    def create_branch(self,
                      # workflow_id,
                      base_info: WorkflowBasic,
                      workflow: ProcessFlow,
                      branch_name='test'):
        if isinstance(base_info, Workflow):
            base_info = base_info.get_basic_info()
        res = self.api.create_branch(base_info.id, base_info, workflow, branch_name)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('检查工作流名称是否可用')
    def check_workflow_name(self, name) -> bool:
        res = self.api.check_workflow_name(name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res.get('data').get('is_unique')

    @allure.step('创建工作流')
    def create_workflow(self,
                        name,
                        source_volumes: Any,
                        target_volume: Any,
                        priority: Priority,
                        process_mode: ProcessMode,
                        process_scope: ProcessScope,
                        file_types: List[FileType],
                        workflow: ProcessFlow,
                        branch_name='主要',
                        **files):
        base_info = WorkflowBasic(
            name=name,
            source_volumes=source_volumes,
            target_volume=target_volume,
            priority=priority,
            process_mode=process_mode,
            process_scope=process_scope,
            file_types=file_types,
            files=list(files)
        )
        res = self.api.create(base_info, workflow, branch_name)
        if 'detail' in res:
            return APIError(code=1, msg=res['detail'])
        else:
            assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
            return Workflow(**res['data'])

    @allure.step('删除工作流')
    def delete_workflow(self, workflow_id, delete_data: bool = False):
        res = self.api.delete(workflow_id, delete_data)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    @allure.step('删除工作流分支')
    def delete_branch(self, workflow_id, delete_data: bool = False):
        res = self.api.delete_branch(workflow_id, delete_data)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)
