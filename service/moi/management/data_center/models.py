from service.models import *


class Volume(BaseModel):
    # _ignore_attrs = ('description', 'nodes')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children_count = kwargs.get('children_count', 0)
        self.created_at = kwargs.get('created_at', '')
        self.created_by =  kwargs.get('created_by', '')
        self.description = kwargs.get('description', '')
        self.id = kwargs.get('id', '')
        self.name = kwargs.get('name', '')
        self.reserved = kwargs.get('reserved', False)
        self.size = kwargs.get('size', 0)
        self.type = kwargs.get('type', 'volume')
        self.updated_at = kwargs.get('updated_at', '')
        self.updated_by = kwargs.get('updated_by', 'admin')
