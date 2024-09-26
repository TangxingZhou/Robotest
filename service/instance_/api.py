import logging
import requests
from fixture.internal.instance import env
from service.base import BaseAPI
from service.api import moc_api_request
from service.instance_.models import *

logger = logging.getLogger(__name__)


class InstanceAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)
        self.plan_type = PlanType.Serverless

    @moc_api_request('/CreateInstance', 'POST')
    def create(self,
               name,
               password='Admin123',
               block_list=(),
               allow_list=('0.0.0.0/0',),
               payment: Payment = Payment.Free,
               **kwargs):
        payload = {
            "name": name,
            "plan_type": self.plan_type.value,
            "provider": self.provider,
            "region": self.region,
            "payment": payment.value,
            "password": password,
            "network_policy": {
                "allow_list": list(allow_list), "block_list": list(block_list)
            }
        }
        for k, v in kwargs.items():
            if v is not None:
                payload[k] = v
        return payload

    @moc_api_request('/DescribeInstanceInfo', 'POST')
    def get_info(self, _id):
        payload = {'id': _id}
        return payload

    @moc_api_request('/DescribeInstances', 'POST')
    def list(self):
        payload = {
            'filters': [
                {
                    'name': 'status',
                    'values': [member.value for member in Status]
                }
            ]
        }
        return payload

    @moc_api_request('/DescribeInstances', 'POST', _request_timeout=20)
    def list_available(self):
        payload = {
            'filters': [
                {
                    'name': 'status',
                    'values': [member.value for member in AvailableStatus]
                }
            ]
        }
        return payload

    @moc_api_request('/DescribeInstances', 'POST')
    def list_terminated(self):
        payload = {
            'filters': [
                {
                    'name': 'status',
                    'values': [member.value for member in TerminatedStatus]
                }
            ]
        }
        return payload

    @moc_api_request('/DescribeInstanceStatus', 'POST')
    def get_status(self):
        return {}

    @moc_api_request('/TerminateInstance', 'POST')
    def terminate(self, _id):
        payload = {
            "id": _id
        }
        return payload

    @moc_api_request('/RecoverInstance', 'POST')
    def recover(self, _id, name):
        payload = {
            "id": _id,
            "name": name
        }
        return payload

    @moc_api_request('/DescribeClientIP', 'POST')
    def get_client_ip(self):
        return

    @moc_api_request('/UpdateInstance', 'POST')
    def update_network_policy(self,
                              _id,
                              block_list=(),
                              allow_list=()):
        payload = {
            "id": _id
        }
        if allow_list:
            payload["network_policy"] = {
                "allow_list": list(allow_list), "block_list": list(block_list)
            }
        return payload

    @moc_api_request('/instance_/password/reset', 'POST')
    def reset_password(self, _id, password):
        payload = {
            "instance_id": _id,
            'password': password
        }
        return payload

    @moc_api_request('/UpdateInstance', 'POST')
    def reset_name(self, _id, name):
        payload = {"id": _id, "name": name}
        return payload

    @moc_api_request('/DescribeDBPlatformURL', 'POST')
    def get_db_platform_url(self, instance_id):
        payload = {
            "id": instance_id
        }
        return payload

    @moc_api_request('/DescribeConfig', 'POST')
    def get_configs(self):
        return {}

    @moc_api_request('/DescribeAccountFreeQuotaUsage', 'POST')
    def get_free_quota_usage(self):
        return {}

    def get_account_info(self):
        res = requests.post(f"{env.get_config('auth_url')}/account/describe", json={}, headers=self.api_client.default_headers)
        return res.json(), res.status_code, res.headers


