
class Organization:

    def __init__(self, **kwargs):
        self.created_at: str = kwargs.get('created_at')
        self.creator: str = kwargs.get('creator')
        self.enable_paid_instance: bool = kwargs.get('enable_paid_instance')
        self.free_instance_limited: int = kwargs.get('free_instance_limited')
        self.free_instance_num: int = kwargs.get('free_instance_num')
        self.free_to_paid_instance_num: int = kwargs.get('free_to_paid_instance_num')
        self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.paid_instance_num: int = kwargs.get('paid_instance_num')
        self.remark: str = kwargs.get('remark')
