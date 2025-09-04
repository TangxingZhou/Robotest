from __future__ import annotations
import json
from typing import Tuple, Set, Any, Collection
from service.moi.process.components import *


class SortField(Enum):
    CreateTime = 'created_at'
    UpdateTime = 'updated_at'


class WorkflowStatus(Enum):
    Running = 1
    Complete = 2
    Stopped = 3
    Paused = 4

class ImageProcessTypes(Enum):
    Caption = 'caption'
    OCR = 'ocr'


class ImageOCRModel(Enum):
    Default = 'ucaslcl/GOT-OCR2_0'
    Default_Tokenizer = 'stepfun-ai/GOT-OCR2_0'


class ImageCaptionLanguage(Enum):
    EN = 'en'
    ZH = 'zh'


class SplitMode(Enum):
    Single = 'single'
    Recursive = 'recursive'


class DataEnhancementFormat(Enum):
    Alpaca = 'Alpaca'
    ShareGPT = 'sharegpt'
    OpenAI = 'openai'
    CustomFormat = 'customize'


class ExtractionTemplate(Enum):
    Custom = 'custom'
    FinancialReport = 'financial_report'
    Invoice = 'invoice'
    Resume = 'resume'


class DocumentType(Enum):
    Text = 1
    PDF = 2
    PPT = 4
    DOC = 5
    Markdown = 6
    DOCX = 11
    PPTX = 12


class ImageType(Enum):
    PNG = 20
    JPG = 21
    JPEG = 22
    BMP = 23
    IMAGE = 3


class AudioType(Enum):
    WAV = 13
    MP3 = 14
    AAC = 15
    FLAC = 16


class VideoType(Enum):
    MP4 = 17
    MOV = 18
    MKV = 19


class FileType(Enum):
    Unknown = 0
    Text = 1
    PDF = 2
    PPT = 4
    DOC = 5
    Markdown = 6
    DOCX = 11
    PPTX = 12
    PNG = 20
    JPG = 21
    JPEG = 22
    BMP = 23
    IMAGE = 3
    WAV = 13
    MP3 = 14
    AAC = 15
    FLAC = 16
    MP4 = 17
    MOV = 18
    MKV = 19


class Priority(Enum):
    High = 500
    Medium = 300
    Low = 100


class ProcessScope(Enum):
    ByFileType = 'byFileType'
    ByFile = 'byFile'


class ProcessMode(BaseModel):
    def __init__(self, interval=0, offset=0):
        super().__init__()
        self.interval = interval
        self.offset = offset
    def once(self):
        self.interval = 0
        self.offset = 0
        return self
        # return {'process_mode': {'interval': 0, 'offset': 0}}

    def periodic(self, interval=5, offset_hours=0, offset_mins=0):
        self.interval = interval
        self.offset = 60 * offset_hours + offset_mins
        return self
        # return {'interval': interval, 'offset': 60 * offset_hours + offset_mins}

    def trigger_by_import(self):
        self.interval = -1
        self.offset = 0
        return self
        # return {'interval': -1, 'offset': 0}

    # def __repr__(self):
    #     return f"{'{'}'process_mode': {'{'}'interval': {self.interval}, 'offset': {self.offset}{'}'}{'}'}"


class WorkflowBasic(BaseModel):
    _ignore_attrs = ('process_scope',)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'id' in kwargs:
            self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self._source_volumes = kwargs.get(
            'source_volumes',
            (json.loads(kwargs.get('source_volume_ids')) if isinstance(kwargs.get('source_volume_ids'), str) else kwargs.get('source_volume_ids'),
             json.loads(kwargs.get('source_volume_names')) if isinstance(kwargs.get('source_volume_names'), str) else kwargs.get('source_volume_names'))
        )
        self._target_volume = kwargs.get('target_volume', (kwargs.get('target_volume_id'), kwargs.get('target_volume_name')))
        self.priority = kwargs.get('priority')
        if 'flow_interval' in kwargs or 'flow_offset' in kwargs:
            self.process_mode = {'interval': kwargs.get('flow_interval'), 'offset': kwargs.get('flow_offset')}
        else:
            self.process_mode = kwargs.get('process_mode')
        self.process_scope = kwargs.get(
            'process_scope',
            json.loads(kwargs.get('content')).get('processScope') if isinstance(kwargs.get('content'), str) else kwargs.get('content', {}).get('processScope'))
        # self.content = kwargs.get('process_scope', kwargs.get('content'))
        self.file_types = json.loads(kwargs.get('file_types')) if isinstance(kwargs.get('file_types'), str) else kwargs.get('file_types')
        self.files = json.loads(kwargs.get('files')) if isinstance(kwargs.get('files'), str) else kwargs.get('files', [])
        self.create_target_volume_name = kwargs.get('create_target_volume_name', '')
        if kwargs.get('group_id'):
            self.group_id = kwargs.get('group_id')
        if kwargs.get('user_id'):
            self.group_id = kwargs.get('user_id')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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
    def process_mode(self) -> ProcessMode:
        return self._process_mode

    @process_mode.setter
    def process_mode(self, process_mode):
        if process_mode:
            if isinstance(process_mode, ProcessMode):
                self._process_mode = process_mode
            elif isinstance(process_mode, dict):
                self._process_mode = ProcessMode(**process_mode)
            else:
                raise ValueError(f"process_mode {process_mode} is invalid, should be a ProcessMode instance or a dict")
        else:
            raise ValueError("process_mode is required")

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
    def content(self) -> dict:
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

    @property
    def files(self):
        return getattr(self, '_files', [])

    @files.setter
    def files(self, files: List[Any]):
        if all(isinstance(f, dict) for f in files):
            self._files = files
        else:
            self._files = [{'id': f.id, 'file_name': f.name} for f in files]
            self.file_types = [FileType(f.file_ext.upper()) for f in files]
            self.process_scope = ProcessScope.ByFile


