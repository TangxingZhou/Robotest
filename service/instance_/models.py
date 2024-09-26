import os
import sys
import math
import subprocess
from datetime import datetime, timezone
from enum import Enum
import pymysql
from pymysql.cursors import Cursor
import jaydebeapi
from service.utils import objects_should_be_equal
from service.cos.cluster import MOClusterPhase
from service.mo.client import MOClient


class PlanType(Enum):
    Serverless = 'serverless'
    Standard = 'standard'


class ChargeType(Enum):
    PrePaid = 'prepaid'
    PostPaid = 'postpaid'
    Free = 'free'


class PayType(Enum):
    Voucher = 'voucher'
    Cash = 'cash'
    Customized = 'customized'


class Payment(Enum):
    Paid = 'paid'
    Free = 'free'


class AvailableStatus(Enum):
    Creating = 'CREATING'
    Active = 'ACTIVE'
    InActive = 'INACTIVE'
    Terminating = 'TERMINATING'
    Upgrading = 'UPGRADING'
    Insufficient_Balance = 'INSUFFICIENT_BALANCE'
    Exceeded_Spend_Limit_No_Serving = 'EXCEEDED_SPENDLIMIT_NOSERVING'
    Exceeded_CU_Quota = 'EXCEEDED_CU_QUOTA'
    Exceeded_Spend_Limit_Keep_Serving = 'EXCEEDED_SPENDLIMIT_KEEPSERVING'
    Exceeded_Storage_Quota = 'EXCEEDED_STORAGE_QUOTA'
    Updating_Capacity = 'UPDATING_CAPACITY'


class TerminatedStatus(Enum):
    Recovering = 'RECOVERING'
    Terminated = 'TERMINATED'


class Status(Enum):
    Creating = 'CREATING'
    Active = 'ACTIVE'
    InActive = 'INACTIVE'
    Terminating = 'TERMINATING'
    Upgrading = 'UPGRADING'
    Insufficient_Balance = 'INSUFFICIENT_BALANCE'
    Exceeded_Spend_Limit_No_Serving = 'EXCEEDED_SPENDLIMIT_NOSERVING'
    Exceeded_CU_Quota = 'EXCEEDED_CU_QUOTA'
    Exceeded_Spend_Limit_Keep_Serving = 'EXCEEDED_SPENDLIMIT_KEEPSERVING'
    Exceeded_Storage_Quota = 'EXCEEDED_STORAGE_QUOTA'
    Updating_Capacity = 'UPDATING_CAPACITY'
    Recovering = 'RECOVERING'
    Terminated = 'TERMINATED'
    Unknown = 'UNKNOWN'


class ChargeTypeMap(Enum):
    PostPaid = 1
    PrePaid = 2


class ServerlessPrice:

    def __init__(self, **kwargs):
        self.actual_price = kwargs.get('currency')
        self.currency = kwargs.get('currency')
        self.price = kwargs.get('currency')
        self.unit = kwargs.get('currency')


class PriceConfig:

    def __init__(self, **kwargs):
        self.currency = kwargs.get('currency')
        self.disabled = kwargs.get('disabled')
        self.free_quota_cu = kwargs.get('free_quota').get('cu')
        self.free_quota_storage = kwargs.get('free_quota').get('storage')
        self.serverless_cu_price = ServerlessPrice(**kwargs.get('serverless').get('cu'))
        self.serverless_storage_price = ServerlessPrice(**kwargs.get('serverless').get('storage'))
        self.standard = kwargs.get('standard')
        self.region_key = kwargs.get('key')
        self.region_text = kwargs.get('text')


class AccountInfo:

    def __init__(self, **kwargs):
        self.company = kwargs.get('company')
        self.email = kwargs.get('email')
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.login_method = kwargs.get('login_method')
        self.mobile_number = kwargs.get('mobile_number')
        self.organization = kwargs.get('organization')
        self.purpose = kwargs.get('purpose')
        self.register_method = kwargs.get('register_method')
        self.total_balance = kwargs.get('total_balance')
        self.type = kwargs.get('type')


class FreeQuota:

    def __init__(self, **kwargs):
        self.cu_quota = kwargs.get('quota').get('cu')
        self.storage_quota = kwargs.get('quota').get('storage')
        self.cu_usage = kwargs.get('usage').get('cu')
        self.storage_usage = kwargs.get('usage').get('storage')


