from enum import Enum


class VoucherStatus(Enum):
    NotActive = 'not_active'
    Available = 'available'
    Expired = 'expired'
    Cancelled = 'cancelled'
    Consumed = 'consumed'


class VoucherRecordStatus(Enum):
    Successful = 'successful'
    Failed = 'failed'


class VoucherSource(Enum):
    MarketingDistribution = 'marketing_distribution'
    RechargeBonus = 'recharge_bonus'


class Vouchers(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.balance = kwargs.get('summary').get('balance')
        self.face_value = kwargs.get('summary').get('face_value')
        for v in kwargs.get('vouchers'):
            self.append(Voucher(**v))


class Voucher:

    def __init__(self, **kwargs):
        self.activated = kwargs.get('activated')
        self.activation_code = kwargs.get('activation_code')
        self.balance = kwargs.get('balance')
        self.consumed_amount = kwargs.get('consumed_amount')
        self.effective_time = kwargs.get('effective_time')
        self.expiration_time = kwargs.get('expiration_time')
        self.face_value = kwargs.get('face_value')
        self.id = kwargs.get('id')
        self.org_id = kwargs.get('org_id')
        self.source = VoucherSource(kwargs.get('source'))
        self.status = VoucherStatus(kwargs.get('status'))


class VoucherRecords(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.amount = kwargs.get('summary').get('amount')
        for v in kwargs.get('data'):
            self.append(VoucherRecord(**v))


class VoucherRecord:

    def __init__(self, **kwargs):
        self.amount = kwargs.get('amount')
        self.balance = kwargs.get('balance')
        self.face_value = kwargs.get('face_value')
        self.org_id = kwargs.get('org_id')
        self.status = VoucherRecordStatus(kwargs.get('status'))
        self.transaction_id = kwargs.get('transaction_id')
        self.transaction_time = kwargs.get('transaction_time')
        self.voucher_id = kwargs.get('voucher_id')