class WorkflowBranch(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.branch_id = kwargs.get('branch_id')
        self.branch_name = kwargs.get('branch_name')
        self.branch_status = kwargs.get('branch_status')
        self.branch_volume_id = kwargs.get('branch_volume_id')
        self.branch_total = kwargs.get('branch_total')
        if kwargs.get('branches'):
            self.branches = [WorkflowBranch(**b) for b in kwargs.get('branches')]
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.creator = kwargs.get('creator')
        self.modifier = kwargs.get('modifier')
        if kwargs.get('status'):
            self.status = WorkflowStatus(kwargs.get('status'))
        self.version = kwargs.get('version')
        if kwargs.get('workflow'):
            self.workflow = ProcessFlow(**kwargs.get('workflow'))

    @property
    def workflow(self) -> ProcessFlow:
        return getattr(self, '_workflow', None)

    @workflow.setter
    def workflow(self, workflow: ProcessFlow):
        self._workflow = workflow


class Workflow(WorkflowBasic, WorkflowBranch):
    def __init__(self, **kwargs):
        WorkflowBasic.__init__(self, **kwargs)
        WorkflowBranch.__init__(self, **kwargs)

    def get_basic_info(self) -> WorkflowBasic:
        return WorkflowBasic(**self.to_dict())


class WorkflowNode(metaclass=FactoryMeta):
    _ignore_attrs = ('root', 'parents', 'children', 'components')
    def __init__(self):
        # self.type = self.__class__.__name__
        # self.root: ProcessFlow = None
        self.parents: List[WorkflowNode ] | None = []
        self.children: List[WorkflowNode] | None = []
        self.components: List[NodeComponent] = []

    def blank(self):
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)) and attr not in self._ignore_attrs:
                setattr(self, attr, None)
        return self

    # def update(self, **kwargs):
    #     for k, v in kwargs.items():
    #         if hasattr(self, k):
    #             if v is not None:
    #                 setattr(self, k, v)
    #         else:
    #             raise AttributeError(f"Node {self.__class__.__name__} does not have attribute {k}")
    #         # else:
    #         #     logger.warning(f"Node {self.__class__.__name__} does not have attribute {k}")

    def retrieve_from_components(self, components: List[NodeComponent]):
        # self.components = [component for component in self.components if component.name in [c.name for c in components]]
        for i, component in enumerate(self.components):
            for c in components:
                if component.name == c.name:
                    self.components[i] = c
                    if c.root is None:
                        c.root = component.root
                    break
        return self

    def add_child(self, node: WorkflowNode):
        if self.children is None:
            raise Exception(f"Node {self.__class__.__name__} cannot be parent node")
        if node.parents is None:
            raise Exception(f"Node {node.__class__.__name__} cannot be child node")
        if node.__class__.__name__ in [n.__class__.__name__ for n in self.root.nodes]:
            raise Exception(f"Node {node.__class__.__name__} already exists in workflow")
        # node.root = self.root
        # self.root.nodes.append(node)
        # node.init()
        self.root.nodes.append(node)
        if node.__class__.__name__ in [c.__class__.__name__ for c in self.children]:
            logger.warning(f"Node {node.__class__.__name__} is already child of node {self.__class__.__name__}")
        else:
            self.children.append(node)
        if self.__class__.__name__ in [c.__class__.__name__ for c in node.parents]:
            logger.warning(f"Node {self.__class__.__name__} is already parent of node {node.__class__.__name__}")
        else:
            node.parents.append(self)
        return node

    def insert_child(self, child: WorkflowNode):
        pass

    def remove_child(self, child: WorkflowNode, abandon_children: bool = False):
        pass

    def replace_child(self, old_child: WorkflowNode, new_child: WorkflowNode):
        pass

    @property
    def root(self) -> ProcessFlow | None:
        if self.parents:
            for parent in self.parents:
                return parent.root
        else:
            if getattr(self, '_workflow', None) is None:
                raise Exception(f"Node {self.__class__.__name__} has no root workflow")
            else:
                return getattr(self, '_workflow')

    @property
    def components(self) -> List[NodeComponent]:
        return self._components

    @components.setter
    def components(self, components: List[NodeComponent]):
        self._components = components

    def get_nodes(self) -> List[WorkflowNode]:
        nodes = [self]
        if self.children:
            for child in self.children:
                nodes.extend(child.get_nodes())
        return nodes

    def get_child_nodes(self) -> List[WorkflowNode]:
        nodes = []
        if self.children:
            nodes.extend(self.children)
            for child in self.children:
                nodes.extend(child.get_child_nodes())
        return nodes

    def get_components(self) -> List[NodeComponent]:
        components = []
        for component in self.components:
            if not component.parents:
                for c in component.get_components():
                    if c.name not in [component.name for component in components]:
                        components.append(c)
        return components

    def get_connections(self) -> List[NodeConnection]:
        connections = []
        for component in self.components:
            if not component.parents:
                for c in component.get_connections():
                    if c not in connections:
                        connections.append(c)
        return connections

    def has_component(self, name) -> bool:
        return any([component.name.replace('-', '') == name for component in self.components])

    # def get_component(self, name) -> Tuple[int, NodeComponent] | None:
    #     for index, component in enumerate(self.components):
    #         if component.name.replace('-', '') == name:
    #             return index, component

    def get_component(self, name) -> NodeComponent | None:
        for component in self.components:
            if component.name.replace('-', '') == name:
                return component
        raise Exception(f"Component {name} is not found in node of {self.__class__.__name__}")

    def remove_component(self, component: NodeComponent):
        if component.name in [c.name for c in self.components]:
            self.components.remove(component)
        else:
            raise Exception(f"Component {component.name} is not found in node of {self.__class__.__name__}")

    def init_connections(self, connections: List = None):
        for component in self.components:
            if component.name in (DocumentJoiner.__name__,):
                component.children = []
            else:
                component.parents = []
                component.children = []
        if connections is None:
            connections = []
        for connection in connections:
            parent = self.get_component(connection[0])
            child = self.get_component(connection[1])
            if child.name in [c.name for c in parent.children]:
                logger.warning(f"Component '{child.name}' is already child of component '{parent.name}'")
            else:
                parent.children.append(child)
            if parent.name in [c.name for c in child.parents]:
                logger.warning(f"Component '{parent.name}' is already parent of component '{child.name}'")
            else:
                child.parents.append(parent)


class StartNode(WorkflowNode):
    # _type_name = 'StartNode'
    def __init__(self):
        super().__init__()
        self.parents = None
        FileRouterComponent(root=self)


class EndNode(WorkflowNode):
    def __init__(self):
        super().__init__()
        self.children = None


