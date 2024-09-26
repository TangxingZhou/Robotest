
class DBInfo:

    def __init__(self, **kwargs):
        self.created = kwargs.get('created')
        self.has_published: bool = kwargs.get('has_published')
        self.is_internal: bool = kwargs.get('is_internal')
        self.is_subscription: bool = kwargs.get('is_subscription')
        self.name = kwargs.get('name')
        self.owner = kwargs.get('owner')
        self.size: int = kwargs.get('size')
        self.tables: int = kwargs.get('tables')


class DBTable:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.owner = kwargs.get('owner')
        self.created = kwargs.get('owner')
        self.kind = kwargs.get('owner')
        self.rows: int = kwargs.get('owner')
        self.size: int = kwargs.get('owner')


class DB:

    def __init__(self, **kwargs):
        self.db_name = kwargs.get('db_name')
        self.db_owner = kwargs.get('db_owner')
        self.has_published: bool = kwargs.get('has_published')
        self.is_internal: bool = kwargs.get('is_internal')
        self.is_subscription: bool = kwargs.get('is_subscription')
        self.tables = [DBTable(**t) for t in kwargs.get('tables', {}).get('tables', [])]
        self.views = [DBTable(**t) for t in kwargs.get('views', {}).get('tables', [])]


class PublicationTargetInstances:

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')


class Publication:

    def __init__(self, **kwargs):
        self.created_at = kwargs.get('created_at')
        self.database = kwargs.get('database')
        self.instance_id = kwargs.get('instance_id')
        self.instance_name = kwargs.get('instance_name')
        self.permission = kwargs.get('permission')
        self.pub_name = kwargs.get('pub_name')
        self.target_instances = [PublicationTargetInstances(**i) for i in kwargs.get('target_instances', [])]
        self.updated_at = kwargs.get('updated_at')

    @property
    def _target_instances_id(self):
        return [i.id for i in self.target_instances]


class Subscription:

    def __init__(self, **kwargs):
        self.created_at = kwargs.get('created_at')
        self.database = kwargs.get('database')
        self.instance_id = kwargs.get('instance_id')
        self.permission = kwargs.get('permission')
        self.pub_name = kwargs.get('pub_name')


class DBColumn:
    
    def __init__(self, **kwargs):
        self.data_type = kwargs.get('data_type')
        self.default_value = kwargs.get('default_value')
        self.key_type = kwargs.get('key_type')
        self.name = kwargs.get('name')
        self.nullable = kwargs.get('nullable')


class DBColumnStat:
    
    def __init__(self, **kwargs):
        self.data_type = kwargs.get('data_type')
        self.maximum = kwargs.get('maximum')
        self.minimum = kwargs.get('minimum')
        self.name = kwargs.get('name')