class Instance:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.id = kwargs.get('id')
        self.plan_type: PlanType = PlanType(kwargs.get('plan_type')) if kwargs.get('plan_type') else None
        self.charge_type: ChargeType = ChargeType(kwargs.get('charge_type')) if kwargs.get('charge_type') else None
        self.payment: Payment = Payment(kwargs.get('payment')) if kwargs.get('payment') else None
        self.status: Status = Status(kwargs.get('status')) if kwargs.get('status') else None
        self.created_at = kwargs.get('created_at')
        self.terminated_at = kwargs.get('terminated_at', '')
        self.creator = kwargs.get('creator')
        self.version = kwargs.get('version')
        self.provider = kwargs.get('provider')
        self.region = kwargs.get('region')
        self.keep_serving: bool = kwargs.get('keep_serving', False)
        self.connections = kwargs.get('connections', [])
        self.network_policy = kwargs.get('network_policy', {})
        self.quota = kwargs.get('quota', {})
        self.usage = kwargs.get('usage', {})
        self.components = kwargs.get('components', {})
        self.prepaid = kwargs.get('prepaid', {})
        self.private_link_endpoint = kwargs.get('private_link_endpoint', {})

    def refresh(self, **kwargs):
        self.name = kwargs.get('name')
        self.id = kwargs.get('id')
        self.plan_type: PlanType = PlanType(kwargs.get('plan_type')) if kwargs.get('plan_type') else None
        self.charge_type: ChargeType = ChargeType(kwargs.get('charge_type')) if kwargs.get('plan_type') else None
        self.payment: Payment = Payment(kwargs.get('payment')) if kwargs.get('payment') else None
        self.status: Status = Status(kwargs.get('status')) if kwargs.get('status') else None
        self.created_at = kwargs.get('created_at')
        self.terminated_at = kwargs.get('terminated_at', '')
        self.creator = kwargs.get('creator')
        self.version = kwargs.get('version')
        self.provider = kwargs.get('provider')
        self.region = kwargs.get('region')
        self.keep_serving: bool = kwargs.get('keep_serving', False)
        self.connections = kwargs.get('connections', [])
        self.network_policy = kwargs.get('network_policy', {})
        self.quota = kwargs.get('quota', {})
        self.usage = kwargs.get('usage', {})
        self.components = kwargs.get('components', {})
        self.prepaid = kwargs.get('prepaid', {})
        self.private_link_endpoint = kwargs.get('private_link_endpoint', {})

    def get_connect_args(self, _type='PYTHON', password=os.getenv('INSTANCE_PASSWORD', 'Admin123')):
        for conn in self.connections:
            if conn['type'] == 'PYTHON' and _type.upper() == 'PYTHON':
                _connect_args = {}
                for _cmd in conn['command'].replace('<your_password>', password).split(', '):
                    _args = _cmd.split('=')
                    if _args[0] == 'port':
                        _connect_args[_args[0]] = int(_args[1])
                    else:
                        _connect_args[_args[0]] = _args[1].strip("'")
                return _connect_args
            elif conn['type'] == 'JDBC' and _type.upper() == 'JDBC':
                return conn['command'].replace('<your_password>', password).replace('<your_databases>', 'mysql')
            elif conn['type'] == 'MYSQL' and _type.upper() == 'MYSQL':
                return f"{conn['command']}{password} -e \"select version() as version;\""
            elif conn['type'] == 'GO' and _type.upper() == 'GO':
                _connect_args = conn['command'].replace('<your_password>', password).split('"')
                return f'{_connect_args[-2]}{_connect_args[1]}'

    def connect(self, _type='PYTHON', password=os.getenv('INSTANCE_PASSWORD', 'Admin123')):
        if _type.upper() == 'PYTHON':
            return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **self.get_connect_args('PYTHON', password))
        elif _type.upper() == 'JDBC':
            return jaydebeapi.connect(
                'com.mysql.cj.jdbc.Driver',
                self.get_connect_args('JDBC', password),
                None,
                f"src/data/JAR/mysql-connector-java-8.0.23.jar"
            )
        elif _type.upper() == 'MYSQL':
            return subprocess.run(self.get_connect_args('MYSQL', password), shell=True, capture_output=True, text=True)
        elif _type.upper() == 'GO':
            return subprocess.run([f'tool/bin/mo-go-connect-{sys.platform}', '-dns', f"{self.get_connect_args('GO', password)}"], shell=False, capture_output=True, text=True)

    def is_in_expected_status(self, status: Status):
        return self.status == status

    def is_terminated(self):
        return self.status == Status.Terminated.value

    @property
    def mo_client(self):
        return MOClient(**self.get_connect_args())

    @staticmethod
    def time_is_close(t1, t2, gap=1, _format='%Y-%m-%dT%H:%M:%SZ'):
        t1_stramp = datetime.strptime(t1, _format)
        t2_stramp = datetime.strptime(t2, _format)
        if t2_stramp > t1_stramp:
            _gap = t2_stramp - t1_stramp
        else:
            _gap = t1_stramp - t2_stramp
        if _gap.days > 0:
            return False
        else:
            return math.isclose(_gap.total_seconds(), 0, abs_tol=gap)

    @staticmethod
    def get_cluster_phase_from_instance_status(status: Status):
        if status == Status.Active:
            return MOClusterPhase.active
        elif status == Status.Exceeded_Spend_Limit_Keep_Serving:
            return MOClusterPhase.active
        elif status == Status.Exceeded_Spend_Limit_No_Serving:
            return MOClusterPhase.suspended
        elif status == Status.Exceeded_CU_Quota:
            return MOClusterPhase.suspended
        elif status == Status.Exceeded_Storage_Quota:
            return MOClusterPhase.restricted
        elif status == Status.Insufficient_Balance:
            return MOClusterPhase.suspended
        elif status == Status.Creating:
            return MOClusterPhase.pending, MOClusterPhase.creating
        elif status == Status.Upgrading:
            return MOClusterPhase.upgrading
        elif status == Status.Terminating:
            return MOClusterPhase.deleting
        elif status == Status.Recovering:
            return MOClusterPhase.hibernated
        elif status == Status.Terminated:
            return MOClusterPhase.hibernated
        elif status == Status.Updating_Capacity:
            return MOClusterPhase.active, MOClusterPhase.restricted, MOClusterPhase.suspended
        elif status == Status.InActive:
            return MOClusterPhase.restricted, MOClusterPhase.suspended
        elif status == Status.Unknown:
            return

    def __eq__(self, other):
        if isinstance(other, Instance):
            for attr in dir(self):
                if not attr.startswith('__') and not callable(getattr(self, attr)):
                    if not objects_should_be_equal(getattr(self, attr), getattr(other, attr)):
                        return False
            return True
        else:
            return False


