from __future__ import annotations
import time
from typing import List
from service.models import *
from service.utils import FactoryMeta


FILE_ROUTER_MIME_TYPES = [
    "text/plain",
    "text/markdown",
    "text/html",
    "image/.*",
    "audio/.*",
    "video/.*",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-outlook",
    "message/rfc822"
]

DOCUMENT_MIME_TYPE_MAPPING = {
    'ImageToDocument': FILE_ROUTER_MIME_TYPES[3],
    'AudioToDocument': FILE_ROUTER_MIME_TYPES[4],
    'VideoToDocument': FILE_ROUTER_MIME_TYPES[5],
    'PDFToDocument': FILE_ROUTER_MIME_TYPES[6],
    'DOCXToDocument': FILE_ROUTER_MIME_TYPES[7],
    'PPTXToDocument': FILE_ROUTER_MIME_TYPES[8],
}


class NodeConnection(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sender: str = kwargs.get('sender')
        self.receiver: str = kwargs.get('receiver')


class NodeComponent(metaclass=FactoryMeta):
    _ignore_attrs = ('id', 'root', 'parents', 'children')
    # _ignore_none_value = ('extra_node_info',)
    def __init__(self, **kwargs):
        # self.addr = id(self)
        self.name: str = kwargs.get('name', getattr(self, '_type_name'))
        self.intro: str = kwargs.get('intro', self.__class__.__name__)
        self.init_parameters = kwargs.get('init_parameters', {})
        self.component_id = kwargs.get('component_id')
        if kwargs.get('component_id'):
            self.id = self.component_id.split('_')[1]
        else:
            self.id = f'{int(time.time() * 1000)}'
        if 'extra_node_info' in kwargs:
            self.extra_node_info = kwargs.get('extra_node_info')
        self.input_keys = kwargs.get('input_keys', {})
        self.output_keys = kwargs.get('output_keys', {})
        self.position = kwargs.get('position', {'x': 0, 'y': 0})
        self.parents: List[NodeComponent] = []
        self.children: List[NodeComponent] = []
        self.root = kwargs.get('root', None)
        if self.root is not None and self.name not in [component.name for component in self.root.components]:
            self.root.components.append(self)

    @property
    def component_id(self):
        if self._component_id:
            return self._component_id
        else:
            return f'{self.intro}_{self.id}'

    @component_id.setter
    def component_id(self, component_id):
        self._component_id = component_id

    @property
    def extra_node_info(self) -> dict:
        # return {'name': self._node_name, 'description': self._node_description}
        return getattr(self, '_extra_node_info', None)

    @extra_node_info.setter
    def extra_node_info(self, kwargs):
        self._node_name = kwargs.get('name')
        self._node_description = kwargs.get('description')
        self._extra_node_info = kwargs

    @property
    def init_parameters(self) -> dict:
        return self._init_parameters

    @init_parameters.setter
    def init_parameters(self, kwargs):
        self._init_parameters = kwargs

    @property
    def children(self) -> List[NodeComponent]:
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    def get_components(self) -> List[NodeComponent]:
        components = [self]
        for child in self.children:
            components.extend(child.get_components())
        return components

    def get_connections(self) -> List[NodeConnection]:
        connections: List[NodeConnection] = []
        if isinstance(self, FileRouterComponent):
            for child in self.children:
                if isinstance(child, PlainToDocument):
                    connections.append(NodeConnection(
                        sender=f"{self.name}.text/plain",
                        receiver=f"{child.name}.sources"
                    ))
                    connections.append(NodeConnection(
                        sender=f"{self.name}.text/markdown",
                        receiver=f"{child.name}.sources"
                    ))
                elif isinstance(child, StructedExtraction):
                    connections.append(NodeConnection(
                        sender=f"{self.name}.application/pdf",
                        receiver=f"{child.name}.documents"
                    ))
                else:
                    connections.append(NodeConnection(
                        sender=f"{self.name}.{DOCUMENT_MIME_TYPE_MAPPING[child.name]}",
                        receiver=f"{child.name}.sources"
                    ))
        elif isinstance(self, MetadataRouter):
            for child in self.children:
                if isinstance(child, ImageOCRToDocument):
                    connections.append(NodeConnection(
                        sender=f"{self.name}.image_ocr",
                        receiver=f"{child.name}.documents"
                    ))
                elif isinstance(child, ImageCaptionToDocument):
                    connections.append(NodeConnection(
                        sender=f"{self.name}.image_caption",
                        receiver=f"{child.name}.documents"
                    ))
                else:
                    connections.append(NodeConnection(
                        sender=f"{self.name}.text",
                        receiver=f"{child.name}.documents"
                    ))
        elif isinstance(self, (DocumentWriter, StructedExtraction)):
            for child in self.children:
                if isinstance(child, DataAugmentation):
                    connections.append(NodeConnection(
                        sender=f"{self.name}.documents_written",
                        receiver=f"{child.name}.count"
                    ))
                else:
                    connections.append(NodeConnection(
                        sender=f"{self.name}.documents",
                        receiver=f"{child.name}.documents"
                    ))
        else:
            for child in self.children:
                connections.append(NodeConnection(
                    sender=f"{self.name}.documents",
                    receiver=f"{child.name}.documents"
                ))
        for child in self.children:
            connections.extend(child.get_connections())
        return connections

    @property
    def root(self):
        if self._root is None:
            if self.parents:
                for parent in self.parents:
                    return parent.root
        else:
            return self._root

    @root.setter
    def root(self, node):
        self._root = node

    def add_child(self, component: NodeComponent):
        if self.children is None:
            raise Exception(f"Component '{self.name}' cannot be parent component")
        if component.parents is None:
            raise Exception(f"Component {component.name} cannot be child component")
        if component not in self.root.components:
            self.root.components.append(component)
        if component in self.children:
            logger.warning(f"Component '{self.name}' is already child of component '{component.name}'")
        else:
            self.children.append(component)
        if self in component.parents:
            logger.warning(f"Component '{self.name}' is already parent of component '{component.name}'")
        else:
            component.parents.append(self)

    def remove_child(self, child: NodeComponent, abandon_children: bool = False):
        for i, c in enumerate(self.children):
            if c == child:
                self.children.pop(i)
                if abandon_children:
                    child.parents.remove(self)
                else:
                    for p in child.parents:
                        for _c in child.children:
                            p.children[p.children.index(child)] = _c

    def replace_child(self, old_child: NodeComponent, new_child: NodeComponent, abandon_children: bool = True):
        if old_child is None:
            raise Exception(f"Component to be replaced is not found")
        if new_child is None:
            raise Exception(f"Component to replace is not found")
        if old_child == new_child:
            logger.warning(f"Component '{old_child.name}' cannot be replaced by itself")
            return
        if old_child in self.children:
            for index, child in enumerate(self.children):
                if child == old_child:
                    # old_child.parents.remove(self)
                    if new_child not in self.children:
                        self.children[index] = new_child
                    if self not in new_child.parents:
                        new_child.parents.append(self)
                    if not abandon_children and old_child.children:
                        for c in old_child.children:
                            if c not in new_child.children:
                                new_child.children.append(c)
                            if new_child not in c.parents:
                                c.parents.append(new_child)
                    break
        else:
            logger.warning(f"Component '{old_child.name}' is not child of component '{self.name}'")

    def insert_child(self, component: NodeComponent):
        if self.children is None:
            raise Exception(f"Component '{self.name}' cannot be parent component")
        else:
            if self.children:
                for child in self.children:
                    child.parents[child.parents.index(self)] = component
                    component.children.append(child)
                    self.children.remove(child)
                self.children.append(component)
                component.parents.append(self)
            else:
                self.children.append(component)
                component.parents.append(self)

    def insert_one_child(self, component: NodeComponent):
        if self.children is None:
            raise Exception(f"Component '{self.name}' cannot be parent component")
        else:
            if self.children:
                for child in self.children[:1]:
                    child.parents[child.parents.index(self)] = component
                    component.children.append(child)
                    self.children.remove(child)
                self.children.append(component)
                component.parents.append(self)
            else:
                self.children.append(component)
                component.parents.append(self)

    def insert_before(self, component: NodeComponent):
        if self.parents is None:
            raise Exception(f"Component '{self.name}' cannot be child component")
        else:
            if self.parents:
                for parent in self.parents:
                    parent.children[parent.children.index(self)] = component
                    component.parents.append(parent)
                    self.parents.remove(parent)
                self.parents.append(component)
                component.children.append(self)
            else:
                self.parents.append(component)
                component.children.append(self)

    @property
    def parents(self) -> List[NodeComponent]:
        return self._parents

    @parents.setter
    def parents(self, parents):
        self._parents = parents


class PlainToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.enhanced_plain_to_document.EnhancedPlainToDocument')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})


class PDFToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.magic_pdf_to_document.MagicPDFToDocument')
        self.init_parameters = kwargs.get('init_parameters', {
            "image_process_types": [
                k for k, v in
                {'caption': kwargs.get('caption_enabled'), 'ocr': kwargs.get('ocr_enabled')}.items() if v
            ]
        })


class DOCXToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.enhanced_docx_to_document.EnhancedDOCXToDocument')
        self.init_parameters = kwargs.get('init_parameters', {
            "image_process_types": [
                k for k, v in
                {'caption': kwargs.get('caption_enabled'), 'ocr': kwargs.get('ocr_enabled')}.items() if v
            ]
        })


class PPTXToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.enhanced_pptx_to_document.EnhancedPPTXToDocument')
        self.init_parameters = kwargs.get('init_parameters', {
            "image_process_types": [
                k for k, v in
                {'caption': kwargs.get('caption_enabled'), 'ocr': kwargs.get('ocr_enabled')}.items() if v
            ]
        })


class ImageToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.image_to_document.ImageToDocument')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            "image_process_types": [
                k for k, v in
                {'caption': kwargs.get('caption_enabled'), 'ocr': kwargs.get('ocr_enabled')}.items() if v
            ]
        })


