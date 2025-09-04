from typing import List, Tuple, Set, Any, Collection
from service.models import *
from service.moi.process.workflow.models import FileType, Priority, ProcessScope


class SortField(Enum):
    StartTime = 'start_time'
    EndTime = 'end_time'
    Duration = 'duration'


class JobStatus(Enum):
    Processing = 0
    Failed = 1
    Complete = 2
    Pending = 3
    Paused = 4
    Retry = 5


class FileStatus(Enum):
    Processing = 0
    Failed = 1
    Complete = 2
    Pending = 3
    Paused = 4
    Retry = 5


class Job(BaseModel):
    _ignore_attrs = ('process_scope',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.branch_name: str = kwargs.get('branch_name')
        self._source_volumes = (kwargs.get('source_volume_ids'), kwargs.get('source_volume_names'))
        self.source_volume_path: List = kwargs.get('source_volume_path')
        self._target_volume = (kwargs.get('target_volume_id'), kwargs.get('target_volume_name'))
        self.target_volume_path: List = kwargs.get('target_volume_path')
        self.priority = kwargs.get('priority')
        self.process_scope = kwargs.get('description').get('processScope')
        self.file_types = kwargs.get('file_types')
        self.processed_count: int = kwargs.get('processed_count')
        self.total_count: int = kwargs.get('total_count')
        self.duration: int = kwargs.get('duration')
        self.status: JobStatus = JobStatus(kwargs.get('status'))
        self.start_time: str = kwargs.get('start_time')
        self.end_time: str = kwargs.get('end_time')
        self.version: str = kwargs.get('version')
        self.workflow: dict = kwargs.get('workflow')
        self.workflow_branch_id: str = kwargs.get('workflow_branch_id')
        self.workflow_id: str = kwargs.get('workflow_id')
        self.workflow_meta_id: str = kwargs.get('workflow_meta_id')
        self.workflow_name: str = kwargs.get('workflow_name')

    @property
    def _source_volumes(self):
        return self.source_volume_ids, self.source_volume_names

    @_source_volumes.setter
    def _source_volumes(self, volumes: List[Any] | Tuple):
        if isinstance(volumes, tuple):
            self.source_volume_ids, self.source_volume_names = volumes
        else:
            self.source_volume_ids = [volume.id for volume in volumes]
            self.source_volume_names = [volume.name for volume in volumes]

    @property
    def _target_volume(self):
        return self.target_volume_id, self.target_volume_name

    @_target_volume.setter
    def _target_volume(self, volume: Any):
        if isinstance(volume, tuple):
            self.target_volume_id, self.target_volume_name = volume
        else:
            self.target_volume_id = volume.id
            self.target_volume_name = volume.name

    @property
    def priority(self) -> Priority:
        return self._priority

    @priority.setter
    def priority(self, priority):
        if priority:
            if isinstance(priority, Priority):
                self._priority = priority
            else:
                self._priority = Priority(priority)
        else:
            raise ValueError("priority is required")

    @property
    def process_scope(self) -> ProcessScope:
        return self._process_scope

    @process_scope.setter
    def process_scope(self, process_scope):
        if process_scope:
            if isinstance(process_scope, ProcessScope):
                self._process_scope = process_scope
            else:
                self._process_scope = ProcessScope(process_scope)
        else:
            raise ValueError("process_scope is required")

    @property
    def description(self) -> dict:
        return {'processScope': self._process_scope.value}

    @property
    def file_types(self) -> Set[FileType]:
        return self._file_types

    @file_types.setter
    def file_types(self, file_types: Collection[FileType | int]):
        self._file_types = set()
        for t in file_types:
            if isinstance(t, FileType):
                self._file_types.add(t)
            else:
                self._file_types.add(FileType(t))


class JobFiles(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.completed: int = kwargs.get('completed')
        self.failed: int = kwargs.get('failed')
        self.file_total: int = kwargs.get('file_total')
        self.pending: int = kwargs.get('pending')
        self.processing: int = kwargs.get('processing')
        self.stopped: int = kwargs.get('stopped')
        self.total: int = kwargs.get('total')
        self.files: List[JobFile] = [JobFile(**f) for f in kwargs.get('files', [])]


class JobFile(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id: str = kwargs.get('id')
        self.file_name: str = kwargs.get('file_name')
        self.file_type: FileType = FileType(kwargs.get('file_type'))
        self.file_status: FileStatus = FileStatus(kwargs.get('file_status'))
        self.start_time: str = kwargs.get('start_time')
        self.end_time: str = kwargs.get('end_time')
        self.error_message: str | None = kwargs.get('error_message')