class DocumentParserNode(WorkflowNode):
    def __init__(self,
                 name: str = '文档解析节点',
                 description: str = '',
                 caption_enabled: bool = True,
                 caption_language: ImageCaptionLanguage = ImageCaptionLanguage.ZH,
                 ocr_enabled: bool = True,
                 ocr_model: ImageOCRModel = ImageOCRModel.Default,
                 ocr_tokenizer: ImageOCRModel = ImageOCRModel.Default_Tokenizer):
        super().__init__()
        plain_to_document_component = PlainToDocument(node_name=name, node_description=description, root=self)
        pdf_to_document_component = PDFToDocument(caption_enabled=caption_enabled, ocr_enabled=ocr_enabled, root=self)
        docx_to_document_component = DOCXToDocument(caption_enabled=caption_enabled, ocr_enabled=ocr_enabled, root=self)
        pptx_to_document_component = PPTXToDocument(caption_enabled=caption_enabled, ocr_enabled=ocr_enabled, root=self)
        document_joiner_component = DocumentJoiner()
        metadata_router_component = MetadataRouter()
        document_joiner_metadata_component = DocumentJoinerMate()
        document_content_image_filler_component = DocumentContentImageFiller()
        document_writer_component = DocumentWriter()
        plain_to_document_component.add_child(document_joiner_component)
        pdf_to_document_component.add_child(document_joiner_component)
        docx_to_document_component.add_child(document_joiner_component)
        pptx_to_document_component.add_child(document_joiner_component)
        document_joiner_component.add_child(metadata_router_component)
        metadata_router_component.add_child(document_joiner_metadata_component)
        if ocr_enabled:
            image_ocr_component = ImageOCRToDocument(ocr_model=ocr_model.value, ocr_tokenizer=ocr_tokenizer.value)
            metadata_router_component.add_child(image_ocr_component)
            image_ocr_component.add_child(document_joiner_metadata_component)
        if caption_enabled:
            image_caption_component = ImageCaptionToDocument(caption_language=caption_language.value)
            metadata_router_component.add_child(image_caption_component)
            image_caption_component.add_child(document_joiner_metadata_component)
        document_joiner_metadata_component.add_child(document_content_image_filler_component)
        document_content_image_filler_component.add_child(document_writer_component)

    @property
    def name(self) -> str | None:
        return self.get_component(PlainToDocument.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(PlainToDocument.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(PlainToDocument.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(PlainToDocument.__name__).extra_node_info['description'] = description

    @property
    def caption_enabled(self) -> bool:
        return 'caption' in self.get_component(PDFToDocument.__name__).init_parameters.get('image_process_types', [])

    @caption_enabled.setter
    def caption_enabled(self, enabled: bool):
        for cls in (PDFToDocument, DOCXToDocument, PPTXToDocument):
            image_process_types: List = self.get_component(cls.__name__).init_parameters.get('image_process_types')
            if enabled:
                if 'caption' not in image_process_types:
                    image_process_types.append('caption')
            else:
                if 'caption' in image_process_types:
                    image_process_types.remove('caption')

    @property
    def caption_language(self) -> ImageCaptionLanguage:
        return ImageCaptionLanguage(self.get_component(ImageCaptionToDocument.__name__).init_parameters.get('language'))

    @caption_language.setter
    def caption_language(self, language: ImageCaptionLanguage):
        if self.caption_enabled:
            self.get_component(ImageCaptionToDocument.__name__).init_parameters['language'] = language.value
        else:
            logger.warning('Caption is not enabled, cannot set language')

    @property
    def ocr_enabled(self) -> bool:
        return 'ocr' in self.get_component(PDFToDocument.__name__).init_parameters.get('image_process_types', [])

    @ocr_enabled.setter
    def ocr_enabled(self, enabled: bool):
        for cls in (PDFToDocument, DOCXToDocument, PPTXToDocument):
            image_process_types: List = self.get_component(cls.__name__).init_parameters.get('image_process_types')
            if enabled:
                if 'ocr' not in image_process_types:
                    image_process_types.append('ocr')
            else:
                if 'ocr' in image_process_types:
                    image_process_types.remove('ocr')

    @property
    def ocr_model(self) -> ImageOCRModel:
        return ImageOCRModel(self.get_component(ImageOCRToDocument.__name__).init_parameters.get('model'))

    @ocr_model.setter
    def ocr_model(self, model: ImageOCRModel):
        if self.caption_enabled:
            self.get_component(ImageOCRToDocument.__name__).init_parameters['model'] = model.value
        else:
            logger.warning('OCR is not enabled, cannot set model')

    @property
    def ocr_tokenizer(self) -> ImageOCRModel:
        return ImageOCRModel(self.get_component(ImageOCRToDocument.__name__).init_parameters.get('tokenizer'))

    @ocr_tokenizer.setter
    def ocr_tokenizer(self, tokenizer: ImageOCRModel):
        if self.caption_enabled:
            self.get_component(ImageOCRToDocument.__name__).init_parameters['tokenizer'] = tokenizer.value
        else:
            logger.warning('OCR is not enabled, cannot set tokenizer')

    def init_connections(self, connections: dict = None):
        connections = [
            (PlainToDocument.__name__, DocumentJoiner.__name__),
            (PDFToDocument.__name__, DocumentJoiner.__name__),
            (DOCXToDocument.__name__, DocumentJoiner.__name__),
            (PPTXToDocument.__name__, DocumentJoiner.__name__),
            (DocumentJoiner.__name__, MetadataRouter.__name__),
            (MetadataRouter.__name__, DocumentJoinerMate.__name__)
        ]
        if self.ocr_enabled:
            connections.extend([
                (MetadataRouter.__name__, ImageOCRToDocument.__name__),
                (ImageOCRToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        if self.caption_enabled:
            connections.extend([
                (MetadataRouter.__name__, ImageCaptionToDocument.__name__),
                (ImageCaptionToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        connections.extend([
            (DocumentJoinerMate.__name__, DocumentContentImageFiller.__name__),
            (DocumentContentImageFiller.__name__, DocumentWriter.__name__)
        ])
        super().init_connections(connections)


class ImageParserNode(WorkflowNode):
    def __init__(self,
                 name: str = '图片解析节点',
                 description: str = '',
                 caption_enabled: bool = True,
                 caption_language: ImageCaptionLanguage = ImageCaptionLanguage.ZH,
                 ocr_enabled: bool = True,
                 ocr_model: ImageOCRModel = ImageOCRModel.Default,
                 ocr_tokenizer: ImageOCRModel = ImageOCRModel.Default_Tokenizer):
        super().__init__()
        image_to_document_component = ImageToDocument(
            node_name=name,
            node_description=description,
            caption_enabled=caption_enabled,
            ocr_enabled=ocr_enabled,
            root=self
        )
        document_joiner_component = DocumentJoiner()
        metadata_router_component = MetadataRouter()
        document_joiner_metadata_component = DocumentJoinerMate()
        document_content_image_filler_component = DocumentContentImageFiller()
        document_writer_component = DocumentWriter()
        image_to_document_component.add_child(document_joiner_component)
        document_joiner_component.add_child(metadata_router_component)
        metadata_router_component.add_child(document_joiner_metadata_component)
        if ocr_enabled:
            image_ocr_component = ImageOCRToDocument(ocr_model=ocr_model.value, ocr_tokenizer=ocr_tokenizer.value)
            metadata_router_component.add_child(image_ocr_component)
            image_ocr_component.add_child(document_joiner_metadata_component)
        if caption_enabled:
            image_caption_component = ImageCaptionToDocument(caption_language=caption_language.value)
            metadata_router_component.add_child(image_caption_component)
            image_caption_component.add_child(document_joiner_metadata_component)
        document_joiner_metadata_component.add_child(document_content_image_filler_component)
        document_content_image_filler_component.add_child(document_writer_component)

    @property
    def name(self) -> str | None:
        return self.get_component(ImageToDocument.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(ImageToDocument.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(ImageToDocument.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(ImageToDocument.__name__).extra_node_info['description'] = description

    @property
    def caption_enabled(self) -> bool:
        return 'caption' in self.get_component(ImageToDocument.__name__).init_parameters.get('image_process_types', [])

    @caption_enabled.setter
    def caption_enabled(self, enabled: bool):
        image_process_types: List = self.get_component(ImageToDocument.__name__).init_parameters.get('image_process_types')
        if enabled:
            if 'caption' not in image_process_types:
                image_process_types.append('caption')
        else:
            if 'caption' in image_process_types:
                image_process_types.remove('caption')

    @property
    def caption_language(self) -> ImageCaptionLanguage:
        return ImageCaptionLanguage(self.get_component(ImageCaptionToDocument.__name__).init_parameters.get('language'))

    @caption_language.setter
    def caption_language(self, language: ImageCaptionLanguage):
        if self.caption_enabled:
            self.get_component(ImageCaptionToDocument.__name__).init_parameters['language'] = language.value
        else:
            logger.warning('Caption is not enabled, cannot set language')

    @property
    def ocr_enabled(self) -> bool:
        return 'ocr' in self.get_component(ImageToDocument.__name__).init_parameters.get('image_process_types', [])

    @ocr_enabled.setter
    def ocr_enabled(self, enabled: bool):
        image_process_types: List = self.get_component(ImageToDocument.__name__).init_parameters.get('image_process_types')
        if enabled:
            if 'ocr' not in image_process_types:
                image_process_types.append('ocr')
        else:
            if 'ocr' in image_process_types:
                image_process_types.remove('ocr')

    @property
    def ocr_model(self) -> ImageOCRModel:
        return ImageOCRModel(self.get_component(ImageOCRToDocument.__name__).init_parameters.get('model'))

    @ocr_model.setter
    def ocr_model(self, model: ImageOCRModel):
        if self.caption_enabled:
            self.get_component(ImageOCRToDocument.__name__).init_parameters['model'] = model.value
        else:
            logger.warning('OCR is not enabled, cannot set model')

    @property
    def ocr_tokenizer(self) -> ImageOCRModel:
        return ImageOCRModel(self.get_component(ImageOCRToDocument.__name__).init_parameters.get('tokenizer'))

    @ocr_tokenizer.setter
    def ocr_tokenizer(self, tokenizer: ImageOCRModel):
        if self.caption_enabled:
            self.get_component(ImageOCRToDocument.__name__).init_parameters['tokenizer'] = tokenizer.value
        else:
            logger.warning('OCR is not enabled, cannot set tokenizer')

    def init_connections(self, connections: dict = None):
        connections = [
            (ImageToDocument.__name__, DocumentJoiner.__name__),
            (DocumentJoiner.__name__, MetadataRouter.__name__),
            (MetadataRouter.__name__, DocumentJoinerMate.__name__)
        ]
        if self.ocr_enabled:
            connections.extend([
                (MetadataRouter.__name__, ImageOCRToDocument.__name__),
                (ImageOCRToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        if self.caption_enabled:
            connections.extend([
                (MetadataRouter.__name__, ImageCaptionToDocument.__name__),
                (ImageCaptionToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        connections.extend([
            (DocumentJoinerMate.__name__, DocumentContentImageFiller.__name__),
            (DocumentContentImageFiller.__name__, DocumentWriter.__name__)
        ])
        super().init_connections(connections)


class AudioParserNode(WorkflowNode):
    def __init__(self,
                 name: str = '音频解析节点',
                 description: str = '',
                 enable_noise_reduction: bool = False,
                 enable_speaker_diarization: bool = False,
                 min_silence_duration: float = 0.5,
                 max_segment_duration: int = 30,
                 asr_model: str = 'sensevoice-v1',
                 audio_server_url: str = 'http://moi-byoa-audio-server.moi:8080'):
        super().__init__()
        audio_to_document_component = AudioToDocument(
            node_name=name,
            node_description=description,
            enable_noise_reduction=enable_noise_reduction,
            enable_speaker_diarization=enable_speaker_diarization,
            min_silence_duration=min_silence_duration,
            max_segment_duration=max_segment_duration,
            asr_model=asr_model,
            audio_server_url=audio_server_url,
            root=self
        )
        document_joiner_component = DocumentJoiner()
        metadata_router_component = MetadataRouter()
        document_joiner_metadata_component = DocumentJoinerMate()
        document_content_image_filler_component = DocumentContentImageFiller()
        document_writer_component = DocumentWriter()
        audio_to_document_component.add_child(document_joiner_component)
        document_joiner_component.add_child(metadata_router_component)
        metadata_router_component.add_child(document_joiner_metadata_component)
        if True:
            image_ocr_component = ImageOCRToDocument(
                ocr_model=ImageOCRModel.Default.value,
                ocr_tokenizer=ImageOCRModel.Default_Tokenizer.value
            )
            metadata_router_component.add_child(image_ocr_component)
            image_ocr_component.add_child(document_joiner_metadata_component)
        if True:
            image_caption_component = ImageCaptionToDocument(caption_language=ImageCaptionLanguage.ZH.value)
            metadata_router_component.add_child(image_caption_component)
            image_caption_component.add_child(document_joiner_metadata_component)
        document_joiner_metadata_component.add_child(document_content_image_filler_component)
        document_content_image_filler_component.add_child(document_writer_component)

    @property
    def name(self) -> str | None:
        return self.get_component(AudioToDocument.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(AudioToDocument.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(AudioToDocument.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(AudioToDocument.__name__).extra_node_info['description'] = description

    @property
    def enable_noise_reduction(self) -> bool:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('enable_noise_reduction')

    @enable_noise_reduction.setter
    def enable_noise_reduction(self, enabled: bool):
        self.get_component(AudioToDocument.__name__).init_parameters['enable_noise_reduction'] = enabled

    @property
    def enable_speaker_diarization(self) -> bool:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('enable_speaker_diarization')

    @enable_speaker_diarization.setter
    def enable_speaker_diarization(self, enabled: bool):
        self.get_component(AudioToDocument.__name__).init_parameters['enable_speaker_diarization'] = enabled

    @property
    def min_silence_duration(self) -> float:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('min_silence_duration')

    @min_silence_duration.setter
    def min_silence_duration(self, duration: float):
        self.get_component(AudioToDocument.__name__).init_parameters['min_silence_duration'] = duration

    @property
    def max_segment_duration(self) -> int:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('max_segment_duration')

    @max_segment_duration.setter
    def max_segment_duration(self, duration: int):
        self.get_component(AudioToDocument.__name__).init_parameters['max_segment_duration'] = duration

    @property
    def asr_model(self) -> str:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('asr_model')

    @asr_model.setter
    def asr_model(self, model):
        self.get_component(AudioToDocument.__name__).init_parameters['asr_model'] = model

    @property
    def audio_server_url(self) -> str:
        return self.get_component(AudioToDocument.__name__).init_parameters.get('audio_server_url')

    @audio_server_url.setter
    def audio_server_url(self, url: str):
        self.get_component(AudioToDocument.__name__).init_parameters['audio_server_url'] = url

    def init_connections(self, connections: dict = None):
        connections = [
            (AudioToDocument.__name__, DocumentJoiner.__name__),
            (DocumentJoiner.__name__, MetadataRouter.__name__),
            (MetadataRouter.__name__, DocumentJoinerMate.__name__)
        ]
        if True:
            connections.extend([
                (MetadataRouter.__name__, ImageOCRToDocument.__name__),
                (ImageOCRToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        if True:
            connections.extend([
                (MetadataRouter.__name__, ImageCaptionToDocument.__name__),
                (ImageCaptionToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        connections.extend([
            (DocumentJoinerMate.__name__, DocumentContentImageFiller.__name__),
            (DocumentContentImageFiller.__name__, DocumentWriter.__name__)
        ])
        super().init_connections(connections)


class VideoParserNode(WorkflowNode):
    def __init__(self,
                 name: str = '视频解析节点',
                 description: str = '',
                 enable_noise_reduction: bool = False,
                 enable_speaker_diarization: bool = False,
                 min_silence_duration: float = 1,
                 max_segment_duration: int = 60,
                 asr_model: str = 'sensevoice-v1',
                 audio_server_url: str = 'http://moi-byoa-audio-server.moi:8080'):
        super().__init__()
        video_to_document_component = VideoToDocument(
            node_name=name,
            node_description=description,
            enable_noise_reduction=enable_noise_reduction,
            enable_speaker_diarization=enable_speaker_diarization,
            min_silence_duration=min_silence_duration,
            max_segment_duration=max_segment_duration,
            asr_model=asr_model,
            audio_server_url=audio_server_url,
            root=self
        )
        document_joiner_component = DocumentJoiner()
        metadata_router_component = MetadataRouter()
        document_joiner_metadata_component = DocumentJoinerMate()
        document_content_image_filler_component = DocumentContentImageFiller()
        document_writer_component = DocumentWriter()
        video_to_document_component.add_child(document_joiner_component)
        document_joiner_component.add_child(metadata_router_component)
        metadata_router_component.add_child(document_joiner_metadata_component)
        if True:
            image_ocr_component = ImageOCRToDocument(
                ocr_model=ImageOCRModel.Default.value,
                ocr_tokenizer=ImageOCRModel.Default_Tokenizer.value
            )
            metadata_router_component.add_child(image_ocr_component)
            image_ocr_component.add_child(document_joiner_metadata_component)
        if True:
            image_caption_component = ImageCaptionToDocument(caption_language=ImageCaptionLanguage.ZH.value)
            metadata_router_component.add_child(image_caption_component)
            image_caption_component.add_child(document_joiner_metadata_component)
        document_joiner_metadata_component.add_child(document_content_image_filler_component)
        document_content_image_filler_component.add_child(document_writer_component)

    @property
    def name(self) -> str | None:
        return self.get_component(VideoToDocument.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(VideoToDocument.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(VideoToDocument.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(VideoToDocument.__name__).extra_node_info['description'] = description

    @property
    def enable_noise_reduction(self) -> bool:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('enable_noise_reduction')

    @enable_noise_reduction.setter
    def enable_noise_reduction(self, enabled: bool):
        self.get_component(VideoToDocument.__name__).init_parameters['enable_noise_reduction'] = enabled

    @property
    def enable_speaker_diarization(self) -> bool:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('enable_speaker_diarization')

    @enable_speaker_diarization.setter
    def enable_speaker_diarization(self, enabled: bool):
        self.get_component(VideoToDocument.__name__).init_parameters['enable_speaker_diarization'] = enabled

    @property
    def min_silence_duration(self) -> float:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('min_silence_duration')

    @min_silence_duration.setter
    def min_silence_duration(self, duration: float):
        self.get_component(VideoToDocument.__name__).init_parameters['min_silence_duration'] = duration

    @property
    def max_segment_duration(self) -> int:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('max_segment_duration')

    @max_segment_duration.setter
    def max_segment_duration(self, duration: int):
        self.get_component(VideoToDocument.__name__).init_parameters['max_segment_duration'] = duration

    @property
    def asr_model(self) -> str:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('asr_model')

    @asr_model.setter
    def asr_model(self, model):
        self.get_component(VideoToDocument.__name__).init_parameters['asr_model'] = model

    @property
    def audio_server_url(self) -> str:
        return self.get_component(VideoToDocument.__name__).init_parameters.get('audio_server_url')

    @audio_server_url.setter
    def audio_server_url(self, url: str):
        self.get_component(VideoToDocument.__name__).init_parameters['audio_server_url'] = url

    def init_connections(self, connections: dict = None):
        connections = [
            (VideoToDocument.__name__, DocumentJoiner.__name__),
            (DocumentJoiner.__name__, MetadataRouter.__name__),
            (MetadataRouter.__name__, DocumentJoinerMate.__name__)
        ]
        if True:
            connections.extend([
                (MetadataRouter.__name__, ImageOCRToDocument.__name__),
                (ImageOCRToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        if True:
            connections.extend([
                (MetadataRouter.__name__, ImageCaptionToDocument.__name__),
                (ImageCaptionToDocument.__name__, DocumentJoinerMate.__name__)
            ])
        connections.extend([
            (DocumentJoinerMate.__name__, DocumentContentImageFiller.__name__),
            (DocumentContentImageFiller.__name__, DocumentWriter.__name__)
        ])
        super().init_connections(connections)


class SplitNode(WorkflowNode):
    def __init__(self,
                 name: str = '分段节点',
                 description: str = '',
                 is_custom_split_symbol: bool = False,
                 split_mode: SplitMode = SplitMode.Single,
                 custom_separators: List = None,
                 split_length: int = 1024,
                 split_overlap: int = 50,
                 split_unit: str = 'single'):
        super().__init__()
        if custom_separators is None:
            custom_separators = ["\n\n",]
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            cls(
                node_name=name,
                node_description=description,
                is_custom_split_symbol=is_custom_split_symbol,
                split_mode=split_mode.value,
                custom_separators=custom_separators,
                split_length=split_length,
                split_overlap=split_overlap,
                split_unit=split_unit,
                root=self
            )

    @property
    def name(self) -> str | None:
        return self.get_component(DocumentSplitter.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
                self.get_component(cls.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(DocumentSplitter.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
                self.get_component(cls.__name__).extra_node_info['description'] = description

    @property
    def is_custom_split_symbol(self) -> bool:
        return self.get_component(DocumentSplitter.__name__).extra_node_info.get('isCustomSplitSymbol')

    @is_custom_split_symbol.setter
    def is_custom_split_symbol(self, is_custom_split_symbol: bool):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).extra_node_info['isCustomSplitSymbol'] = is_custom_split_symbol

    @property
    def split_mode(self) -> SplitMode:
        return SplitMode(self.get_component(DocumentSplitter.__name__).extra_node_info.get('splitMode'))

    @split_mode.setter
    def split_mode(self, mode: SplitMode):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).extra_node_info['splitMode'] = mode.value

    @property
    def custom_separators(self) -> List:
        return self.get_component(DocumentSplitter.__name__).init_parameters.get('custom_separators')

    @custom_separators.setter
    def custom_separators(self, separators: List):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).init_parameters['custom_separators'] = separators

    @property
    def split_length(self) -> int:
        return self.get_component(DocumentSplitter.__name__).init_parameters.get('split_length')

    @split_length.setter
    def split_length(self, split_length: int):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).init_parameters['split_length'] = split_length

    @property
    def split_overlap(self) -> int:
        return self.get_component(DocumentSplitter.__name__).init_parameters.get('split_overlap')

    @split_overlap.setter
    def split_overlap(self, split_overlap: int):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).init_parameters['split_overlap'] = split_overlap

    @property
    def split_unit(self) -> int:
        return self.get_component(DocumentSplitter.__name__).init_parameters.get('split_unit')

    @split_unit.setter
    def split_unit(self, split_unit: str):
        for cls in (DocumentSplitter, DocumentSplitterImageOCR, DocumentSplitterImageCaption):
            self.get_component(cls.__name__).init_parameters['split_unit'] = split_unit


class DataCleanNode(WorkflowNode):
    def __init__(self,
                 name: str = '数据清洗节点',
                 description: str = '',
                 deduplication_by_md5: bool = False,
                 deduplication_by_similarity: bool = False,
                 deduplication_ngram_ratio: float = 0.5,
                 filter_special_char_ratio: float = 0.5,
                 remove_html_labels: bool = False,
                 remove_invisible_char: bool = False,
                 remove_persional_message: bool = True,
                 remove_sensitive_words: bool = False,
                 remove_url: bool = False,
                 switch_deduplication: bool = False,
                 switch_special_char_filter: bool = False,
                 switch_special_char_remove: bool = False,
                 switch_text_standardization: bool = False,
                 traditional_chinese_to_simple: bool = False,
                 unicode_normalization: bool = False):
        super().__init__()
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            cls(
                node_name=name,
                node_description=description,
                deduplication_by_md5=deduplication_by_md5,
                deduplication_by_similarity=deduplication_by_similarity,
                deduplication_ngram_ratio=deduplication_ngram_ratio,
                filter_special_char_ratio=filter_special_char_ratio,
                remove_html_labels=remove_html_labels,
                remove_invisible_char=remove_invisible_char,
                remove_persional_message=remove_persional_message,
                remove_sensitive_words=remove_sensitive_words,
                remove_url=remove_url,
                switch_deduplication=switch_deduplication,
                switch_special_char_filter=switch_special_char_filter,
                switch_special_char_remove=switch_special_char_remove,
                switch_text_standardization=switch_text_standardization,
                traditional_chinese_to_simple=traditional_chinese_to_simple,
                unicode_normalization=unicode_normalization,
                root=self
            )

    @property
    def name(self) -> str | None:
        return self.get_component(DocumentCleaner.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
                self.get_component(cls.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(DocumentCleaner.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
                self.get_component(cls.__name__).extra_node_info['description'] = description

    @property
    def deduplication_by_md5(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('deduplication_by_md5')

    @deduplication_by_md5.setter
    def deduplication_by_md5(self, deduplication_by_md5: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['deduplication_by_md5'] = deduplication_by_md5

    @property
    def deduplication_by_similarity(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('deduplication_by_similarity')

    @deduplication_by_similarity.setter
    def deduplication_by_similarity(self, deduplication_by_similarity: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['deduplication_by_similarity'] = deduplication_by_similarity

    @property
    def deduplication_ngram_ratio(self) -> float:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('deduplication_ngram_ratio')

    @deduplication_ngram_ratio.setter
    def deduplication_ngram_ratio(self, deduplication_ngram_ratio: float):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['deduplication_ngram_ratio'] = deduplication_ngram_ratio

    @property
    def filter_special_char_ratio(self) -> float:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('filter_special_char_ratio')

    @filter_special_char_ratio.setter
    def filter_special_char_ratio(self, filter_special_char_ratio: float):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['filter_special_char_ratio'] = filter_special_char_ratio

    @property
    def remove_html_labels(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('remove_html_labels')

    @remove_html_labels.setter
    def remove_html_labels(self, remove_html_labels: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['remove_html_labels'] = remove_html_labels

    @property
    def remove_invisible_char(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('remove_invisible_char')

    @remove_invisible_char.setter
    def remove_invisible_char(self, remove_invisible_char: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['remove_invisible_char'] = remove_invisible_char

    @property
    def remove_persional_message(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('remove_persional_message')

    @remove_persional_message.setter
    def remove_persional_message(self, remove_persional_message: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['remove_persional_message'] = remove_persional_message

    @property
    def remove_sensitive_words(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('remove_sensitive_words')

    @remove_sensitive_words.setter
    def remove_sensitive_words(self, remove_sensitive_words: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['remove_sensitive_words'] = remove_sensitive_words

    @property
    def remove_url(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('remove_url')

    @remove_url.setter
    def remove_url(self, remove_url: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['remove_url'] = remove_url

    @property
    def switch_deduplication(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('switch_deduplication')

    @switch_deduplication.setter
    def switch_deduplication(self, switch_deduplication: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['switch_deduplication'] = switch_deduplication

    @property
    def switch_special_char_filter(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('switch_special_char_filter')

    @switch_special_char_filter.setter
    def switch_special_char_filter(self, switch_special_char_filter: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['switch_special_char_filter'] = switch_special_char_filter

    @property
    def switch_special_char_remove(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('switch_special_char_remove')

    @switch_special_char_remove.setter
    def switch_special_char_remove(self, switch_special_char_remove: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['switch_special_char_remove'] = switch_special_char_remove

    @property
    def switch_text_standardization(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('switch_text_standardization')

    @switch_text_standardization.setter
    def switch_text_standardization(self, switch_text_standardization: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['switch_text_standardization'] = switch_text_standardization

    @property
    def traditional_chinese_to_simple(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('traditional_chinese_to_simple')

    @traditional_chinese_to_simple.setter
    def traditional_chinese_to_simple(self, traditional_chinese_to_simple: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['traditional_chinese_to_simple'] = traditional_chinese_to_simple

    @property
    def unicode_normalization(self) -> bool:
        return self.get_component(DocumentCleaner.__name__).init_parameters.get('unicode_normalization')

    @unicode_normalization.setter
    def unicode_normalization(self, unicode_normalization: bool):
        for cls in (DocumentCleaner, DocumentCleanerImageOCR, DocumentCleanerImageCaption):
            self.get_component(cls.__name__).init_parameters['unicode_normalization'] = unicode_normalization


class TextEmbeddingNode(WorkflowNode):
    def __init__(self,
                 name: str = '文本嵌入节点',
                 description: str = '',
                 model: str = 'BAAI/bge-m3'):
        super().__init__()
        DocumentEmbedder(
            node_name=name,
            node_description=description,
            model=model,
            root=self
        )
        # self.children = None

    @property
    def name(self) -> str | None:
        return self.get_component(DocumentEmbedder.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(DocumentEmbedder.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(DocumentEmbedder.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(DocumentEmbedder.__name__).extra_node_info['description'] = description

    @property
    def model(self) -> str:
        return self.get_component(DocumentEmbedder.__name__).init_parameters.get('model')

    @model.setter
    def model(self, model: str):
        self.get_component(DocumentEmbedder.__name__).init_parameters['model'] = model


class DataEnhancementNode(WorkflowNode):
    def __init__(self,
                 name: str = '数据增强节点',
                 description: str = '',
                 samples_per_block: int = 10,
                 data_format: DataEnhancementFormat = DataEnhancementFormat.Alpaca,
                 json_schema: dict = None):
        super().__init__()
        if json_schema is None:
            json_schema = {}
        DataAugmentation(
            node_name=name,
            node_description=description,
            samples_per_block=samples_per_block,
            data_format=data_format.value,
            json_schema=json_schema,
            root=self
        )
        # self.children = None

    @property
    def name(self) -> str | None:
        return self.get_component(DataAugmentation.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(DataAugmentation.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(DataAugmentation.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(DataAugmentation.__name__).extra_node_info['description'] = description

    @property
    def samples_per_block(self) -> int:
        return self.get_component(DataAugmentation.__name__).init_parameters.get('samples_per_block')

    @samples_per_block.setter
    def samples_per_block(self, samples_per_block: int):
        self.get_component(DataAugmentation.__name__).init_parameters['samples_per_block'] = samples_per_block

    @property
    def data_format(self) -> DataEnhancementFormat:
        return DataEnhancementFormat(self.get_component(DataAugmentation.__name__).init_parameters.get('data_format'))

    @data_format.setter
    def data_format(self, data_format: DataEnhancementFormat):
        self.get_component(DataAugmentation.__name__).init_parameters['data_format'] = data_format.value

    @property
    def json_schema(self) -> dict:
        return self.get_component(DataAugmentation.__name__).init_parameters.get('json_schema')

    @json_schema.setter
    def json_schema(self, json_schema: dict):
        self.get_component(DataAugmentation.__name__).init_parameters['json_schema'] = json_schema


class InformationExtractionNode(WorkflowNode):
    def __init__(self,
                 name: str = '信息提取节点',
                 description: str = '',
                 extraction_template: ExtractionTemplate = ExtractionTemplate.Custom,
                 model_type: str = 'llmmodel',  # llmmodel or multimodel
                 model: str = 'Qwen/Qwen2.5-VL-32B-Instruct',  # Qwen/Qwen2.5-VL-32B-Instruct
                 json_schema: dict = None):
        super().__init__()
        if json_schema is None:
            json_schema = {
                "title": "ExtractInfo",
                "description": "",
                "type": "object",
                "properties": {},
                "required": []
            }
        StructedExtraction(
            node_name=name,
            node_description=description,
            extraction_template=extraction_template.value,
            model_type=model_type,
            model=model,
            json_schema=json_schema,
            root=self
        )

    @property
    def name(self) -> str | None:
        return self.get_component(StructedExtraction.__name__).extra_node_info.get('name')

    @name.setter
    def name(self, name: str):
        if name:
            self.get_component(StructedExtraction.__name__).extra_node_info['name'] = name

    @property
    def description(self) -> str | None:
        return self.get_component(StructedExtraction.__name__).extra_node_info.get('description')

    @description.setter
    def description(self, description: str):
        if description is not None:
            self.get_component(StructedExtraction.__name__).extra_node_info['description'] = description

    @property
    def extraction_template(self) -> ExtractionTemplate:
        return ExtractionTemplate(self.get_component(StructedExtraction.__name__).extra_node_info.get('extraction_template'))

    @extraction_template.setter
    def extraction_template(self, extraction_template: ExtractionTemplate):
        self.get_component(StructedExtraction.__name__).extra_node_info['extraction_template'] = extraction_template.value

    @property
    def model_type(self) -> str:
        return self.get_component(StructedExtraction.__name__).init_parameters.get('model_type')

    @model_type.setter
    def model_type(self, model_type: str):
        self.get_component(StructedExtraction.__name__).init_parameters['model_type'] = model_type

    @property
    def model(self) -> str:
        return self.get_component(StructedExtraction.__name__).init_parameters.get('model')

    @model.setter
    def model(self, model: str):
        self.get_component(StructedExtraction.__name__).init_parameters['model'] = model

    @property
    def json_schema(self) -> dict:
        return self.get_component(StructedExtraction.__name__).init_parameters.get('json_schema')

    @json_schema.setter
    def json_schema(self, json_schema: dict):
        self.get_component(StructedExtraction.__name__).init_parameters['json_schema'] = json_schema


class ProcessFlow(BaseModel):
    _ignore_attrs = ('description', 'nodes')
    # _parser_nodes = (DocumentParserNode.__name__, ImageParserNode.__name__, AudioParserNode.__name__, VideoParserNode.__name__)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.components: List[NodeComponent] = kwargs.get('components', [])
        self.connections: List[NodeConnection] = kwargs.get('connections', [])
        self.edges = kwargs.get('edges', [])
        self.extra_components = kwargs.get('extra_components', [])
        if kwargs.get('model_type'):
            self.model_type = kwargs.get('model_type')
        self.description = kwargs.get('moi_workflow')[0]['description'] if kwargs.get('moi_workflow') else kwargs.get('description', '')
        # self.nodes: List[WorkflowNode] | None = None if kwargs.get('components', []) else []
        if kwargs.get('components', []):
            self.nodes = self.retrieve_nodes()
        else:
            self.nodes = []

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def moi_workflow(self):
        return [{'description': self._description}]

    @property
    def components(self) -> List[NodeComponent]:
        if self._components:
            return self._components
        else:
            return self.get_components()

    @components.setter
    def components(self, components: List[dict]):
        self._components = []
        for component in components:
            if component.get('name').replace('-', '') not in [c.name for c in self._components]:
                self._components.append(NodeComponent(_type_name=component.get('name').replace('-', ''), **component))

    def has_component(self, name) -> bool:
        return any([component.name == name for component in self.get_components()])

    def get_components(self):
        if self.nodes:
            return self.get_node(StartNode.__name__).get_components()
        else:
            raise Exception('no nodes found in this workflow')

    def get_component(self, name) -> NodeComponent | None:
        for component in self.get_components():
            if component.name.replace('-', '') == name:
                return component
        raise Exception(f"component {name} is not found in workflow")

    def merge_components(self, node: WorkflowNode):
        if node.__class__.__name__ == StartNode.__name__:
            parser_nodes = [child for child in node.children if 'ParserNode' in child.__class__.__name__]
            for child in node.children:
                for x in [c for c in child.components if not c.parents]:
                    node.components[-1].children.append(x)
                    x.parents.append(node.components[-1])
                if parser_nodes and child.has_component(DocumentJoiner.__name__):
                    if child is not parser_nodes[0]:
                        component = child.get_component(DocumentJoiner.__name__)
                        if component.parents:
                            for parent in component.parents:
                                if parent.root.__class__.__name__ in [n.__class__.__name__ for n in self.nodes]:
                                    parent.replace_child(component, parser_nodes[0].get_component(DocumentJoiner.__name__))
                        else:
                            logger.warning(f"Component {component.__class__.__name__} has no parents.")
            for child in node.children:
                self.merge_components(child)
        elif 'ParserNode' in node.__class__.__name__:
            for child in node.children:
                if isinstance(child, SplitNode):
                    self.get_component(MetadataRouter.__name__).insert_one_child(
                        child.get_component(DocumentSplitter.__name__)
                    )
                    self.get_component(ImageOCRToDocument.__name__).insert_one_child(
                        child.get_component(DocumentSplitterImageOCR.__name__)
                    )
                    self.get_component(ImageCaptionToDocument.__name__).insert_one_child(
                        child.get_component(DocumentSplitterImageCaption.__name__)
                    )
                elif isinstance(child, DataCleanNode):
                    self.get_component(MetadataRouter.__name__).insert_one_child(
                        child.get_component(DocumentCleaner.__name__)
                    )
                    self.get_component(ImageOCRToDocument.__name__).insert_one_child(
                        child.get_component(DocumentCleanerImageOCR.__name__)
                    )
                    self.get_component(ImageCaptionToDocument.__name__).insert_one_child(
                        child.get_component(DocumentCleanerImageCaption.__name__)
                    )
                elif isinstance(child, InformationExtractionNode):
                    for c in node.get_component(DocumentJoinerMate.__name__).children:
                        self.get_component(DocumentJoinerMate.__name__).replace_child(
                            c, child.get_component(StructedExtraction.__name__)
                        )
            for child in node.children:
                self.merge_components(child)
        elif node.__class__.__name__ in (SplitNode.__name__, DataCleanNode.__name__):
            for child in node.children:
                if isinstance(child, DataCleanNode):
                    self.get_component(DocumentSplitter.__name__).insert_child(
                        child.get_component(DocumentCleaner.__name__)
                    )
                    self.get_component(DocumentSplitterImageOCR.__name__).insert_child(
                        child.get_component(DocumentCleanerImageOCR.__name__)
                    )
                    self.get_component(DocumentSplitterImageCaption.__name__).insert_child(
                        child.get_component(DocumentCleanerImageCaption.__name__)
                    )
                elif isinstance(child, TextEmbeddingNode):
                    self.get_component(DocumentJoinerMate.__name__).insert_child(
                        child.get_component(DocumentEmbedder.__name__)
                    )
                elif isinstance(child, DataEnhancementNode):
                    self.get_component(DocumentWriter.__name__).insert_child(
                        child.get_component(DataAugmentation.__name__)
                    )
            for child in node.children:
                self.merge_components(child)
        elif node.__class__.__name__ == InformationExtractionNode.__name__:
            for child in node.children:
                if isinstance(child, DataEnhancementNode):
                    self.get_component(StructedExtraction.__name__).insert_child(
                            child.get_component(DataAugmentation.__name__)
                    )

    @property
    def connections(self) -> List[NodeConnection]:
        if self._connections:
            return self._connections
        else:
            return self.get_node('StartNode').get_connections()
            # return self.nodes[0].get_connections()

    @connections.setter
    def connections(self, connections: List[dict]):
        self._connections = []
        for connection in connections:
            self._connections.append(NodeConnection(**connection))

    def rebuild_connections(self):
        self.nodes = self.get_nodes()
        removed_nodes = []
        for component in self.components:
            if component.root.__class__.__name__ not in [n.__class__.__name__ for n in self.nodes]:
                if component.root.__class__.__name__ not in [n.__class__.__name__ for n in removed_nodes]:
                    removed_nodes.append(component.root)
        for n in set(removed_nodes + self.nodes):
            n.init_connections()
        self.merge_components(self.get_node(StartNode.__name__))
        self.components = []
        self.connections = []

    @property
    def nodes(self) -> List[WorkflowNode] | None:
        # if self._nodes is None:
        #     self.nodes = self.retrieve_nodes()
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List[WorkflowNode] |  None):
        self._nodes = nodes

    def has_any_nodes(self, key) -> bool:
        return any([node.__class__.__name__ == key for node in self.nodes])

    def retrieve_nodes(self):
        components, nodes = {}, []
        for component in self.components:
            components[component.name] = component
        if FileRouterComponent.__name__ in components:
            start_node = StartNode().retrieve_from_components(self.components)
            setattr(start_node, '_workflow', self)
        if PlainToDocument.__name__ in components:
            _ = DocumentParserNode().retrieve_from_components(self.components)
        if ImageToDocument.__name__ in components:
            _ = ImageParserNode().retrieve_from_components(self.components)
        if AudioToDocument.__name__ in components:
            _ = AudioParserNode().retrieve_from_components(self.components)
        if VideoToDocument.__name__ in components:
            _ = VideoParserNode().retrieve_from_components(self.components)
        if DocumentSplitter.__name__ in components:
            _ = SplitNode().retrieve_from_components(self.components)
        if DocumentCleaner.__name__ in components:
            _ = DataCleanNode().retrieve_from_components(self.components)
        if DocumentEmbedder.__name__ in components:
            _ = TextEmbeddingNode().retrieve_from_components(self.components)
        if DataAugmentation.__name__ in components:
            _ = DataEnhancementNode().retrieve_from_components(self.components)
        if StructedExtraction.__name__ in components:
            _ = InformationExtractionNode().retrieve_from_components(self.components)
        for connection in self.connections:
            parent: NodeComponent = components[connection.sender.split('.')[0]]
            child: NodeComponent = components[connection.receiver.split('.')[0]]
            if parent not in child.parents:
                child.parents.append(parent)
            if child not in parent.children:
                parent.children.append(child)
        root_components = [component for component in self.components if not component.parents]

        def connect(_component: NodeComponent):
            for _child in _component.children:
                if _component.root.__class__.__name__ != _child.root.__class__.__name__:
                    if _component.root.__class__.__name__ not in [n.__class__.__name__ for n in nodes]:
                        nodes.append(_component.root)
                    if 'ParserNode' in _component.root.__class__.__name__ and 'ParserNode' in _child.root.__class__.__name__:
                        continue
                    if _component.root.__class__.__name__ not in [_c.__class__.__name__ for _c in _child.root.children]:
                        if _child.root.__class__.__name__ not in [n.__class__.__name__ for n in nodes]:
                            if _child.root.__class__.__name__ in [c.__name__ for c in (TextEmbeddingNode, DataEnhancementNode, InformationExtractionNode)]:
                                parent_node: WorkflowNode = nodes[-1]
                            else:
                                parent_node: WorkflowNode = _component.root
                            if _child.root.__class__.__name__ not in [_c.__class__.__name__ for _c in parent_node.children]:
                                parent_node.children.append(_child.root)
                            if parent_node.__class__.__name__ not in [_c.__class__.__name__ for _c in _child.root.parents]:
                                _child.root.parents.append(parent_node)
                            nodes.append(_child.root)
            for _child in _component.children:
                connect(_child)

        for root_component in root_components:
            connect(root_component)
        # nodes.append(EndNode())
        # setattr(nodes[-1], '_workflow', self)
        return nodes

    def get_nodes(self) -> List[WorkflowNode]:
        return [self.get_node(StartNode.__name__)] + self.get_node(StartNode.__name__).get_child_nodes()

    def get_node(self, _type) -> WorkflowNode:
        if self.nodes:
            if not isinstance(self.nodes[0], StartNode):
                raise Exception('workflow is not started with a StartNode')
        else:
            raise Exception('no nodes found in this workflow')
        for node in self.nodes:
            if node.__class__.__name__ == _type:
                return node
        raise Exception(f"Node {_type} is not found in this workflow")

    def start(self) -> StartNode:
        start_node: StartNode = StartNode()
        setattr(start_node, '_workflow', self)
        self.nodes.append(start_node)
        return start_node

    def end(self):
        # self.nodes.append(EndNode())
        # setattr(self.nodes[-1], '_workflow', self)
        if self.nodes:
            if isinstance(self.nodes[0], StartNode):
                self.merge_components(self.nodes[0])
            else:
                raise Exception('workflow is not started with a StartNode')
        else:
            raise Exception('no nodes found in this workflow')

    def insert_node(self, name: str, node: WorkflowNode, abandon_children: bool = False):
        parent = self.get_node(name)
        if parent.children is None:
            raise Exception(f"Node '{name}' cannot be parent node")
        if node.__class__.__name__ in [n.__class__.__name__ for n in self.nodes]:
            raise Exception(f"Node '{node.__class__.__name__}' already exists in workflow")
        if node.children:
            raise Exception(f"Node '{node.__class__.__name__}' cannot have children node")
        else:
            if 'ParserNode' in node.__class__.__name__ and parent.__class__.__name__ != StartNode.__name__:
                raise Exception(f"parser nodes cannot be child of node '{parent.__class__.__name__}'")
            if parent.children:
                if node.__class__.__name__ in [n.__class__.__name__ for n in parent.children]:
                    logger.warning(f"Node '{node.__class__.__name__}' is already a child of node '{parent.__class__.__name__}'")
                else:
                    parser_nodes = [n for n in self.nodes if 'ParserNode' in n.__class__.__name__]
                    if parser_nodes:
                        parser_nodes_in_queue = []
                        for cls in (DocumentParserNode, ImageParserNode, AudioParserNode, VideoParserNode):
                            for parser_node in parser_nodes + [node]:
                                if parser_node.__class__.__name__ == cls.__name__:
                                    parser_nodes_in_queue.append(parser_node)
                                    break
                        for parser_node in parser_nodes:
                            if not abandon_children and parser_node.__class__.__name__ == parser_nodes_in_queue[0].__class__.__name__:
                                continue
                            if parser_node.children:
                                # parser_nodes_in_queue[0].children.extend([n for n in parser_node.children])
                                for child in parser_node.children:
                                    parser_node.children.pop([n.__class__.__name__ for n in parser_node.children].index(child.__class__.__name__))
                                    parent_index = [n.__class__.__name__ for n in child.parents].index(parser_node.__class__.__name__)
                                    if abandon_children:
                                        child.parents.pop(parent_index)
                                    else:
                                        if child.__class__.__name__ not in [n.__class__.__name__ for n in parser_nodes_in_queue[0].children]:
                                            parser_nodes_in_queue[0].children.append(child)
                                        child.parents[parent_index] = parser_nodes_in_queue[0]
                        parent.children = [n for n in parser_nodes_in_queue]
                        node.parents.append(parent)
                        insert_index = [n.__class__.__name__ for n in self.nodes].index(parser_nodes[0].__class__.__name__)
                        self.nodes = self.nodes[:insert_index] + parser_nodes_in_queue + self.nodes[insert_index + len(parser_nodes):]
                    else:
                        for child in parent.children:
                            parent.children.pop([n.__class__.__name__ for n in parent.children].index(child.__class__.__name__))
                            parent_index = [n.__class__.__name__ for n in child.parents].index(parent.__class__.__name__)
                            if abandon_children:
                                child.parents.pop(parent_index)
                            else:
                                child.parents[parent_index] = node
                                node.children.append(child)
                        parent.children.append(node)
                        node.parents.append(parent)
                        insert_index = [n.__class__.__name__ for n in self.nodes].index(parent.__class__.__name__)
                        self.nodes = self.nodes[:insert_index + 1] + [node] + self.nodes[insert_index + 1:]
            else:
                parent.children.append(node)
                node.parents.append(parent)
        self.rebuild_connections()

    def remove_node(self, name: str, abandon_children: bool = False):
        if name in (StartNode.__name__, EndNode.__name__):
            raise Exception('Cannot remove StartNode or EndNode')
        node = self.get_node(name)
        self.nodes.pop([n.__class__.__name__ for n in self.nodes].index(node.__class__.__name__))
        if node.parents:
            for parent in node.parents:
                parser_nodes = [n for n in self.nodes if 'ParserNode' in n.__class__.__name__]
                node_index = [n.__class__.__name__ for n in parent.children].index(node.__class__.__name__)
                parent.children.pop(node_index)
                node.parents.pop([n.__class__.__name__ for n in node.parents].index(parent.__class__.__name__))
                if not abandon_children and node.children:
                    if parser_nodes:
                        parser_nodes[0].children.extend(node.children)
                    else:
                        parent.children = parent.children[:node_index] + node.children + parent.children[node_index:]
                    for child in node.children:
                        node_index = [n.__class__.__name__ for n in child.parents].index(node.__class__.__name__)
                        if parser_nodes:
                            child.parents[node_index] = parser_nodes[0]
                        else:
                            child.parents[node_index] = parent
                        child_index = [n.__class__.__name__ for n in node.children].index(child.__class__.__name__)
                        node.children.pop(child_index)
        else:
            if not abandon_children and node.children:
                for child in node.children:
                    node.children.pop([n.__class__.__name__ for n in node.children].index(child.__class__.__name__))
                    child.parents.pop([n.__class__.__name__ for n in child.parents].index(node.__class__.__name__))
        self.rebuild_connections()

    def replace_node(self, name: str, node: WorkflowNode, abandon_children: bool = False):
        if name in (StartNode.__name__, EndNode.__name__):
            raise Exception('Cannot replace StartNode or EndNode')
        if node.__class__.__name__ in [c.__class__.__name__ for c in self.nodes]:
            # _ = self.nodes.pop([n.__class__.__name__ for n in self.nodes].index(node.__class__.__name__))
            raise Exception(f"Node '{node.__class__.__name__}' already exists in workflow")
        if node.children:
            raise Exception(f"Node '{node.__class__.__name__}' cannot have children node")
        old_node = self.get_node(name)
        self.nodes[[n.__class__.__name__ for n in self.nodes].index(old_node.__class__.__name__)] = node
        if old_node.parents:
            for parent in old_node.parents:
                parent.children[[n.__class__.__name__ for n in parent.children].index(old_node.__class__.__name__)] = node
                old_node.parents.pop([n.__class__.__name__ for n in old_node.parents].index(parent.__class__.__name__))
                node.parents.append(parent)
                if not abandon_children and old_node.children:
                    for child in old_node.children:
                        child.parents[[n.__class__.__name__ for n in child.parents].index(old_node.__class__.__name__)] = node
                        old_node.children.pop([n.__class__.__name__ for n in old_node.children].index(child.__class__.__name__))
                        node.children.append(child)
        else:
            if not abandon_children and old_node.children:
                for child in old_node.children:
                    child.parents[[n.__class__.__name__ for n in child.parents].index(old_node.__class__.__name__)] = node
                    old_node.children.pop([n.__class__.__name__ for n in node.children].index(child.__class__.__name__))
                    node.children.append(child)
        self.rebuild_connections()


if __name__ == '__main__':
    process_flow = ProcessFlow()
    _start_node = process_flow.start()
    _parser_node: WorkflowNode = _start_node.add_child(DocumentParserNode())
    _ = _start_node.add_child(ImageParserNode())
    _ = _start_node.add_child(AudioParserNode())
    _ = _start_node.add_child(VideoParserNode())
    _split_node: WorkflowNode = _parser_node.add_child(SplitNode())
    _ = _split_node.add_child(TextEmbeddingNode())
    process_flow.end()
    print(process_flow)
