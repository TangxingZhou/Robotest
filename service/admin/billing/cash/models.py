from enum import Enum


class TransactionChannel(Enum):
    CorporateTransfer = 'corporate_transfer'
    Alipay = 'alipay'
    CashBalance = 'cash_balance'


class TransactionTypeDetail(Enum):
    Consume = 'consume'
    Recharge = 'recharge'
    Withdraw = 'withdraw'
    Refund = 'refund'


class TransactionType(Enum):
    Income = 'income'
    Expense = 'expense'


class TransactionStatus(Enum):
    Successful = 'successful'
    Failed = 'failed'


class CashRecords(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.total = kwargs.get('total')
        self.total_expense = kwargs.get('summary').get('total_expense')
        self.total_income = kwargs.get('summary').get('total_income')
        self.billing_cycles = kwargs.get('summary').get('billing_cycles')
        for r in kwargs.get('data'):
            self.append(CashRecord(**r))


class CashRecord:

    def __init__(self, **kwargs):
        self.amount = kwargs.get('amount')
        self.balance = kwargs.get('balance')
        self.billing_cycle = kwargs.get('billing_cycle')
        self.comment = kwargs.get('comment')
        self.income_or_expense = TransactionType(kwargs.get('income_or_expense'))
        self.org_creator = kwargs.get('org_creator')
        self.org_id = kwargs.get('org_id')
        self.org_name = kwargs.get('org_name')
        self.status = TransactionStatus(kwargs.get('status'))
        self.transaction_account = kwargs.get('transaction_account')
        self.transaction_channel = TransactionChannel(kwargs.get('transaction_channel'))
        self.transaction_id = kwargs.get('transaction_id')
        self.transaction_time = kwargs.get('transaction_time')
        self.transaction_type = TransactionTypeDetail(kwargs.get('transaction_type'))
