import allure
from service.base import BaseController
from service.moi.connect.export.api import ExportAPI
from service.moi.connect.export.models import *
from service.error import APIError
from fixture.internal.instance import env
from service.utils import wait_and_filter


logger = logging.getLogger(__name__)


class ExportController(BaseController):
    _api_class = ExportAPI

    def __init__(self, _id=None, user=env.get_config('workspace_platform_user'), api_client=None):
        super().__init__(f"{_id}:{user if user else 'admin'}", api_client)

    @property
    def workspace_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Workspace-Id')

    @property
    def user_name(self) -> str:
        return self.api.api_client.default_headers.get('X-User-Name')

    @wait_and_filter()
    @allure.step('查看导出任务列表')
    def get_task_list(self, page=1, page_size=10, *args, **kwargs):
        res = self.api.task_list(page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [ExportTask(**t) for t in res['data']['tasks']], res['data']['total']

    @allure.step('查看导出任务详情')
    def get_task_info(self, task_id):
        res = self.api.task_info(task_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return ExportTaskInfo(**res['data'])

    @allure.step('查看导出任务文件列表')
    def get_task_files(self, task_id, page=1, page_size=10):
        res = self.api.task_files(task_id, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [ExportedFile(**f) for f in res['data']['files']], res['data']['total']

    @allure.step('导出到Dify知识库')
    def export_to_dify(self,
                       task_name,
                       connector_id,
                       connector_name,
                       dataset_id,
                       dataset_name,
                       embedding_model,
                       files: List[ExportFile],
                       merge_title_to_text=True):
        res = self.api.export(
            task_name,
            self.user_name,
            connector_id,
            connector_name,
            ConnectorSourceType.Dify,
            DifyExportConfig(dataset_id=dataset_id, dataset_name=dataset_name, embedding_model=embedding_model),
            files,
            merge_title_to_text
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('导出到MO数据库')
    def export_to_mo(self,
                     task_name,
                     connector_id,
                     connector_name,
                     column,
                     database,
                     table,
                     new_table: bool,
                     files: List[ExportFile],
                     duplicated_strategy: MODuplicatedStrategy = MODuplicatedStrategy.Reserve,
                     merge_title_to_text=False):
        res = self.api.export(
            task_name,
            self.user_name,
            connector_id,
            connector_name,
            ConnectorSourceType.MO,
            MOExportConfig(column=column, database_name=database, table_name=table, new_table=new_table, duplicated_strategy=duplicated_strategy),
            files,
            merge_title_to_text
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('导出到OSS对象存储')
    def export_to_oss(self,
                      task_name,
                      connector_id,
                      connector_name,
                      files: List[ExportFile],
                      path,
                      need_compress: bool = True,
                      compress_method: S3CompressMethod = S3CompressMethod.GZIP,
                      merge_title_to_text=False):
        res = self.api.export(
            task_name,
            self.user_name,
            connector_id,
            connector_name,
            ConnectorSourceType.OSS,
            OSSExportConfig(path=path, need_compress=need_compress, compress_method=compress_method),
            files,
            merge_title_to_text
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('导出到标准S3对象存储')
    def export_to_s3(self,
                     task_name,
                     connector_id,
                     connector_name,
                     path,
                     files: List[ExportFile],
                     need_compress: bool = True,
                     compress_method: S3CompressMethod = S3CompressMethod.GZIP,
                     merge_title_to_text=False):
        res = self.api.export(
            task_name,
            self.user_name,
            connector_id,
            connector_name,
            ConnectorSourceType.S3,
            S3ExportConfig(path=path, need_compress=need_compress, compress_method=compress_method),
            files,
            merge_title_to_text
        )
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('删除导出任务')
    def delete_task(self, _id):
        res = self.api.delete_task(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
