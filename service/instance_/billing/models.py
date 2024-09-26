from enum import Enum
from service.admin.billing.cash.models import TransactionStatus, TransactionType
from service.admin.billing.voucher.models import VoucherStatus, VoucherSource, VoucherRecordStatus


class BillingTrendType(Enum):
    InstancePlanType = 'instance_plan_type'
    BillingItem = 'billing_item'
    TopInstances = 'top_instances'


class BillingDimension(Enum):
    BillingItem = 'billing_item'
    Instance = 'instance_'


class BillingPeriod(Enum):
    Monthly = 'monthly'
    Daily = 'daily'
    Hourly = 'hourly'


class BillingStatus(Enum):
    InBilling = 'in_billing'
    Cleared = 'cleared'
    uncleared = 'uncleared'
    unsettled = 'unsettled'
    # TODO: 待补充，账单列表和月账单概览里账单状态是否一致


class BillingItem(Enum):
    Compute = 'compute'
    CU = 'cu'
    Network = 'network'
    IO_IN = 'objectinapi'
    IO_OUT = 'objectoutapi'
    Storage = 'storage'


class BillingType(Enum):
    PostPaid = 'pay-as-you-go'
    PrePaid = 'subscription'


class AccountStat:

    def __init__(self, **kwargs):
        self.cash_balance = kwargs.get('cash_balance')
        self.daily_spending = kwargs.get('daily_spending')
        self.monthly_spending = kwargs.get('monthly_spending')
        self.total_balance = kwargs.get('total_balance')
        self.voucher_balance = kwargs.get('voucher_balance')


class MonthlyBillingDetail:

    def __init__(self, **kwargs):
        self.billing_cycle = kwargs.get('billing_cycle')
        self.billing_date = kwargs.get('billing_date')
        self.cash_deduction = kwargs.get('cash_deduction')
        self.expenditure_amount = kwargs.get('expenditure_amount')
        self.outstanding_amount = kwargs.get('outstanding_amount')
        self.status = BillingStatus(kwargs.get('status'))
        self.voucher_deduction = kwargs.get('voucher_deduction')


class MonthlyBilling(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.total_cash_deduction = kwargs.get('total_cash_deduction')
        self.total_expenditure_amount = kwargs.get('total_expenditure_amount')
        self.total_outstanding_amount = kwargs.get('total_outstanding_amount')
        self.total_voucher_deduction = kwargs.get('total_voucher_deduction')
        for d in kwargs.get('details'):
            self.append(MonthlyBillingDetail(**d))


class BillingTrend(list):

    def __init__(self, **kwargs):
        super().__init__()
        for s in kwargs.get('series'):
            self.append(BillingTrendCycle(**s))


class BillingTrendCycle(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.billing_cycle = kwargs.get('billing_cycle')
        self.series = kwargs.get('series')
        for s in kwargs.get('series'):
            self.append(BillingTrendCycleSeries(**s))


class BillingTrendCycleSeries:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.value = kwargs.get('value')


class TransactionRecord:

    def __init__(self, **kwargs):
        self.amount = kwargs.get('amount')
        self.balance = kwargs.get('balance')
        self.billing_cycle = kwargs.get('billing_cycle')
        self.comment = kwargs.get('comment')
        self.income_or_expense = TransactionType(kwargs.get('income_or_expense'))
        self.status = TransactionStatus(kwargs.get('status'))
        self.transaction_account = kwargs.get('transaction_account')
        self.transaction_channel = kwargs.get('transaction_channel')
        self.transaction_id = kwargs.get('transaction_id')
        self.transaction_time = kwargs.get('transaction_time')
        self.transaction_type = kwargs.get('transaction_type')


class Transaction(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.summary_amount = kwargs.get('transaction_summary').get('amount')
        for t in kwargs.get('transactions'):
            self.append(TransactionRecord(**t))


class BillingRecord:

    def __init__(self, **kwargs):
        self.billing_id = kwargs.get('billing_id')
        self.billing_cycle = kwargs.get('billing_cycle')
        self.instance_plan_type = kwargs.get('instance_plan_type')
        self.instance_charge_type = kwargs.get('instance_charge_type')
        self.instance_id = kwargs.get('instance_id')
        self.start_time = kwargs.get('start_time')
        self.billing_item = kwargs.get('billing_item')
        self.billing_type = kwargs.get('billing_type')
        self.price = kwargs.get('price')
        self.unit = kwargs.get('unit')
        self.usage = kwargs.get('usage')
        self.usage_unit = kwargs.get('usage_unit')
        self.pretax_gross_amount = kwargs.get('pretax_gross_amount')
        self.discount_amount = kwargs.get('discount_amount')
        self.pretax_amount = kwargs.get('pretax_amount')
        self.round_down_amount = kwargs.get('round_down_amount')
        self.outstanding_amount = kwargs.get('outstanding_amount')
        self.cash_deduction = kwargs.get('cash_deduction')
        self.voucher_deduction = kwargs.get('voucher_deduction')
        self.status = BillingStatus(kwargs.get('status'))


class Billing(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.summary_cash_deduction = kwargs.get('billing_summary').get('cash_deduction')
        self.summary_discount_amount = kwargs.get('billing_summary').get('discount_amount')
        self.summary_outstanding_amount = kwargs.get('billing_summary').get('outstanding_amount')
        self.summary_pretax_amount = kwargs.get('billing_summary').get('pretax_amount')
        self.summary_pretax_gross_amount = kwargs.get('billing_summary').get('pretax_gross_amount')
        self.summary_round_down_amount = kwargs.get('billing_summary').get('round_down_amount')
        self.summary_voucher_deduction = kwargs.get('billing_summary').get('voucher_deduction')
        for r in kwargs.get('billings'):
            self.append(BillingRecord(**r))


class VoucherStat:

    def __init__(self, **kwargs):
        self.balance = kwargs.get('balance')
        self.cancelled_amount = kwargs.get('cancelled_amount')
        self.consumed_amount = kwargs.get('consumed_amount')
        self.expired_amount = kwargs.get('expired_amount')
        self.face_value = kwargs.get('face_value')
        self.inactive_amount = kwargs.get('inactive_amount')


class Voucher(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.summary_voucher_balance = kwargs.get('voucher_summary').get('balance')
        self.summary_voucher_face_value = kwargs.get('voucher_summary').get('face_value')
        for r in kwargs.get('vouchers'):
            self.append(VoucherDetail(**r))


class VoucherDetail:

    def __init__(self, **kwargs):
        self.balance = kwargs.get('balance')
        self.effective_time = kwargs.get('effective_time')
        self.expiration_time = kwargs.get('expiration_time')
        self.face_value = kwargs.get('face_value')
        self.recharge_time = kwargs.get('recharge_time')
        self.source = VoucherSource(kwargs.get('source'))
        self.status = VoucherStatus(kwargs.get('status'))
        self.voucher_id = kwargs.get('voucher_id')


class VoucherRecord(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.summary_voucher_record_amount = kwargs.get('vouchers_record_summary').get('amount')
        for r in kwargs.get('vouchers'):
            self.append(VoucherRecordDetail(**r))


class VoucherRecordDetail:

    def __init__(self, **kwargs):
        self.amount = kwargs.get('amount')
        self.balance = kwargs.get('balance')
        self.face_value = kwargs.get('face_value')
        self.status = VoucherRecordStatus(kwargs.get('status'))
        self.transaction_id = kwargs.get('transaction_id')
        self.transaction_time = kwargs.get('transaction_time')
        self.voucher_id = kwargs.get('voucher_id')
