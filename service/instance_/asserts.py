import re
import allure
from pymysql.err import OperationalError as PyMsqlOperationalError
from jaydebeapi import OperationalError as JDBCOperationalError
from dateutil.relativedelta import relativedelta
from cloud.k8s.client import K8sClient
from service.instance_.api import *
from service.instance_.models import *
from service.cos.provider import ProviderProfile
from service.cos.cluster import Cluster, MOClusterType, MOClusterPhase
from service.admin.instance_.consts import *


class InstanceAssertion:

    def __init__(self, k8s_client: K8sClient, instance: Instance = None):
        self._k8s_client = k8s_client
        if instance:
            self.instance = instance

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, instance: Instance):
        self.cluster = Cluster(self._k8s_client, instance.id)
        self._instance = instance

    def check_asserts_for_creation(self,
                                   name,
                                   account_info: AccountInfo,
                                   created_at,
                                   plan_type: PlanType,
                                   charge_type: ChargeType):
        self.assert_name(name)
        self.assert_in_active_status()
        self.assert_organization(account_info)
        self.assert_creator(account_info)
        self.assert_plan_type(plan_type)
        self.assert_charge_type(charge_type)
        self.assert_mo_version()
        self.assert_ip_white_list()
        self.assert_cloud_provider_and_region()
        self.assert_creation_time(created_at)
        self.assert_terminate_time('')
        self.assert_to_connect_mysql_client()
        self.assert_to_connect_jdbc_client()
        self.assert_to_connect_python_client()
        self.assert_to_connect_go_client()
        # self.assert_rpivate_link_endpoint()

    @allure.step('验证实例名和account_id')
    def assert_name(self, name):
        assert self.instance.name == name
        if self.cluster.id_is_account_name:
            assert self.cluster.account_id == self.instance.id
        else:
            assert self.cluster.account_id == self.instance.id.replace('-', '_')

    @allure.step('验证实例状态')
    def assert_in_active_status(self):
        assert self.instance.status == Status.Active
        assert self.cluster.phase == MOClusterPhase.active

    @allure.step('验证实例类型')
    def assert_plan_type(self, plan_type: PlanType):
        assert self.instance.plan_type == plan_type
        assert self.cluster.plan_type == plan_type.value
        assert self.cluster.cluster_type == 'account'

    @allure.step('验证实例付费类型')
    def assert_charge_type(self, plan_type: PlanType, charge_type: ChargeType):
        assert self.instance.charge_type == charge_type
        if plan_type == PlanType.Standard:
            assert self.instance.payment == Payment.Paid
            if charge_type == ChargeType.PrePaid:
                assert self.cluster.type == MOClusterType.standard_prepaid
            elif charge_type == ChargeType.PostPaid:
                assert self.cluster.type == MOClusterType.standard_postpaid
        elif plan_type == PlanType.Serverless:
            if charge_type == ChargeType.Free:
                assert self.instance.payment == Payment.Free
                assert self.cluster.type == MOClusterType.serverless_free
            elif charge_type == ChargeType.PostPaid:
                assert self.instance.payment == Payment.Paid
                assert self.cluster.type == MOClusterType.serverless_paid

    @allure.step('检查实例组织ID')
    def assert_organization(self, account_info: AccountInfo):
        assert self.cluster.organization == account_info.organization

    @allure.step('检查实例创建者')
    def assert_creator(self, account_info: AccountInfo):
        assert self.instance.creator == f'{account_info.firstname} {account_info.lastname}'

    @allure.step('检查实例版本')
    def assert_mo_version(self):
        assert self.instance.version == self.cluster.version

    @allure.step('检查实例白名单')
    def assert_ip_white_list(self):
        assert self.instance.network_policy.get('allow_list') == self.cluster.ip_white_list

    @allure.step('检查实例云供应商和地区')
    def assert_cloud_provider_and_region(self, provider=env.get_config('provider'), region=env.get_config('region')):
        assert self.instance.prepaid == provider
        assert self.instance.region == region
        assert self.cluster.cn_unit == (provider, region)

    @allure.step('检查实例创建时间')
    def assert_creation_time(self, created_at):
        assert Instance.time_is_close(created_at, self.instance.created_at)
        if hasattr(self.instance, 'begin_valid_at') and self.instance.begin_valid_at:
            assert self.instance.begin_valid_at == self.instance.created_at
        assert Instance.time_is_close(self.cluster.creation_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'), self.instance.created_at)

    @allure.step('检查实例终止时间')
    def assert_terminate_time(self, terminated_at):
        if terminated_at:
            assert Instance.time_is_close(terminated_at, self.instance.terminated_at)
        else:
            assert self.instance.terminated_at == ''

    def assert_to_connect_clients(self, err_msg=''):
        self.assert_to_connect_mysql_client(err_msg)
        # self.assert_to_connect_jdbc_client(err_msg)
        self.assert_to_connect_python_client(err_msg)
        self.assert_to_connect_go_client(err_msg)

    @allure.step('验证Mysql客户端连接')
    def assert_to_connect_mysql_client(self, err_msg=''):
        connect_args = self.instance.get_connect_args('mysql')
        assert f'-h {self.cluster.cluster.status.endpoint.address}' in connect_args
        assert f'-P {self.cluster.cluster.status.endpoint.port}' in connect_args
        assert f'-u {self.cluster.account_id}:admin:accountadmin' in connect_args
        mysql_result = self.instance.connect('mysql')
        # with allure.step(f"{connect_args}"):
        #     pass
        allure.attach(f'{connect_args}', 'mysql cli', allure.attachment_type.TEXT)
        if err_msg:
            assert mysql_result.returncode != 0 and mysql_result.stdout == '' and re.search(re.compile(err_msg), mysql_result.stderr) is not None
        else:
            assert mysql_result.returncode == 0 and mysql_result.stdout.strip()[8:] == self.instance.version

    @allure.step('验证JDBC客户端连接')
    def assert_to_connect_jdbc_client(self, err_msg=''):
        connect_args = self.instance.get_connect_args('jdbc')
        assert f'{self.cluster.cluster.status.endpoint.address}:{self.cluster.cluster.status.endpoint.port}' in connect_args
        assert f'user={self.cluster.account_id}:admin:accountadmin' in connect_args
        try:
            with self.instance.connect('jdbc').cursor() as cursor:
                cursor.execute('select version() as version;')
                assert cursor.fetchone().get('version') == self.instance.version
        except JDBCOperationalError as e:
            logger.debug(e)
            if err_msg:
                assert re.search(re.compile(err_msg), e.args[1]) is not None
            else:
                raise e

    @allure.step('验证Python客户端连接')
    def assert_to_connect_python_client(self, err_msg=''):
        connect_args = self.instance.get_connect_args('python')
        assert connect_args['host'] == self.cluster.cluster.status.endpoint.address
        assert connect_args['port'] == self.cluster.cluster.status.endpoint.port
        assert connect_args['user'] == f'{self.cluster.account_id}:admin:accountadmin'
        try:
            with self.instance.connect('python').cursor() as cursor:
                cursor.execute('select version() as version;')
                assert cursor.fetchone().get('version') == self.instance.version
        except PyMsqlOperationalError as e:
            logger.debug(e)
            if err_msg:
                assert re.search(re.compile(err_msg), e.args[1]) is not None
            else:
                raise e

    @allure.step('验证GO客户端连接')
    def assert_to_connect_go_client(self, err_msg=''):
        connect_args = self.instance.get_connect_args('go')
        assert f'{self.cluster.cluster.status.endpoint.address}:{self.cluster.cluster.status.endpoint.port}' in connect_args
        assert f'{self.cluster.account_id}#admin#accountadmin' in connect_args
        go_result = self.instance.connect('go')
        if err_msg:
            assert go_result.returncode != 0 and re.search(re.compile(err_msg), go_result.stderr) is not None
        else:
            assert go_result.returncode == 0 and go_result.stderr == ''
            for v in re.findall(r'Version of matrixone is (.*)\.', go_result.stdout.strip()):
                assert v == self.instance.version

    @allure.step('验证私网连接信息')
    def assert_rpivate_link_endpoint(self):
        assert self.instance.private_link_endpoint.get('service_name') == self.cluster.cluster.status.aliyun_status.private_link.service_name
        assert sorted(self.instance.private_link_endpoint.get('zones')) == sorted(self.cluster.cluster.status.aliyun_status.private_link.zones)


class ServerlessInstanceAssertion(InstanceAssertion):

    def __init__(self, k8s_client: K8sClient, instance: StandardInstance = None):
        super().__init__(k8s_client, instance)

    @allure.step('验证实例的免费CU和存储限额')
    def assert_free_quota(self):
        assert self.instance.quota.get('cu') == SERVERLESS_FREE_INSTANCE_DEFAULT_QUOTA.get('cu')
        assert self.instance.quota.get('storage') == SERVERLESS_FREE_INSTANCE_DEFAULT_QUOTA.get('storage')

    @allure.step('验证实例的CU和存储使用量')
    def assert_cu_and_storage_usage(self, cu, storage: int):
        assert self.instance.usage.get('cu') == cu
        assert self.instance.usage.get('storage') == storage

    @allure.step('验证实例的/日、/月消费限额')
    def assert_production_quota(self, daily: int = None, monthly: int = None, unit='rmb'):
        self.assert_free_quota()
        assert self.instance.quota.get('daily') == daily
        assert self.instance.quota.get('monthly') == monthly
        assert self.instance.quota.get('unit') == unit

    @allure.step('验证实例的/日、/月消费额')
    def assert_production_usage(self, cu, storage: int, daily_expense, monthly_expense, before_convert_cu=None, unit='rmb'):
        self.assert_cu_and_storage_usage(cu, storage)
        assert self.instance.usage.get('daily_expense') == daily_expense
        assert self.instance.usage.get('monthly_expense') == monthly_expense
        assert self.instance.usage.get('before_convert_cu') == before_convert_cu
        assert self.instance.usage.get('unit') == unit
    

class StandardInstanceAssertion(InstanceAssertion):

    def __init__(self, k8s_client: K8sClient, instance: StandardInstance = None):
        super().__init__(k8s_client, instance)

    def check_asserts_for_creation(self,
                                   name,
                                   account_info: AccountInfo,
                                   created_at,
                                   plan_type: PlanType,
                                   charge_type: ChargeType,
                                   capacity,
                                   replicas,
                                   profile: ProviderProfile,
                                   period=1,
                                   auto_renew_period=0):
        super().check_asserts_for_creation(name, account_info, created_at, plan_type, charge_type)
        self.assert_capacity(capacity)
        self.assert_replicas(replicas)
        self.assert_profile(profile)
        self.assert_resources(profile)
        self.assert_storage(profile)
        self.assert_host_node_instance_type(profile)
        self.assert_expiration_date(period)
        self.assert_remain_days()
        self.assert_auto_renew(auto_renew_period)

    @staticmethod
    @allure.step('检查价格明细')
    def assert_expense(expense, compute_prices, replicas):
        assert compute_prices.price == expense.compute_original_price
        assert compute_prices.discount == expense.compute_discount
        assert expense.compute_original_price * replicas == expense.compute_original_amount
        assert expense.compute_original_price * replicas * expense.compute_discount == expense.compute_trade_amount
        assert expense.compute_original_amount - expense.compute_trade_amount == expense.compute_discount_amount
        assert expense.compute_original_amount == expense.total_original_amount
        assert expense.compute_trade_amount == expense.total_trade_amount
        assert expense.compute_discount_amount == expense.total_discount_amount

    @allure.step('检查实例规格')
    def assert_capacity(self, capacity):
        assert self.instance.components.get('cn').get('capacity') == capacity
        # assert self.cluster.cn_profile == f'cn.{capacity}'
        # assert self.cluster.cn_profile == 'cn.profileForTest'
        # assert self.cluster.cn_profile == profile.name

    @allure.step('检查实例profile')
    def assert_profile(self, profile: ProviderProfile):
        # profile = self._provider_profiles.get_profile_by_name(f'cn.{capacity}')
        # profile = self._provider_profiles.get_profile_by_name(f'cn.profileForTest')
        assert self.cluster.cn_profile == profile.name

    @allure.step('检查实例资源使用情况：CN副本数')
    def assert_replicas(self, replicas):
        assert self.cluster.cn_replicas == replicas
        assert len(self.cluster.get_cn_pods()) == replicas

    @allure.step('检查实例资源使用情况：CPU, Mem')
    def assert_resources(self, profile: ProviderProfile):
        assert self.cluster.cn_resources.requests.get('cpu') == profile.requests_cpu
        assert self.cluster.cn_resources.requests.get('memory') == profile.requests_memory
        assert self.cluster.cn_resources.limits.get('cpu') == profile.limits_cpu
        assert self.cluster.cn_resources.limits.get('memory') == profile.limits_memory
        for pod in self.cluster.get_cn_pods():
            resources = pod.get_resources()
            assert resources.requests.get('cpu') == profile.requests_cpu
            assert resources.requests.get('memory') == profile.requests_memory
            assert resources.limits.get('cpu') == profile.limits_cpu
            assert resources.limits.get('memory') == profile.limits_memory

    @allure.step('检查实例资源使用情况：存储类型和大小')
    def assert_storage(self, profile: ProviderProfile):
        assert self.cluster.cn_storage == (profile.volume_sc, profile.volume_size)
        for pod in self.cluster.get_cn_pods():
            pvc = pod.get_pvcs()
            assert pvc.status.phase == 'Bound'
            assert pvc.spec.resources.requests.get('storage') == profile.volume_size
            assert pvc.spec.storage_class_name == profile.volume_sc

    @allure.step('检查实例资源使用情况：机器类型')
    def assert_host_node_instance_type(self, profile: ProviderProfile):
        for pod in self.cluster.get_cn_pods():
            assert pod.host_node_instance_type in profile.instance_types

    @allure.step('检查实例到期时间')
    def assert_expiration_date(self, period):
        if self.instance.charge_type == ChargeType.PrePaid:
            expiration_date = datetime.strptime(
                (datetime.now() + relativedelta(months=period, days=1)).strftime('%Y-%m-%dT00:00:00Z'),
                '%Y-%m-%dT%H:%M:%SZ').astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            assert self.instance.period == period
            assert self.instance.end_valid_at == expiration_date
            assert self.cluster.expiration_date == expiration_date

    @allure.step('检查实例剩余天数')
    def assert_remain_days(self):
        if self.instance.charge_type == ChargeType.PrePaid:
            assert self.instance.remain_days == self.instance.get_remain_days()

    @allure.step('检查实例是否开启自动续费、自动续费周期、自动续费付款方式')
    def assert_auto_renew(self, auto_renew_period, pay_type: PayType = PayType.Voucher):
        if self.instance.charge_type == ChargeType.PrePaid:
            if auto_renew_period > 0:
                assert self.instance.auto_renew_enabled is True
            else:
                assert self.instance.auto_renew_enabled is False
            assert self.instance.auto_renew_period == auto_renew_period
            assert self.instance.auto_pay_type == pay_type

    @allure.step('验证实例的CU和存储限额')
    def assert_free_quota(self):
        assert self.instance.quota == {}

    @allure.step('验证实例的CU和存储使用量')
    def assert_cu_and_storage_usage(self, cu, storage: int):
        assert self.instance.usage.get('cu') == cu
        assert self.instance.usage.get('storage') == storage