class FileRouterComponent(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.routers.file_type_router.FileTypeRouter')
        self.intro = kwargs.get('intro', 'FileTypeRouter')
        self.init_parameters = kwargs.get('init_parameters', {
            "additional_mimetypes": None,
            "mime_types": FILE_ROUTER_MIME_TYPES
        })


class DocumentJoiner(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.joiners.document_joiner.DocumentJoiner')
        self.init_parameters = kwargs.get('init_parameters', {
            "join_mode": "concatenate",
            "sort_by_score": True,
            "top_k": None,
            "weights": None
        })


class MetadataRouter(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.routers.metadata_router.MetadataRouter')
        self.init_parameters = kwargs.get('init_parameters', {
            "rules": {
                "image_caption": {
                    "operator": "AND",
                    "conditions": [
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "image"
                        },
                        {
                            "field": "meta.process_type",
                            "operator": "==",
                            "value": "caption"
                        }
                    ]
                },
                "image_ocr": {
                    "operator": "AND",
                    "conditions": [
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "image"
                        },
                        {
                            "field": "meta.process_type",
                            "operator": "==",
                            "value": "ocr"
                        }
                    ]
                },
                "text": {
                    "operator": "OR",
                    "conditions": [
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "text"
                        },
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "title"
                        },
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "audio"
                        },
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "video"
                        },
                        {
                            "field": "meta.content_type",
                            "operator": "==",
                            "value": "table"
                        }
                    ]
                }
            }
        })


