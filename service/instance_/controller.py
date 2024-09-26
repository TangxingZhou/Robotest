import copy
import time
import allure
from service.api_client import APIClient
from service.base import BaseController
from service.instance_.api import *
from service.instance_.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class InstanceController(BaseController):
    _api_class = InstanceAPI

    def __init__(self, account=env.get_config('email'), api_client=None):
        super().__init__(account, api_client)
        self.account_info: AccountInfo = None

    @staticmethod
    def convert(**kwargs):
        if kwargs.get('plan_type') == PlanType.Serverless.value:
            return ServerlessInstance(**kwargs)
        elif kwargs.get('plan_type') == PlanType.Standard.value:
            return StandardInstance(**kwargs)
        else:
            return Instance(**kwargs)

    def is_in_status(self, _id, status: Status = None):
        instance_status = {}
        res = self.api.get_status()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        for ins in res['data']['statuses']:
            instance_status[ins['id']] = ins['status']
        if status is None:
            return _id not in instance_status
        else:
            if _id in instance_status:
                return instance_status[_id] == status.value
            else:
                return

    def wait_for_status(self, status: Status = None, timeout=0, interval=0, ignore_not_exists=False, *ids):
        if timeout == 0:
            time.sleep(1)
            return
        if status is None:
            logger.debug(f"Start to wait for instances {ids} to become absent.")
        else:
            logger.debug(f"Start to wait for status of instances {ids} to turn into {status.value}.")
        start, ids = time.time(), list(ids)
        while time.time() - start < timeout if timeout > 0 else True:
            _ids = copy.copy(ids)
            if _ids:
                for _id in _ids:
                    is_in = self.is_in_status(_id, status)
                    if is_in is None:
                        if ignore_not_exists:
                            logger.warning(f"Instance {_id} not found.")
                            ids.remove(_id)
                        else:
                            raise Exception(f"Instance {_id} not found.")
                    else:
                        if is_in:
                            ids.remove(_id)
                        else:
                            break
            else:
                return
            if status is None:
                logger.debug(f"Wait for instances {ids} to become absent.")
            else:
                logger.debug(f"Wait for status of instances {ids} to turn into {status.value}.")
            time.sleep(interval)
        if status is None:
            msg = f"Timeout for instance {ids} to become absent."
        else:
            msg = f"Timeout for instance {ids} to turn into {status.value}."
        raise Exception(msg)

    def create(self,
               name,
               password='Admin123',
               block_list=(),
               allow_list=('0.0.0.0/0',),
               payment: Payment = Payment.Free,
               _timeout: int = 5 * 60,
               **kwargs):
        res = self.api.create(name, password, block_list, allow_list, payment, **kwargs)
        err = APIError(**res)
        if err.is_ok():
            self.wait_for_status(Status.Active, _timeout, 5, False, res['data']['id'])
            return None, res['data']['id']
        else:
            return err, None

    @allure.step('查看实例状态')
    def get_status(self):
        res = self.api.get_status()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Instance(**res['data'])

    @allure.step('终止实例')
    def terminate(self, _id, _timeout: int = 0):
        logger.info(f"To terminate instance of '{_id}'")
        res = self.api.terminate(_id)
        err = APIError(**res)
        if err.is_ok():
            self.wait_for_status(Status.Terminated, _timeout, 5, False, _id)
        else:
            return err

    @allure.step('恢复实例')
    def recover(self, _id, name, _timeout: int = 5 * 60):
        res = self.api.recover(_id, name)
        err = APIError(**res)
        if err.is_ok():
            self.wait_for_status(Status.Active, _timeout, 5, False, res['data']['id'])
        else:
            return err

    @allure.step('等待实例删除')
    def is_deleted(self, _id, _timeout: int = 5 * 60):
        self.wait_for_status(None, _timeout, 5, False, _id)

    @allure.step('查看全部实例')
    def list(self):
        res = self.api.list()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [InstanceController.convert(**i) for i in res.get('data').get('instances')]

    @allure.step('查看可用实例')
    def list_available(self):
        res = self.api.list_available()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        # TODO: 过滤失效，待确认
        return [InstanceController.convert(**i) for i in res.get('data').get('instances') if i.get('status') in AvailableStatus._value2member_map_]

    @allure.step('查看终止实例')
    def list_terminated(self):
        res = self.api.list_terminated()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        # TODO: 过滤失效，待确认
        return [InstanceController.convert(**i) for i in res.get('data').get('instances') if i.get('status') in TerminatedStatus._value2member_map_]

    def filter(self, **kwargs):
        instances = self.list()
        for k, v in kwargs.items():
            instances = list(filter(lambda i: getattr(i, k) == v if hasattr(i, k) else False, instances))
        if instances:
            if len(instances) == 1:
                return instances[0]
            else:
                return instances
        else:
            return

    @allure.step('查看实例详情')
    def get_info(self, _id):
        res = self.api.get_info(_id)
        err = APIError(**res)
        if err.is_ok():
            return None, InstanceController.convert(**res.get('data'))
        else:
            return err, None

    @allure.step('获取价格配置')
    def get_configs(self):
        res = self.api.get_configs()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        # TODO: 获取配置及折扣
        provider_prices = [p.get('region_groups')[0]['regions'] for p in res['data']['providers']
                           if p.get('key') == self.provider and p.get('disabled') is False]
        if provider_prices:
            for region in provider_prices[0]:
                if region.get('key') == self.region and region.get('disabled') is False:
                    return PriceConfig(**region)

    @allure.step('查看免费CU和存储限额')
    def get_free_quota_usage(self):
        res = self.api.get_free_quota_usage()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return FreeQuota(**res.get('data'))

    @allure.step('查看账号详情')
    def get_account_info(self):
        res = self.api.get_account_info()
        assert res[0].get('code') == 'OK' and res[0].get('msg') == 'OK'
        self.account_info = AccountInfo(**res[0]['data'])

    @allure.step('修改实例的网络策略')
    def update_network_policy(self, _id, block_list=(), allow_list=('0.0.0.0/0',)):
        res = self.api.update_network_policy(_id, block_list, allow_list)
        err = APIError(**res)
        if not err.is_ok():
            return err
        # TODO: 网络策略无法立即生效，待测试
        time.sleep(10)

    @allure.step('重置实例密码')
    def reset_password(self, _id, password=os.getenv('INSTANCE_PASSWORD', 'Admin123')):
        res = self.api.reset_password(_id, password)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('重置实例名')
    def reset_name(self, _id, name):
        res = self.api.reset_name(_id, name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('获取实例的数据库管理平台登录信息')
    def get_db_platform_url(self, _id):
        res = self.api.get_db_platform_url(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']['url'], res['data']['account_name']

    @allure.step('登录实例的数据库管理平台')
    def login_db_platform(self, _id):
        # import threading
        # with APIClient.client_lock:
        #     if _id not in APIClient.clients:
        #         threading.Thread(target=APIClient.refresh_login_token, args=(APIClient.login_db_platform, 10 * 60, *self.get_db_platform_url(_id)), daemon=True).start()
        return APIClient.login_db_platform(*self.get_db_platform_url(_id))

    def refund(self, _id):
        pass

    def update(self):
        pass

    def clear(self):
        self.wait_for_status(Status.Terminated, 5 * 60, 5, True, *[ins.id for ins in self.list_available()])

    def _clear(self):
        instances = self.list_available()
        for ins in instances:
            if ins.plan_type == PlanType.Standard:
                if ins.charge_type == ChargeType.PrePaid:
                    self.refund(ins.id)
                else:
                    self.terminate(ins.id)
            elif ins.plan_type == PlanType.Serverless:
                self.terminate(ins.id)
        self.wait_for_status(Status.Terminated, 5 * 60, 5, False, *[ins.id for ins in instances])


class ServerlessInstanceController(InstanceController):
    _api_class = ServerlessAPI

    def __init__(self, account=env.get_config('email'), api_client=None):
        super().__init__(account, api_client)
        self.get_account_info()

    @allure.step('新建Serverless实例')
    def create(self,
               name,
               password='Admin123',
               block_list=(),
               allow_list=('0.0.0.0/0',),
               payment: Payment = Payment.Free,
               quota: dict = None,
               keep_serving: bool = None,
               _timeout: int = 5 * 60):
        res = self.api.create(name, password, block_list, allow_list, payment, quota, keep_serving)
        err = APIError(**res)
        if err.is_ok():
            self.wait_for_status(Status.Active, _timeout, 5, False, res['data']['id'])
            return None, res['data']['id']
        else:
            return err, None

    @allure.step('修改Serverless实例：免转付、spend limit、服务保持等')
    def update(self, _id, payment: Payment = None, quota: dict = None, keep_serving: bool = False):
        res = self.api.update(_id, payment, quota, keep_serving)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('插入CU使免费实例CU消耗超限')
    def inactive(self, _id):
        res = self.api.update(_id)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('终止全部Serverless实例')
    def clear(self):
        for ins in self.list_available():
            if ins.status in (Status.Terminating,):
                continue
            if ins.plan_type == PlanType.Serverless:
                self.terminate(ins.id)
        super().clear()


class StandardInstanceController(InstanceController):
    _api_class = StandardAPI

    def __init__(self, account=env.get_config('email'), api_client=None):
        super().__init__(account, api_client)
        self.get_account_info()

    @allure.step('新建Standard实例')
    def create(self,
               name,
               password='Admin123',
               block_list=(),
               allow_list=('0.0.0.0/0',),
               charge_type=ChargeType.PostPaid,
               capacity='c8m32',
               replicas: int = 1,
               pay_type: PayType = PayType.Voucher,
               pay_period=1,
               auto_pay_type: PayType = PayType.Voucher,
               auto_pay_period=0,
               _timeout: int = 20 * 60):
        res = self.api.create(name, password, block_list, allow_list, charge_type, capacity, replicas, pay_type,
                              pay_period, auto_pay_type, auto_pay_period)
        err = APIError(**res)
        if err.is_ok():
            self.wait_for_status(Status.Active, _timeout, 5, False, res['data']['id'])
            return None, res['data']['id']
        else:
            return err, None

    @allure.step('获取Standard实例新建金额')
    def get_expense(self, capacity, replicas: int = 1, period: int = None):
        res = self.api.get_expense(capacity, replicas, period)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Expense(**res['data'])

    @allure.step('获取Standard实例退订金额')
    def get_refund_amount(self, _id):
        res = self.api.get_refund_amount(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']['actual_payment_amount'], res['data']['consumed_amount'], res['data']['estimated_refund_amount']

    @allure.step('Standard实例退订')
    def refund(self, _id):
        res = self.api.refund(_id)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('获取Standard实例续费金额')
    def get_renew_expense(self, _id, charge_type=ChargeType.PostPaid, period=1, capacity=None, replicas: int = None):
        res = self.api.get_renew_expense(_id, charge_type, period, capacity, replicas)
        err = APIError(**res)
        if err.is_ok():
            return None, Expense(**res['data'])
        else:
            return err, None

    @allure.step('Standard实例续费')
    def renew(self,
              _id,
              pay_type: PayType = PayType.Voucher,
              pay_period=1,
              auto_pay_type: PayType = None):
        res = self.api.renew(_id, pay_type, pay_period, auto_pay_type)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('Standard实例修改自动续费：开关、周期、付费方式')
    def update_auto_renew(self, _id, auto_renew_period=1, auto_pay_type: PayType = PayType.Voucher):
        res = self.api.update_auto_renew(_id, auto_renew_period, auto_pay_type)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('Standard实例变配')
    def update_config(self, _id, capacity, replicas: int):
        res = self.api.update_config(_id, capacity, replicas)
        err = APIError(**res)
        if not err.is_ok():
            return err

    @allure.step('获取Standard实例变配金额')
    def get_update_expense(self, _id, capacity, replicas: int):
        res = self.api.get_update_expense(_id, capacity, replicas)
        err = APIError(**res)
        if err.is_ok():
            return None, UpdateConfigExpense(**res['data'])
        else:
            return err, None

    @allure.step('终止或退订全部Standard实例')
    def clear(self):
        for ins in self.list_available():
            if ins.status in (Status.Terminating,):
                continue
            if ins.plan_type == PlanType.Standard:
                if ins.charge_type == ChargeType.PrePaid:
                    self.refund(ins.id)
                else:
                    self.terminate(ins.id)
        super().clear()
