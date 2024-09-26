import allure
from service.base import BaseController
from service.admin.instance_.api import *
from service.admin.instance_.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class InstanceController(BaseController):
    _api_class = InstanceAPI

    def __init__(self, account='admin', api_client=None):
        super().__init__(account, api_client)

    @allure.step('查询实例')
    def get_instances(self,
                      _id=None,
                      name=None,
                      org_creator=None,
                      org_name=None,
                      payment: List[Payment] = None,
                      plan_charge_type: List[PlanChargeType] = None,
                      status: List[Status] = None,
                      page=1,
                      page_size=15):
        res = self.api.get_instances(_id, name, org_creator, org_name, payment, plan_charge_type, status, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return [Instance(**i) for i in res.get('data').get('instances')], res.get('data').get('total')

    @allure.step('修改实例')
    def update(self,
               _id,
               cu_limited_monthly: int = None,
               storage_limited: int = None,
               normal_max_cn: int = None,
               normal_min_cn: int = None,
               limited_max_cn: int = None,
               limited_min_cn: int = None,
               **kwargs):
        res = self.api.update(_id,
                              cu_limited_monthly,
                              storage_limited,
                              normal_max_cn,
                              normal_min_cn,
                              limited_max_cn,
                              limited_min_cn,
                              **kwargs)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"

    @allure.step('查看实例详情')
    def get_detail(self, _id):
        """
        This method seems deprecated and should be removed. Will be replaced by get_instance.
        """
        res = self.api.get_detail(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        return InstanceDetail(**res.get('data'))

    @allure.step('查看实例详情')
    def get_instance(self, _id):
        res = self.api.get_instance(_id)
        err = APIError(**res)
        if err.is_ok():
            return None, InstanceDetail(**res['data'])
        else:
            return err, None

    @allure.step('查看CU历月使用')
    def get_cu_logs(self, _id, _type='CUMonthly', page=1, page_size=100):
        res = self.api.get_cu_logs(_id, _type, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        # TODO: 待解析

    @allure.step('查看操作日志')
    def get_operation_logs(self, _id, _type='instance_', page=1, page_size=15):
        res = self.api.get_operation_logs(_id, _type, page, page_size)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('message')}"
        # TODO: 待解析
