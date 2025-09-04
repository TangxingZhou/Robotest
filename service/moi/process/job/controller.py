import allure
from service.base import BaseController
from service.moi.process.job.api import JobAPI
from service.moi.process.job.models import *
from service.error import APIError
from fixture.internal.instance import env
from service.utils import wait_and_filter

logger = logging.getLogger(__name__)


class JobController(BaseController):
    _api_class = JobAPI

    def __init__(self, _id=None, user=env.get_config('workspace_platform_user'), api_client=None):
        super().__init__(f"{_id}:{user if user else 'admin'}", api_client)

    @property
    def workspace_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Workspace-Id')

    @property
    def user_name(self) -> str:
        return self.api.api_client.default_headers.get('X-User-Name')

    @wait_and_filter()
    @allure.step('查看作业列表')
    def list_jobs(self,
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
                  *args,
                  **kwargs):
        res = self.api.list(
            keyword,
            file_types,
            files_count_ge,
            order_by,
            is_desc,
            page_num,
            page_size
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Job(**w) for w in res['data']['jobs']], res['data']['total']

    @allure.step('查看作业详情')
    def get_job(self, job_id):
        res = self.api.get(job_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Job(**res['data'])

    @allure.step('查看作业详情里的文件列表')
    def get_files(self, job_id, status: List[FileStatus] = None , page_num=1, page_size=20):
        res = self.api.get_files(job_id, status, page_num, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return JobFiles(**res['data'])

    @allure.step('重试处理失败的文件')
    def retry_files(self, job_id, files: List):
        res = self.api.get_files(job_id, files)
        if not APIError(**res).is_ok():
            logger.error(f"response code: {res.get('code')}, message: {res.get('msg')}")
            return APIError(**res)

    def find_files(self,
                   workflow_id: str = None,
                   source_file_id: str = None,
                   target_volume_id: str = None,
                   workflow_branch_id: str = None,
                   workflow_branch_name: str = None,
                   page_num=1,
                   page_size=20):
        res = self.api.find_files(
            page_num,
            page_size,
            workflow_id=workflow_id,
            source_file_id=source_file_id,
            target_volume_id=target_volume_id,
            workflow_branch_id=workflow_branch_id,
            workflow_branch_name=workflow_branch_name,
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return JobFiles(**res['data'])