class DocumentJoinerMate(NodeComponent):
    # _type_name = 'DocumentJoiner-Mate'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.joiners.document_joiner.DocumentJoiner')
        self.name = kwargs.get('name', 'DocumentJoiner-Mate')
        self.intro = kwargs.get('intro', 'DocumentJoiner')
        self.init_parameters = kwargs.get('init_parameters', {
            "join_mode": "concatenate",
            "sort_by_score": True,
            "top_k": None,
            "weights": None
        })


class ImageOCRToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.image_ocr_to_document.ImageOCRToDocument')
        self.init_parameters = kwargs.get('init_parameters', {
            "model": kwargs.get('ocr_model'),
            "tokenizer": kwargs.get('ocr_tokenizer')
        })


class ImageCaptionToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.image_caption_to_document.ImageCaptionToDocument')
        self.init_parameters = kwargs.get('init_parameters', {
            "language": kwargs.get('caption_language')
        })


class DocumentContentImageFiller(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.document_content_image_filler.DocumentContentImageFiller')


class DocumentWriter(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.writers.document_writer.DocumentWriter')
        self.init_parameters = kwargs.get('init_parameters', {
            "document_store": {
                "init_parameters": {
                    "connection_string": {
                        "env_vars": [
                            "DATABASE_SYNC_URI"
                        ],
                        "strict": True,
                        "type": "env_var"
                    },
                    "embedding_dimension": 1024,
                    "keyword_index_name": "haystack_keyword_index",
                    "recreate_table": True,
                    "table_name": "embedding_results",
                    "vector_function": "cosine_similarity"
                },
                "type": "byoa.integrations.document_stores.mo_document_store.MOIDocumentStore"
            },
            "policy": "NONE"
        })


class AudioToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.audio_to_document.AudioToDocument')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            'enable_noise_reduction': kwargs.get('enable_noise_reduction'),
            'enable_speaker_diarization': kwargs.get('enable_speaker_diarization'),
            'min_silence_duration': kwargs.get('min_silence_duration'),
            'max_segment_duration': kwargs.get('max_segment_duration'),
            'asr_model': kwargs.get('asr_model'),
            'audio_server_url': kwargs.get('audio_server_url')
        })


class VideoToDocument(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.converters.video_to_document.VideoToDocument')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            'enable_noise_reduction': kwargs.get('enable_noise_reduction'),
            'enable_speaker_diarization': kwargs.get('enable_speaker_diarization'),
            'min_silence_duration': kwargs.get('min_silence_duration'),
            'max_segment_duration': kwargs.get('max_segment_duration'),
            'asr_model': kwargs.get('asr_model'),
            'audio_server_url': kwargs.get('audio_server_url')
        })


