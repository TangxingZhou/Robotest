import os
from service.models import *


class DifyDataSet(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.document_count: int = kwargs.get('document_count')
        self.embedding_model: str = kwargs.get('embedding_model')
        self.embedding_available: bool = kwargs.get('embedding_available')


class DifyDocument(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.created_at: int = kwargs.get('created_at')
        self.word_count: int = kwargs.get('word_count')
        self.display_status: str = kwargs.get('display_status')
        self.data_source_type: str = kwargs.get('data_source_type')
        self.indexing_status: str = kwargs.get('indexing_status')
        self.upload_file_detail = kwargs.get('data_source_detail_dict', {}).get('upload_file')
        self.upload_file_id: str = kwargs.get('data_source_info', {}).get('upload_file_id')

    def fields_are_correct(self, name):
        assert self.name == name, f"{self.name} != {name}"
        assert self.data_source_type == "upload_file"

    def is_running(self):
        assert self.display_status == '', f"{self.display_status} != ''"
        assert self.word_count == 0, f"{self.word_count} != 0"

    def is_completed(self):
        assert self.display_status == 'available', f"{self.display_status} != 'available'"
        assert self.word_count > 0, f"{self.word_count} <= 0"

    # def __lt__(self, other):
    #     if not isinstance(other, DifyDocument):
    #         return NotImplemented
    #     return self.name < other.name


class DifySegment(BaseModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.document_id: str = kwargs.get('document_id')
        self.content: str = kwargs.get('content')
        self.created_at: int = kwargs.get('created_at')
        self.completed_at: int = kwargs.get('completed_at')
        self.updated_at: int = kwargs.get('updated_at')
        self.enabled: bool = kwargs.get('enabled')
        self.status: str = kwargs.get('status')
        self.keywords = kwargs.get('keywords', [])
        self.word_count: int = kwargs.get('word_count')

    def fields_are_correct(self, content):
        # assert self.content == content, f"{self.content} != {content}"
        assert self.status == "completed", f"{self.status} != 'completed'"
