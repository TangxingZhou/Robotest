import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone, timedelta
from service.base import BaseAPI
from service.api import moc_api_request
from service.database.query_history.models import *

logger = logging.getLogger(__name__)


class QueryHistoryAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/query/history', 'POST', 'service.database.query_history.models.QueryHistory')
    def get_history(self,
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
                    offset=0,
                    limit=20,
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
            msg = f"Available options for order_by are: {', '.join(available_order_by_fields)}"
            logger.error(msg)
            raise Exception(msg)
        payload = {
            "offset": offset,
            "limit": limit,
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

    @moc_api_request('/query/history', 'POST')
    def download_query_history(self, start_at='', _timezone: int = 8):
        if not start_at:
            start_at = (datetime.now() + relativedelta(minutes=-20)).astimezone(timezone(timedelta(hours=_timezone), 'UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
            start_at = f'{start_at[:-2]}:{start_at[-2:]}'
        payload = {
            "order": "desc",
            "order_by": ["request_at"],
            "sql_source_type": ["cloud_user_sql", "external_sql"],
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
            ],
            "offset": 0,
            "limit": 1000
        }
        return payload

    @moc_api_request('/query/detail', 'POST')
    def get_query_detail(self, statement_id, start_at, end_at):
        payload = {
            "statement_id": statement_id,
            "start": start_at,
            "end": end_at
        }
        return payload

    @moc_api_request('/query/result', 'POST')
    def get_query_result(sel, statement_id, offset=0, limit=1000):
        payload = {
            "offset": offset,
            "limit": limit,
            "statement_id": statement_id
        }
        return payload
    
    @moc_api_request('/query/result/download', 'POST')
    def download_query_result(sel, statement_id):
        payload = {
            "statement_id": statement_id
        }
        return payload

    @moc_api_request('/query/profile', 'POST')
    def get_query_profile(self, statement_id, start_at, end_at):
        payload = {
            "statement_id": statement_id,
            "start": start_at,
            "end": end_at
        }
        return payload
