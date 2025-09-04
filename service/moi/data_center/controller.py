import allure
from service.base import BaseController
from service.moi.data_center.api import DataCenterAPI
from service.moi.data_center.models import *
from service.error import APIError
from fixture.internal.instance import env
from service.utils import wait_and_filter

logger = logging.getLogger(__name__)


class DataCenterController(BaseController):
    _api_class = DataCenterAPI

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

    @allure.step('创建数据卷')
    def create_volume(self, name, database_id):
        res = self.api.create_volume(name, database_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']['id']

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

    @allure.step('下载数据卷里的文件')
    def get_raw(self, volume_id, file_id):
        # import zipfile
        # zip_path = self.api.get_raw(volume_id, file_id)
        # with zipfile.ZipFile(zip_path, 'r') as zip_file:
        #     zip_file.extractall()
        return self.api.get_raw(volume_id, file_id)
