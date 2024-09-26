import allure
import requests
from urllib.parse import unquote
from sqlalchemy import select
from service.utils import wait_for
from service.error import APIError
from service.base import BaseController
from service.database.query_history.api import *
from service.database.query_history.models import *
from service.cos.cluster import RootCluster
from service.mo.client import MOClient

logger = logging.getLogger(__name__)


class QueryHistoryController(BaseController):
    _api_class = QueryHistoryAPI

    def __init__(self, _id=None, api_client=None):
        super().__init__(_id, api_client)

    @property
    def instance_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Instance-Id')

    @wait_for(lambda r: r.total > 0, 2, 15)
    @allure.step('查看查询历史')
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
                    _timezone: int = 8,
                    _timeout: int = 15):
        res = self.api.get_history(query_type,
                                   start_at,
                                   end_at,
                                   statement,
                                   duration,
                                   databases,
                                   user,
                                   statement_id,
                                   session_id,
                                   not_executed_by_user,
                                   cu,
                                   order_by,
                                   order,
                                   status,
                                   offset,
                                   limit,
                                   _last_hours,
                                   _timezone)
        assert res.err is None
        return res
        # assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        # return QueryHistory(**res['data'])

    @staticmethod
    def query_statement_info(root_cluster: RootCluster,
                             instance_id: str,
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
        _whereclause = [StatementInfo.account == instance_id]
        if start_at:
            if isinstance(start_at, str):
                start_at = datetime.strptime(start_at, '%Y-%m-%d %H:%M:%S')
            elif isinstance(start_at, datetime):
                start_at = start_at.astimezone(timezone(timedelta(hours=0), 'UTC'))
            else:
                raise ValueError(f"Invalid start_at: {start_at}, should be in format '%Y-%m-%d %H:%M:%S' or datetime object.")
        else:
            start_at = datetime.now(timezone.utc) + relativedelta(hours=0 - _last_hours)
        _whereclause.append(StatementInfo.request_at >= start_at)
        if end_at:
            if isinstance(end_at, str):
                end_at = datetime.strptime(end_at, '%Y-%m-%d %H:%M:%S')
            elif isinstance(end_at, datetime):
                end_at = end_at.astimezone(timezone(timedelta(hours=0), 'UTC'))
            else:
                raise ValueError(f"Invalid start_at: {end_at}, should be in format '%Y-%m-%d %H:%M:%S' or datetime object.")
            _whereclause.append(StatementInfo.request_at < end_at)
        if query_type:
            _whereclause.append(StatementInfo.query_type.in_([t.value for t in query_type]))
        if statement:
            _whereclause.append(StatementInfo.statement.like(f'%{statement}%', escape='\\\\'))
        if duration:
            _whereclause.append(StatementInfo.duration >= duration * 1000000000)
        if databases:
            _whereclause.append(StatementInfo.database.in_(databases))
        if user:
            _whereclause.append(StatementInfo.user == user)
        if statement_id:
            _whereclause.append(StatementInfo.statement_id == statement_id)
        if session_id:
            _whereclause.append(StatementInfo.session_id == session_id)
        if not_executed_by_user:
            _whereclause.append(StatementInfo.sql_source_type.in_(['cloud_nouser_sql', 'internal_sql']))
        else:
            _whereclause.append(StatementInfo.sql_source_type.in_(['cloud_user_sql', 'external_sql']))
        if cu:
            _whereclause.append(StatementInfo.cu >= cu)
        if status:
            _whereclause.append(StatementInfo.status == status.value)
        available_order_by_fields = (
            "duration",
            "request_at",
            "response_at",
            "rows_read",
            "bytes_scan",
            "cu"
        )
        if order_by not in available_order_by_fields:
            msg = f"Invalid order_by: {order_by}, available options for order_by are: {', '.join(available_order_by_fields)}"
            logger.error(msg)
            raise Exception(msg)
        with MOClient(**root_cluster.mo).mo_session() as session:
            oder_by_clauses = [StatementInfo.__dict__[order_by].desc() if order == 'desc' else StatementInfo.__dict__[order_by].asc()]
            # if order_by != 'request_at':
            #     oder_by_clauses.append(StatementInfo.request_at.desc())
            return session.scalars(
                select(StatementInfo).where(*_whereclause).order_by(*oder_by_clauses).offset(offset).limit(limit)
            ).all()

    @allure.step('下载查询历史')
    def download_query_history(self, start_at='', _timezone: int = 8):
        res = self.api.download_query_history(start_at, _timezone)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        response = requests.get(res['data']['link'])
        assert response.status_code == 200
        file_path = unquote(res['data']['link'].split('?')[0].split('/')[3]).replace('/', '_')
        with open(file_path, 'wb') as file:
            file.write(response.content)
        allure.attach.file(file_path, file_path, allure.attachment_type.CSV)
        return file_path

    @allure.step('查看历史SQL记录详情')
    def get_query_detail(self, statement_id, start_at, end_at):
        res = self.api.get_query_detail(statement_id, start_at, end_at)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']

    @allure.step('查看历史SQL执行结果')
    def get_query_result(self, statement_id, offset=0, limit=1000):
        res = self.api.get_query_result(statement_id, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return QueryResult(**res['data'])

    @allure.step('下载历史SQL执行结果')
    def download_query_result(self, statement_id):
        res = self.api.download_query_result(statement_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        response = requests.get(res['data']['link'])
        assert response.status_code == 200
        file_path = unquote(res['data']['link'].split('?')[0].split('/')[3]).replace('/', '_')
        with open(file_path, 'wb') as file:
            file.write(response.content)
        allure.attach.file(file_path, file_path, allure.attachment_type.CSV)
        return file_path

    @allure.step('查看历史SQL执行分析')
    def get_query_profile(self, statement_id, start_at, end_at):
        res = self.api.get_query_profile(statement_id, start_at, end_at)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']
