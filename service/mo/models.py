import pprint
from datetime import datetime
from dateutil.tz import tzutc
from decimal import Decimal
from sqlalchemy import func, VARCHAR, DECIMAL, TEXT, DATETIME, BIGINT, FLOAT
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import Mapped, mapped_column, column_property
from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.ext.hybrid import hybrid_property


class MOBase(DeclarativeBase):
    pass


class CU(MOBase):
    __table_args__ = {'schema': 'mo_cloud'}
    __tablename__ = 'cu'

    account: Mapped[str] = mapped_column(VARCHAR(128), primary_key=True)
    type: Mapped[str] = mapped_column(VARCHAR(191), primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DATETIME, primary_key=True)
    end_time: Mapped[datetime] = mapped_column(DATETIME)
    cu: Mapped[Decimal] = mapped_column(DECIMAL(23))
    network: Mapped[Decimal] = mapped_column(DECIMAL(23))
    object_in_api: Mapped[Decimal] = mapped_column(DECIMAL(23))
    object_out_api: Mapped[Decimal] = mapped_column(DECIMAL(23))


class StatementInfo(MOBase):
    __table_args__ = {'schema': 'system'}
    __tablename__ = 'statement_info'

    account: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='account name')
    user: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='user name')
    host: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='user client ip')
    database: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='what database current session stay in.')
    node_type: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='node type in MO, val in [DN, CN, LOG]')
    node_uuid: Mapped[str] = mapped_column(VARCHAR(36), nullable=False, default=None, comment='node uuid, which node gen this data.')
    status: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='sql statement running status, enum: Running, Success, Failed')
    err_code: Mapped[str] = mapped_column(VARCHAR(1024), nullable=True, default='0', comment='error code info')
    statement_type: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='statement type, val in [Insert, Delete, Update, Drop Table, Drop User, ...]')
    query_type: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, default=None, comment='query type, val in [DQL, DDL, DML, DCL, TCL]')
    statement_id: Mapped[str] = mapped_column(VARCHAR(36), primary_key=True, nullable=False, default=None, comment='statement uniq id')
    transaction_id: Mapped[str] = mapped_column(VARCHAR(36), nullable=False, default=None, comment='txn uniq id')
    session_id: Mapped[str] = mapped_column(VARCHAR(36), nullable=False, default=None, comment='session uniq id')
    statement: Mapped[str] = mapped_column(TEXT, nullable=False, default=None, comment='sql statement')
    statement_tag: Mapped[str] = mapped_column(TEXT, nullable=False, default=None, comment='note tag in statement(Reserved)')
    statement_fingerprint: Mapped[str] = mapped_column(TEXT, nullable=False, default=None, comment='note tag in statement(Reserved)')
    error: Mapped[str] = mapped_column(TEXT, nullable=False, default=None, comment='error message')
    exec_plan: Mapped[str] = mapped_column(TEXT, nullable=True, default='{}', comment='statement execution plan')
    stats: Mapped[str] = mapped_column(TEXT, nullable=True, default='[]', comment='global stats info in exec_plan')
    sql_source_type: Mapped[str] = mapped_column(TEXT, nullable=False, default=None, comment='sql statement source type')
    request_at: Mapped[datetime] = mapped_column(DATETIME(timezone=True), nullable=False, default=None, comment='request accept datetime')
    response_at: Mapped[datetime] = mapped_column(DATETIME(timezone=True), nullable=False, default=None, comment='response send datetime')
    rows_read: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='rows read total')
    bytes_scan: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='bytes scan total')
    role_id: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='role id')
    aggr_count: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='the number of statements aggregated')
    result_count: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='the number of rows of sql execution results')
    duration: Mapped[int] = mapped_column(BIGINT, nullable=True, default=0, comment='exec time, unit: ns')
    cu = column_property(cast(func.substring(
        func.regexp_substr(stats, '[0-9\.]+]'), 1, func.length(func.regexp_substr(stats, '[0-9\.]+]')) - 1), FLOAT))

    # @hybrid_property
    # def cu(self):
    #     return eval(self.stats)[-1]
    #
    # @cu.expression
    # def cu(cls):
    #     return cast(func.substring(func.regexp_substr(cls.stats, '[0-9\.]+]'), 1,
    #                                func.length(func.regexp_substr(cls.stats, '[0-9\.]+]')) - 1), FLOAT)

    @property
    def _request_at(self):
        return self.request_at.replace(tzinfo=tzutc())

    @property
    def _response_at(self):
        return self.response_at.replace(tzinfo=tzutc())

    def to_dict(self):
        result = {}
        for attr in self.__dir__():
            if not attr.startswith('_') and not callable(getattr(self, attr)) and attr not in ('metadata', 'registry'):
                if isinstance(getattr(self, attr), datetime):
                    if getattr(self, attr).tzinfo is None:
                        result[attr] = getattr(self, attr).replace(tzinfo=tzutc())
                else:
                    result[attr] = getattr(self, attr)
        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()
