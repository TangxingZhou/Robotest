from enum import Enum

class SQLType(Enum):
    Other = 'Other'
    DQL = 'DQL'
    DDL = 'DDL'
    DML = 'DML'
    DCL = 'DCL'
    TCL = 'TCL'


class InstanceInfo:

    def __init__(self, **kwargs):
        self.ID = kwargs.get('ID')
        self.account_name = kwargs.get('account_name')
        self.connections = kwargs.get('connections')
        self.created_at = kwargs.get('created_at')
        self.created_by = kwargs.get('created_by')
        self.db_count = kwargs.get('db_count')
        self.name = kwargs.get('name')
        self.network_policy = kwargs.get('network_policy')
        self.organization = kwargs.get('organization')
        self.plan_type = kwargs.get('plan_type')
        self.provider = kwargs.get('provider')
        self.quota = kwargs.get('quota')
        self.region = kwargs.get('region')
        self.usage = kwargs.get('usage')
        self.version = kwargs.get('version')
