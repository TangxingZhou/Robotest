import allure
from service.utils import wait_for
from service.base import BaseController
from service.admin.diagnose.api import *
from service.admin.diagnose.models import *
from service.admin.instance_.models import InstanceDetail
from service.database.query_history.models import QueryHistory
from service.error import APIError

logger = logging.getLogger(__name__)


class DiagnoseController(BaseController):
    _api_class = DiagnoseAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('查询实例')
    def get_instance(self, _id):
        res = self.api.get_instance(_id)
        err = APIError(**res)
        if err.is_ok():
            return None, InstanceDetail(**res['data'])
        else:
            return err, None

    @wait_for(lambda r: r.total > 0, 2, 15)
    @allure.step('查看实例查询历史')
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
                    _timezone: int = 8,
                    _timeout: int = 15):
        res = self.api.get_history(_id,
                                   query_type,
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
                                   page,
                                   page_size,
                                   _last_hours,
                                   _timezone)
        assert res.err is None
        return res
        # if res.err is None:
        #     return None, res
        # else:
        #     return res.err, None
        # assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        # return QueryHistory(**res['data'])