class ServerlessInstance(Instance):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StandardInstance(Instance):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def auto_renew_enabled(self):
        return self.prepaid.get('auto_renew')

    @property
    def auto_pay_type(self):
        return PayType(self.prepaid.get('auto_pay_type'))

    @property
    def auto_renew_period(self):
        return self.prepaid.get('auto_renew_period')

    @property
    def begin_valid_at(self):
        if self.prepaid.get('begin_valid_at'):
            return datetime.strptime(self.prepaid.get('begin_valid_at'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%dT%H:%M:%SZ')

    @property
    def end_valid_at(self):
        return self.prepaid.get('end_valid_at')

    @property
    def period(self):
        return self.prepaid.get('period')

    @property
    def remain_days(self):
        return self.prepaid.get('remain_days')

    def get_remain_days(self):
        end_valid_at = datetime.strptime(self.end_valid_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        return (end_valid_at - datetime.now(timezone.utc)).days


class UpdateConfigExpense:

    def __init__(self, **kwargs):
        self.cash_balance = kwargs.get('cash_balance')
        self.voucher_balance = kwargs.get('voucher_balance')
        if kwargs.get('prepaid'):
            self.trade_amount = kwargs.get('prepaid').get('trade_amount')
        if kwargs.get('postpaid'):
            self.compute = kwargs.get('postpaid').get('compute')
            self.compute_last = kwargs.get('postpaid').get('compute_last')


class Expense:

    def __init__(self, **kwargs):
        self.cash_balance = float(kwargs.get('cash_balance'))
        self.voucher_balance = float(kwargs.get('voucher_balance'))
        self.expiration_time = float(kwargs.get('voucher_balance'))
        self.compute_discount = float(kwargs.get('compute').get('discount'))
        self.compute_discount_amount = float(kwargs.get('compute').get('discount_amount'))
        self.compute_original_amount = float(kwargs.get('compute').get('original_amount'))
        self.compute_original_price = float(kwargs.get('compute').get('original_price'))
        self.compute_trade_amount = float(kwargs.get('compute').get('trade_amount'))
        self.total_discount = float(kwargs.get('total').get('discount'))
        self.total_discount_amount = float(kwargs.get('total').get('discount_amount'))
        self.total_original_amount = float(kwargs.get('total').get('original_amount'))
        self.total_original_price = float(kwargs.get('total').get('original_price'))
        self.total_trade_amount = float(kwargs.get('total').get('trade_amount'))
