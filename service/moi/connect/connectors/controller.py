import allure
from service.base import BaseController
from service.moi.connect.connectors.api import ConnectorAPI
from service.moi.connect.connectors.models import *
from service.error import APIError
from fixture.internal.instance import env

logger = logging.getLogger(__name__)


class ConnectorController(BaseController):
    _api_class = ConnectorAPI

    def __init__(self, _id=None, user=env.get_config('workspace_platform_user'), api_client=None):
        super().__init__(f"{_id}:{user if user else 'admin'}", api_client)

    @property
    def workspace_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Workspace-Id')

    @property
    def user_name(self) -> str:
        return self.api.api_client.default_headers.get('X-User-Name')

    @allure.step('查看连接器列表')
    def get_connector_list(self,
                           keyword='',
                           source_type: List[ConnectorSourceType] = None,
                           usage_type: List[ConnectorUsageType] = None,
                           status: List[ConnectorStatus] = None,
                           order_by: ConnectorListOrderBy = '',
                           is_desc: bool = False,
                           page=1,
                           page_size=10):
        res = self.api.list(keyword, source_type, usage_type, status, order_by, is_desc, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Connector(**c) for c in res['data']['connectors']], res['data']['total']

    @allure.step('连接测试')
    def validate_connector(self,
                           name,
                           source_type: ConnectorSourceType = ConnectorSourceType.OSS,
                           **kwargs) -> bool:
        config = ConnectorConfig(source_type.name.lower(), **kwargs)
        res = self.api.validate(name, config, source_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']['valid']

    @allure.step('创建阿里云OSS连接器')
    def create_oss_connector(self,
                             name,
                             access_key_id,
                             access_key_secret,
                             bucket_name,
                             endpoint,
                             usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        config = OSSConnectorConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            bucket_name=bucket_name,
            endpoint=endpoint
        )
        res = self.api.create(name, config, ConnectorSourceType.OSS, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('创建标准S3连接器')
    def create_s3_connector(self,
                            name,
                            access_key_id,
                            access_key_secret,
                            bucket_name,
                            endpoint,
                            path_style: bool = True,
                            region: str = None,
                            usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        config = S3ConnectorConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            bucket_name=bucket_name,
            endpoint=endpoint,
            path_style=path_style,
            region=region
        )
        res = self.api.create(name, config, ConnectorSourceType.S3, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('创建Dify知识库连接器')
    def create_dify_connector(self,
                              name,
                              api_url,
                              api_key,
                              usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Export,)):
        config = DifyConnectorConfig(
            api_key=api_key,
            api_url=api_url
        )
        res = self.api.create(name, config, ConnectorSourceType.Dify, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('创建MO数据库连接器')
    def create_mo_connector(self,
                            name,
                            host,
                            port: int,
                            username,
                            password,
                            usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Export,)):
        config = MOConnectorConfig(
            host=host,
            port=port,
            username=username,
            password=password
        )
        res = self.api.create(name, config, ConnectorSourceType.MO, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('修改阿里云OSS连接器')
    def update_oss_connector(self,
                             _id,
                             name,
                             access_key_id,
                             access_key_secret,
                             bucket_name,
                             endpoint,
                             usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        config = OSSConnectorConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            bucket_name=bucket_name,
            endpoint=endpoint
        )
        res = self.api.update(_id, name, config, ConnectorSourceType.OSS, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('修改标准S3连接器')
    def update_s3_connector(self,
                            _id,
                            name,
                            access_key_id,
                            access_key_secret,
                            bucket_name,
                            endpoint,
                            path_style: bool = True,
                            region: str = None,
                            usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Import,)):
        config = S3ConnectorConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            bucket_name=bucket_name,
            endpoint=endpoint,
            path_style=path_style,
            region=region
        )
        res = self.api.update(_id, name, config, ConnectorSourceType.S3, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('修改Dify知识库连接器')
    def update_dify_connector(self,
                              _id,
                              name,
                              api_url,
                              api_key,
                              usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Export,)):
        config = DifyConnectorConfig(
            api_key=api_key,
            api_url=api_url
        )
        res = self.api.update(_id, name, config, ConnectorSourceType.Dify, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('修改MO数据库连接器')
    def update_mo_connector(self,
                            _id,
                            name,
                            host,
                            port: int,
                            username,
                            password,
                            usage_type: Tuple[ConnectorUsageType] = (ConnectorUsageType.Export,)):
        config = MOConnectorConfig(
            host=host,
            port=port,
            username=username,
            password=password
        )
        res = self.api.update(_id, name, config, ConnectorSourceType.MO, usage_type)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('校验MO表名是否存在')
    def check_mo_table_name(self, _id, database, table) -> bool:
        res = self.api.check_mo_table_name(_id, database, table)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']['exists']

    @allure.step('删除连接器')
    def delete_connector(self, _id):
        res = self.api.delete(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
