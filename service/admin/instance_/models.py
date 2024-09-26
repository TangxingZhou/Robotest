from enum import Enum
from service.instance_.models import PlanType, ChargeType, Status, Payment


class PlanChargeType(Enum):
    Serverless = 'serverless'
    Standard_Prepaid = 'standard_prepaid'
    Standard_Postpaid = 'standard_postpaid'


class Instance:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.id = kwargs.get('id')
        self.plan_type: PlanType = PlanType(kwargs.get('plan_type')) if kwargs.get('plan_type') else None
        self.charge_type: ChargeType = ChargeType(kwargs.get('charge_type')) if kwargs.get('plan_type') else None
        self.payment: Payment = Payment(kwargs.get('payment')) if kwargs.get('payment') else None
        self.status: Status = Status(kwargs.get('status')) if kwargs.get('status') else None
        self.created_at = kwargs.get('created_at')
        self.org_creator = kwargs.get('org_creator')
        self.org_name = kwargs.get('org_name')


class InstanceDetail:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.id = kwargs.get('id')
        self.plan_type: PlanType = PlanType(kwargs.get('plan_type')) if kwargs.get('plan_type') else None
        self.charge_type: ChargeType = ChargeType(kwargs.get('charge_type')) if kwargs.get('charge_type') else None
        self.payment: Payment = Payment(kwargs.get('payment')) if kwargs.get('payment') else None
        self.status: Status = Status(kwargs.get('status')) if kwargs.get('status') else None
        self.created_at = kwargs.get('created_at')
        self.creator = kwargs.get('creator')
        self.provider = kwargs.get('provider')
        self.region = kwargs.get('region')
        self.keep_serving: bool = kwargs.get('keep_serving')
        self.components = kwargs.get('components')
        self.prepaid = kwargs.get('prepaid')
        self.cu_limited_monthly = kwargs.get('cu_limited_monthly')
        self.cu_used_monthly = kwargs.get('cu_used_monthly')
        self.cu_used_total = kwargs.get('cu_used_total')
        self.latest_created_at = kwargs.get('latest_created_at')
        self.mo_version = kwargs.get('mo_version')
        self.org_creator = kwargs.get('org_creator')
        self.org_id = kwargs.get('org_id')
        self.org_name = kwargs.get('org_name')
        self.storage = kwargs.get('storage')
        self.storage_limited = kwargs.get('storage_limited')
        self.cost_unit = kwargs.get('cost_unit')
        self.daily_cost = kwargs.get('daily_cost')
        self.monthly_cost = kwargs.get('monthly_cost')
        self.normal_cn = kwargs.get('normal_cn')
        self.normal_max_cn = kwargs.get('normal_max_cn')
        self.normal_min_cn = kwargs.get('normal_min_cn')
        self.limited_cn = kwargs.get('limited_cn')
        self.limited_max_cn = kwargs.get('limited_max_cn')
        self.limited_min_cn = kwargs.get('limited_min_cn')
