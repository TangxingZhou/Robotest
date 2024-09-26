import logging
from typing import List
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone, timedelta
from service.base import BaseAPI
from service.api import moc_api_request
from service.database.query_history.models import SQLType, SQLStatus

logger = logging.getLogger(__name__)


class DiagnoseAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/instances/{_id}', 'GET')
    def get_instance(self, _id):
        return None, [], {'_id': _id}

    @moc_api_request('/queries', 'POST', 'service.database.query_history.models.QueryHistory')
    def get_history(self,
                    _id,
                    query_type: List[SQLType] = None,
                    start_at='',
                    end_at='',
                    statement='',
                    duration: int = None,
                    databases: List[str] = None,
                    user='',
                    statement_id='',
                    session_id='',
                    not_executed_by_user: bool = False,
                    cu: int = 0,
                    order_by='request_at',
                    order='desc',
                    status: SQLStatus = None,
                    page=1,
                    page_size=20,
                    _last_hours: int = 2,
                    _timezone: int = 8):
        if start_at:
            if isinstance(start_at, str):
                datetime.strptime(start_at, '%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(start_at, datetime):
                start_at = start_at.astimezone(timezone(timedelta(hours=_timezone), 'UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
            else:
                raise ValueError(f"Invalid start_at: {start_at}, should be in format '%Y-%m-%dT%H:%M:%S%z' or datetime object.")
        else:
            start_at = (datetime.now() + relativedelta(hours=0 - _last_hours)).astimezone(
                timezone(timedelta(hours=_timezone), 'UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
        start_at = f'{start_at[:-2]}:{start_at[-2:]}'
        available_order_by_fields = (
            "duration",
            "request_at",
            "response_at",
            "rows_read",
            "bytes_scan",
            "cu"
        )
        if order_by not in available_order_by_fields:
            msg = f"Available options for order_by is: {', '.join(available_order_by_fields)}"
            logger.error(msg)
            raise Exception(msg)
        payload = {
            "instance_id": _id,
            "page": page,
            "page_size": page_size,
            "order": order,
            "order_by": [order_by],
            "start": start_at,
            "selected_field": [
                "statement",
                "statement_id",
                "duration",
                "status",
                "query_type",
                "request_at",
                "response_at",
                "user",
                "database",
                "transaction_id",
                "session_id",
                "rows_read",
                "bytes_scan",
                "result_count",
                "cu"
            ]
        }
        if query_type:
            payload.update(query_type=[t.value for t in query_type])
        if end_at:
            if isinstance(end_at, str):
                datetime.strptime(end_at, '%Y-%m-%dT%H:%M:%S%z')
            elif isinstance(end_at, datetime):
                end_at = end_at.astimezone(timezone(timedelta(hours=_timezone), 'UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
            else:
                raise ValueError(f"Invalid end_at: {end_at}, should be in format '%Y-%m-%dT%H:%M:%S%z' or datetime object.")
            payload.update(end=f'{end_at[:-2]}:{end_at[-2:]}')
        if statement:
            payload.update(statement=statement)
        if duration:
            payload.update(duration=duration * 1000000000)
        if databases:
            payload.update(databases=databases)
        if user:
            payload.update(user=[user])
        if statement_id:
            payload.update(statement_id=statement_id)
        if session_id:
            payload.update(session_id=session_id)
        if not not_executed_by_user:
            payload.update(sql_source_type=["cloud_user_sql", "external_sql"])
        if cu:
            payload.update(cu=cu)
        if status:
            payload.update(status=status.name)
        return payload
