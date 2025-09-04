import oss2
import boto3
from botocore.config import Config
from typing import List, Optional, Tuple
from service.models import *
from service.utils import FactoryMeta
from service.mo.client import MOClient
from service.s3 import OSSBucket, S3Bucket, MinioClient


class ConnectorOperation(BaseEnum):
    Create = 'create'
    Update = 'update'
    Validate = 'validate'
    Delete = 'delete'

class ConnectorSourceType(BaseEnum):
    Local = 1
    MO = 3
    OSS = 4
    S3 = 5
    Dify = 6
    HDFS = 7


class ConnectorUsageType(BaseEnum):
    Import = 1
    Export = 2


class ConnectorStatus(BaseEnum):
    Active = 'active'
    Failed = 'failed'


class ConnectorListOrderBy(BaseEnum):
    Name = 'name'
    CreatedAt = 'created_at'
    UpdatedAt = 'updated_at'


class ConnectorConfig(metaclass=FactoryMeta):
    pass


class OSSConnectorConfig(ConnectorConfig):
    _type_name = 'oss'

    def __init__(self, **kwargs):
        self.access_key_id: str = kwargs.get('access_key_id')
        self.access_key_secret: str = kwargs.get('access_key_secret')
        self.bucket_name: str = kwargs.get('bucket_name')
        self.endpoint: str = kwargs.get('endpoint')

    @property
    def _client(self) -> OSSBucket:
        bucket_paths = self.bucket_name.partition('/')
        return OSSBucket(
            self.endpoint,
            self.access_key_id,
            self.access_key_secret,
            bucket_paths[0],
            bucket_paths[2]
        )


class S3ConnectorConfig(ConnectorConfig):
    _type_name = 's3'

    def __init__(self, **kwargs):
        self.access_key_id: str = kwargs.get('access_key_id')
        self.access_key_secret: str = kwargs.get('access_key_secret')
        self.bucket_name: str = kwargs.get('bucket_name')
        self.endpoint: str = kwargs.get('endpoint')
        self.path_style: bool = kwargs.get('path_style')
        if kwargs.get('region', None):
            self.region = kwargs.get('region')

    @property
    def _client(self) -> MinioClient | S3Bucket:
        bucket_paths = self.bucket_name.partition('/')
        # return S3Bucket(
        #     self.endpoint,
        #     self.access_key_id,
        #     self.access_key_secret,
        #     bucket_paths[0],
        #     bucket_paths[2],
        #     getattr(self, 'region', None),
        #     self.path_style
        # )
        return MinioClient(
            self.endpoint,
            self.access_key_id,
            self.access_key_secret,
            bucket_paths[0],
            bucket_paths[2],
            getattr(self, 'region', None)
        )


class DifyConnectorConfig(ConnectorConfig):
    _type_name = 'dify'

    def __init__(self, **kwargs):
        self.api_key = kwargs.get('api_key')
        self.api_url = kwargs.get('api_url')


class MOConnectorConfig(ConnectorConfig):
    _type_name = 'mo'

    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port: int = kwargs.get('port', 6001)
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

    @property
    def _mo_client(self):
        return MOClient(host=self.host, port=self.port, user=self.username, password=self.password)


class Connector(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'oss' in kwargs.get('config', {}):
            self.config = ConnectorConfig('oss', **kwargs.get('config').get('oss'))
        elif 's3' in kwargs.get('config', {}):
            self.config = ConnectorConfig('s3', **kwargs.get('config').get('s3'))
        elif 'dify' in kwargs.get('config', {}):
            self.config = ConnectorConfig('dify', **kwargs.get('config').get('dify'))
        elif 'mo' in kwargs.get('config', {}):
            self.config = ConnectorConfig('mo', **kwargs.get('config').get('mo'))
        else:
            self.config = None
        self.id: int = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.source_type: ConnectorSourceType = ConnectorSourceType(kwargs.get('source_type'))
        self.usage_type: List[ConnectorUsageType] = [ConnectorUsageType(t) for t in kwargs.get('usage_type')]
        self.status: ConnectorStatus = ConnectorStatus(kwargs.get('status'))
        self.username: str = kwargs.get('username')
        self.created_at = kwargs.get('created_at')
        self.updated_at: int = kwargs.get('updated_at')
        self.related_task_ids: List[int] = kwargs.get('related_task_ids')

    def fields_are_correct(self,
                           name,
                           usage_type: List[ConnectorUsageType],
                           source_type: ConnectorSourceType,
                           username):
        assert self.name == name, f"{self.name} != {name}"
        assert sorted(self.usage_type, key=lambda x: x.value) == sorted(usage_type, key=lambda x: x.value), \
            f"{self.usage_type} != {usage_type}"
        assert self.source_type == source_type, f"{self.source_type} != {source_type}"
        assert self.username == username, f"{self.username} != {username}"

    def is_connected(self):
        assert self.status == ConnectorStatus.Active, f"{self.status.value} != {ConnectorStatus.Active.value}"

    def is_disconnected(self):
        assert self.status == ConnectorStatus.Failed, f"{self.status.value} != {ConnectorStatus.Failed.value}"

    def is_created(self):
        assert self.created_at == self.updated_at, f"{self.created_at} != {self.updated_at}"

    def is_updated(self):
        assert self.created_at != self.updated_at, f"{self.created_at} v.s {self.updated_at}"