class ServerlessAPI(InstanceAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    def create(self,
               name,
               password='Admin123',
               block_list=(),
               allow_list=('0.0.0.0/0',),
               payment: Payment = Payment.Free,
               quota: dict = None,
               keep_serving: bool = None):
        return super().create(name, password, block_list, allow_list, payment, quota=quota, keep_serving=keep_serving)

    @moc_api_request('/UpdateInstance', 'POST')
    def update(self, _id, payment: Payment = None, quota: dict = None, keep_serving: bool = False):
        payload = {
            "id": _id,
            "quota": quota,
            "keep_serving": keep_serving
        }
        if payment is not None:
            payload["payment"] = payment.value
        if quota is None:
            payload["quota"] = {}
        return payload

    @moc_api_request('/InactiveInstance', 'POST')
    def inactive(self, _id):
        return {"id": _id}


class StandardAPI(InstanceAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)
        self.plan_type = PlanType.Standard
        self.payment = Payment.Paid

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
               **kwargs):
        if charge_type == ChargeType.PrePaid:
            if auto_pay_period < 1:
                prepaid = {"period": pay_period, "auto_renew": False, "pay_type": pay_type.value},
            else:
                prepaid = {"period": pay_period, "auto_renew": True, "pay_type": pay_type.value, "auto_pay_type": auto_pay_type.value}
        else:
            prepaid = None
        if not (0 < replicas <= 10):
            raise ValueError("replicas should be >0 and <=10")
        components = {"cn": {"capacity": capacity, "replicas": replicas}}
        return super().create(name, password, block_list, allow_list, Payment.Paid, charge_type=charge_type.value,
                              components=components, prepaid=prepaid)

    @moc_api_request('/DescribeInstanceExpense', 'POST')
    def get_expense(self, capacity, replicas: int = 1, period: int = None):
        if not (0 < replicas <= 10):
            raise ValueError("replicas should be >0 and <=10")
        payload = {
            "plan_type": self.plan_type.value,
            "provider": self.provider,
            "region": self.region,
            "components": {
                "cn": {
                    "capacity": capacity,
                    "replicas": replicas
                }
            }
        }
        if period is None:
            payload.update(charge_type=ChargeType.PostPaid.value)
        else:
            payload.update(charge_type=ChargeType.PrePaid.value, period=period)
        return payload

    @moc_api_request('/DescribeRefundAmount', 'POST')
    def get_refund_amount(self, _id):
        payload = {
            "id": _id
        }
        return payload

    @moc_api_request('/RefundInstance', 'POST')
    def refund(self, _id):
        payload = {
            "id": _id
        }
        return payload

    @moc_api_request('/DescribeRenewExpense', 'POST')
    def get_renew_expense(self, _id, charge_type=ChargeType.PostPaid, period=1, capacity=None, replicas: int = None):
        if capacity is None or replicas is None:
            payload = {
                "id": _id,
                "period": period
            }
        else:
            if not (0 < replicas <= 10):
                raise ValueError("replicas should be >0 and <=10")
            payload = {
                "id": _id,
                "period": period,
                "components": {"cn": {"capacity": "c8m32", "replicas": replicas}},
                "plan_type": self.plan_type.value,
                "provider": self.provider,
                "region": self.region,
                "charge_type": charge_type.value
            }
        return payload

    @moc_api_request('/RenewInstance', 'POST')
    def renew(self,
              _id,
              pay_type: PayType = PayType.Voucher,
              pay_period=1,
              auto_pay_type: PayType = None):
        if auto_pay_type is None:
            prepaid = {
                "period": pay_period,
                "auto_renew": False,
                "pay_type": pay_type.value
            }
        else:
            prepaid = {
                "period": pay_period,
                "auto_renew": True,
                "pay_type": pay_type.value,
                "auto_pay_type": auto_pay_type.value
            }
        payload = {
            "id": _id,
            "prepaid": prepaid
        }
        return payload

    @moc_api_request('/UpdateInstanceAutoRenew', 'POST')
    def update_auto_renew(self, _id, auto_renew_period=1, auto_pay_type: PayType = PayType.Voucher):
        if auto_renew_period < 1:
            payload = {
                "id": _id,
                "auto_renew": False
            }
        else:
            payload = {
                "id": _id,
                "auto_renew": True,
                "auto_renew_period": auto_renew_period,
                "auto_pay_type": auto_pay_type.value
            }
        return payload

    @moc_api_request('/UpdateInstanceConfig', 'POST')
    def update_config(self, _id, capacity, replicas: int):
        if not (0 < replicas <= 10):
            raise ValueError("replicas should be >0 and <=10")
        payload = {
            "id": _id,
            "components": {"cn": {"capacity": capacity, "replicas": replicas}}
        }
        return payload

    @moc_api_request('/GetInstanceUpdateExpense', 'POST')
    def get_update_expense(self, _id, capacity, replicas: int):
        if not (0 < replicas <= 10):
            raise ValueError("replicas should be >0 and <=10")
        payload = {
            "id": _id,
            "components":
                {"cn": {"capacity": capacity, "replicas": replicas}}
        }
        return payload
