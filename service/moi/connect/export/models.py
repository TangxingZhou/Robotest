from typing import List
from service.models import *
from service.utils import *
from service.moi.connect.connectors.models import ConnectorSourceType


class ExportTaskStatus(BaseEnum):
    Processing = 1
    Completed = 2
    Failed = 3


class ExportFileStatus(BaseEnum):
    Pending = 0
    Processing = 1
    Completed = 2


class MODuplicatedStrategy(BaseEnum):
    Overwrite = 1
    Skip = 2
    Reserve = 3


class MOExportField(BaseEnum):
    File_ID = 'file_id'
    File_Name = 'file_name'
    Block_ID = 'block_id'
    Block_NO = 'block_no'
    Block_Type = 'block_type'
    Block_Level = 'block_level'
    Content = 'content'
    Page_NO = 'page_no'
    Embedding = 'embedding'
    Image_Data = 'image_data'
    Created_At = 'created_at'
    Updated_At = 'updated_at'
    Meta = 'meta'


class MOExportColumn:
    column = {
        'combine_column': [],
        'export_column': []
    }

    def __init__(self, source_column: str = '', target_colume: str = '', merge_to_meta_column: bool = False, **kwargs):
        self.source_column = kwargs.get('_source_column', source_column)
        if not self.source_column:
            raise ValueError('source_column is required')
        self.target_colume = kwargs.get('_target_colume', target_colume)
        self.merge_to_meta_column = kwargs.get('_merge_to_meta_column', merge_to_meta_column)
        if self.target_colume == target_colume:
            if target_colume:
                self.column['export_column'].append({'source_column': source_column, 'mapping_column': target_colume})
            else:
                self.column['export_column'].append({'source_column': source_column, 'mapping_column': source_column})
        if merge_to_meta_column:
            self.column['combine_column'].append(source_column)


class S3CompressMethod(BaseEnum):
    GZIP = 'gzip'
    Origin = 'no'


class ExportConfig(metaclass=FactoryMeta):
    pass


class OSSExportConfig(ExportConfig):
    _type_name = 'oss_config'

    def __init__(self, **kwargs):
        self.need_compress: bool = kwargs.get('need_compress')
        self.path: str = kwargs.get('path')
        self.compress_method: S3CompressMethod = kwargs.get('compress_method') \
            if kwargs.get('compress_method') is None or isinstance(kwargs.get('compress_method'), S3CompressMethod) \
            else S3CompressMethod(kwargs.get('compress_method'))


class S3ExportConfig(ExportConfig):
    _type_name = 's3_config'

    def __init__(self, **kwargs):
        self.need_compress: bool = kwargs.get('need_compress')
        self.path: str = kwargs.get('path')
        self.compress_method: S3CompressMethod = kwargs.get('compress_method') \
            if kwargs.get('compress_method') is None or isinstance(kwargs.get('compress_method'), S3CompressMethod) \
            else S3CompressMethod(kwargs.get('compress_method'))


class DifyExportConfig(ExportConfig):
    _type_name = 'dify_config'

    def __init__(self, **kwargs):
        self.dataset_id = kwargs.get('dataset_id')
        self.dataset_name = kwargs.get('dataset_name')
        self.embedding_model = kwargs.get('embedding_model')


class MOExportConfig(ExportConfig):
    _type_name = 'mo_config'

    def __init__(self, **kwargs):
        self.column = kwargs.get('column', {})
        self.database_name = kwargs.get('database_name')
        self.table_name = kwargs.get('table_name')
        self.new_table: bool = kwargs.get('new_table')
        self.duplicated_strategy: MODuplicatedStrategy = kwargs.get('duplicated_strategy') \
            if kwargs.get('duplicated_strategy') is None or isinstance(kwargs.get('duplicated_strategy'), MODuplicatedStrategy) \
            else MODuplicatedStrategy(kwargs.get('duplicated_strategy'))

    def export_columns(self):
        return [MOExportColumn(
            _source_column=c.get('source_column'),
            _target_colume=c.get('mapping_column'),
            _merge_to_meta_column=c['source_column'] in self.column.get('combine_column', [])
        ) for c in self.column.get('export_column', [])]


class HuggingFaceExportConfig(ExportConfig):
    _type_name = 'hugging_face_config'

    def __init__(self, **kwargs):
        self.dataset_id = kwargs.get('api_key')
        self.dataset_name = kwargs.get('api_key')
        self.embedding_model = kwargs.get('api_key')


class LlamaFactoryExportConfig(ExportConfig):
    _type_name = 'llama_factory_config'

    def __init__(self, **kwargs):
        self.dataset_id = kwargs.get('api_key')
        self.dataset_name = kwargs.get('api_key')
        self.embedding_model = kwargs.get('api_key')


