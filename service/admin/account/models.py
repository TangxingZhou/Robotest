from enum import Enum


class Type(Enum):
    Internal = 'internal'
    Enterprise = 'enterprise'
    Partner = 'partner'
    Individual = 'individual'
    Others = 'others'


class Status(Enum):
    TrialPending = 'trial_pending'
    Approved = 'approved'
    TrialInactivated = 'trial_inactivated'
    Pending = 'pending'
    Inactivated = 'inactivated'
    Rejected = 'rejected'
    Activated = 'activated'
    Blocked = 'blocked'


class Source(Enum):
    Direct = 'direct'
    Channel = 'channel'
    OfficialWebsite = 'official_website'
    Event = 'event'
    Others = 'others'


class Account:

    def __init__(self, **kwargs):
        self.company = kwargs.get('company')
        self.created_at = kwargs.get('created_at')
        self.email = kwargs.get('email')
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.org_id = kwargs.get('org_id')
        self.phone_number = kwargs.get('phone_number')
        self.purpose = kwargs.get('purpose')
        self.signup_method = kwargs.get('signup_method')
        self.source = Source(kwargs.get('source'))
        self.status = Status(kwargs.get('status'))
        self.type = Type(kwargs.get('type'))