class DocumentSplitter(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.enhance_document_splitter.EnhancedDocumentSplitter')
        self.extra_node_info = kwargs.get('extra_node_info', {
            'name': kwargs.get('node_name'),
            'description': kwargs.get('node_description'),
            'isCustomSplitSymbol': kwargs.get('is_custom_split_symbol'),
            'splitMode': kwargs.get('split_mode')
        })
        self.init_parameters = kwargs.get('init_parameters', {
            "custom_separators": kwargs.get('custom_separators'),
            "split_length": kwargs.get('split_length'),
            "split_overlap": kwargs.get('split_overlap'),
            "split_unit": kwargs.get('split_unit')
        })


class DocumentSplitterImageOCR(DocumentSplitter):
    # _type_name = 'DocumentSplitter-ImageOCR'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', 'DocumentSplitter-ImageOCR')
        self.intro = kwargs.get('intro', 'DocumentSplitter')


class DocumentSplitterImageCaption(DocumentSplitter):
    # _type_name = 'DocumentSplitter-ImageCaption'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', 'DocumentSplitter-ImageCaption')
        self.intro = kwargs.get('intro', 'DocumentSplitter')


class DocumentCleaner(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.cleaner.moi_document_cleaner.MoiDocumentCleaner')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            'deduplication_by_md5': kwargs.get('deduplication_by_md5'),
            'deduplication_by_similarity': kwargs.get('deduplication_by_similarity'),
            'deduplication_ngram_ratio': kwargs.get('deduplication_ngram_ratio'),
            'filter_special_char_ratio': kwargs.get('filter_special_char_ratio'),
            'remove_html_labels': kwargs.get('remove_html_labels'),
            'remove_invisible_char': kwargs.get('remove_invisible_char'),
            'remove_persional_message': kwargs.get('remove_persional_message'),
            'remove_sensitive_words': kwargs.get('remove_sensitive_words'),
            'remove_url': kwargs.get('remove_url'),
            'switch_deduplication': kwargs.get('switch_deduplication'),
            'switch_special_char_filter': kwargs.get('switch_special_char_filter'),
            'switch_special_char_remove': kwargs.get('switch_special_char_remove'),
            'switch_text_standardization': kwargs.get('switch_text_standardization'),
            'traditional_chinese_to_simple': kwargs.get('traditional_chinese_to_simple'),
            'unicode_normalization': kwargs.get('unicode_normalization')
        })


class DocumentCleanerImageOCR(DocumentCleaner):
    # _type_name = 'DocumentCleaner-ImageOCR'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', 'DocumentCleaner-ImageOCR')
        self.intro = kwargs.get('intro', 'DocumentCleaner')


class DocumentCleanerImageCaption(DocumentCleaner):
    # _type_name = 'DocumentCleaner-ImageCaption'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', 'DocumentCleaner-ImageCaption')
        self.intro = kwargs.get('intro', 'DocumentCleaner')


class DocumentEmbedder(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'haystack.components.embedders.openai_document_embedder.OpenAIDocumentEmbedder')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            "api_base_url": "https://api.siliconflow.cn/v1",
            "api_key": {
                "env_vars": [
                    "OPENAI_API_KEY"
                ],
                "strict": True,
                "type": "env_var"
            },
            "batch_size": 32,
            "dimensions": None,
            "embedding_separator": "\n",
            "meta_fields_to_embed": [],
            "model": kwargs.get('model'),
            "organization": None,
            "prefix": "",
            "progress_bar": True,
            "suffix": ""
        })


class DataAugmentation(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.data_augmentation.DataAugmentation')
        self.extra_node_info = kwargs.get('extra_node_info', {'name': kwargs.get('node_name'), 'description': kwargs.get('node_description')})
        self.init_parameters = kwargs.get('init_parameters', {
            "type": "general",
            "keyword_count": 5,
            "use_document_count": 30,
            "json_num_per_block": kwargs.get('samples_per_block'),
            "json_schema_type": kwargs.get('data_format'),
            "json_schema": kwargs.get('json_schema'),
            "style_prompt": ""
        })


class StructedExtraction(NodeComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = kwargs.get('type', 'byoa.integrations.components.structed_extraction.StructedExtraction')
        self.extra_node_info = kwargs.get('extra_node_info', {
            'name': kwargs.get('node_name'),
            'description': kwargs.get('node_description'),
            'extraction_template': kwargs.get('extraction_template')
        })
        self.init_parameters = kwargs.get('init_parameters', {
            "model": kwargs.get('model'),
            "json_schema": kwargs.get('json_schema'),
            "model_type": kwargs.get('model_type')
        })