class ExportFile:

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.directory = kwargs.get('directory', '默认')
        self.warehouse = kwargs.get('warehouse', '原始数据卷')
        self.target_volume_name = kwargs.get('target_volume_name')
        self.target_volume_branch = kwargs.get('target_volume_branch')

    def __repr__(self):
        return '/'.join(self.full_path)

    @property
    def full_path(self):
        return [self.directory, self.warehouse, self.target_volume_name, self.target_volume_branch, self.name]


class ExportedFile:

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.create_time = kwargs.get('create_time')
        self.details = kwargs.get('details')
        self.status: ExportFileStatus = ExportFileStatus(kwargs.get('status'))
        self.full_path = kwargs.get('full_path')

    def fields_are_correct(self, full_path):
        assert self.id is not None, f"{self.id}"
        assert self.full_path == full_path, f"{self.full_path} != {full_path}"

    def is_pending(self):
        assert self.status == ExportFileStatus.Pending, f"{self.status.value} != {ExportFileStatus.Pending.value}"
        assert self.create_time is not None, self.create_time

    def is_running(self):
        assert self.status == ExportFileStatus.Processing, f"{self.status.value} != {ExportFileStatus.Processing.value}"
        assert self.start_time is not None, self.create_time
        assert self.end_time is None, self.end_time

    def is_completed(self):
        assert self.status == ExportFileStatus.Completed, f"{self.status.value} != {ExportFileStatus.Completed.value}"
        assert self.end_time is not None, self.end_time


class ExportTask(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.connector_name: str = kwargs.get('connector_name')
        self.create_time: str = kwargs.get('create_time')
        self.end_time: str = kwargs.get('end_time')
        self.export_source = kwargs.get('export_source')
        self.status: ExportTaskStatus = ExportTaskStatus(kwargs.get('status'))
        self.type: ConnectorSourceType = ConnectorSourceType(kwargs.get('type'))

    def fields_are_correct(self,
                           name,
                           export_source,
                           connector_name):
        assert self.name == name, f"{self.name} != {name}"
        assert objects_should_be_equal([s[0] for s in self.export_source], [s[0] for s in export_source])
        assert objects_should_be_equal(self.export_source, export_source), f"{self.export_source} != {export_source}"
        assert self.connector_name == connector_name, f"{self.connector_name} != {connector_name}"

    def is_running(self):
        assert self.status == ExportTaskStatus.Processing, f"{self.status.value} != {ExportTaskStatus.Processing.value}"
        assert self.create_time is not None, self.create_time
        assert self.end_time is None, self.end_time

    def is_completed(self):
        assert self.status == ExportTaskStatus.Completed, f"{self.status.value} != {ExportTaskStatus.Completed.value}"
        assert self.end_time is not None, self.end_time

    def is_to_dify(self):
        assert self.type == ConnectorSourceType.Dify, f"{self.type.value} != {ConnectorSourceType.Dify.value}"

    def is_to_mo(self):
        assert self.type == ConnectorSourceType.MO, f"{self.type.value} != {ConnectorSourceType.MO.value}"

    def is_to_oss(self):
        assert self.type == ConnectorSourceType.OSS, f"{self.type.value} != {ConnectorSourceType.OSS.value}"

    def is_to_s3(self):
        assert self.type == ConnectorSourceType.S3, f"{self.type.value} != {ConnectorSourceType.S3.value}"


class ExportTaskInfo(ExportTask):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'oss_config' in kwargs.get('config', {}):
            self.config = ExportConfig('oss_config', **kwargs.get('config').get('oss_config'))
        elif 's3_config' in kwargs.get('config', {}):
            self.config = ExportConfig('s3_config', **kwargs.get('config').get('s3_config'))
        elif 'dify_config' in kwargs.get('config', {}):
            self.config = ExportConfig('dify_config', **kwargs.get('config').get('dify_config'))
        elif 'mo_config' in kwargs.get('config', {}):
            self.config = ExportConfig('mo_config', **kwargs.get('config').get('mo_config'))
        elif 'hugging_face_config' in kwargs.get('config', {}):
            self.config = ExportConfig('hugging_face_config', **kwargs.get('config').get('hugging_face_config'))
        elif 'llama_factory_config' in kwargs.get('config', {}):
            self.config = ExportConfig('llama_factory_config', **kwargs.get('config').get('llama_factory_config'))
        else:
            self.config = None
        self.merge_title_to_text: bool = kwargs.get('config', {}).get('merge_title_to_text')
        self.creator: str = kwargs.get('creator')

    def fields_are_correct(self,
                           _id,
                           name,
                           connector_name,
                           creator=None,
                           merge_title_to_text: bool = True):
        assert self.id == _id, f"{self.id} != {_id}"
        assert self.name == name, f"{self.name} != {name}"
        assert self.creator == creator, f"{self.creator} != {creator}"
        assert self.connector_name == connector_name, f"{self.connector_name} != {connector_name}"
        assert self.merge_title_to_text == merge_title_to_text, f"{self.merge_title_to_text} != {merge_title_to_text}"

    def config_is_correct(self, config: ExportConfig):
        assert self.config == config, f"{self.config} != {config}"
