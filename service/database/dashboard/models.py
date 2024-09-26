from enum import Enum


class MetricsType(Enum):
    QPS = 'QPS'
    TPS = 'TPS'
    QueryLatency = 'QueryLatency'
    TransactionTotalCount = 'TransactionTotalCount'
    TransactionErrorCount = 'TransactionErrorCount'
    StatementTotalCount = 'StatementTotalCount'
    StatementErrorCount = 'StatementErrorCount'


class MetricsAgg(Enum):
    AVG = 'avg'
    SUM = 'sum'
    MAX = 'max'
    MIN = 'min'
