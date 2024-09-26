import logging

logger = logging.getLogger(__name__)


class ServerlessPrice(dict):

    def __init__(self, **kwargs):
        super().__init__()
        self.provider = kwargs.get('provider')
        self.region = kwargs.get('region')
        self.base_cu = kwargs.get('base_cu')
        self.cu_factor_units = kwargs.get('cu_factor_units')
        self['cu'] = ServerlessUnitPrice(**kwargs.get('cu'))
        self['storage'] = ServerlessUnitPrice(**kwargs.get('storage'))


class ServerlessUnitPrice:

    def __init__(self, **kwargs):
        self.price = kwargs.get('price')
        self.discount = kwargs.get('discount')
        self.price_unit = kwargs.get('price_unit')


class StandardPrice(dict):

    def __init__(self, **kwargs):
        super().__init__()
        self.provider = kwargs.get('provider')
        self.region = kwargs.get('region')
        for k, v in kwargs.get('price').items():
            if k == 'compute':
                self[k] = StandardComputePrice(**v[0])
            else:
                self[k] = StandardCommonPrice(**v)

    @property
    def capacities(self):
        return list(self.get('compute').keys())

    def capacity_period_is_valid(self, capacity, period: int = 1):
        for k, v in self.get('compute').items():
            if k == capacity:
                if period in v.periods:
                    return True
                else:
                    logger.error(f"Period '{period}' is invalid for capacity '{capacity}', available: {v.periods}")
                    return False
        logger.error(f"Capacity '{capacity}' is invalid, available: {self.capacities}")
        return False

    def get_compute_price(self, capacity, period: int = 1):
        if self.capacity_period_is_valid(capacity, period):
            return self.get('compute').get_price(capacity, period)

    def get_common_price(self, k):
        if k == 'compute':
            logger.error(f"Price of compute cannot be gotten by this method.")
        else:
            return self.get(k)


class StandardCommonPrice:

    def __init__(self, **kwargs):
        self.discount = float(kwargs.get('discount'))
        self.price = float(kwargs.get('price'))
        self.price_unit = kwargs.get('price_unit')


class StandardComputePrice(dict):

    def __init__(self, **kwargs):
        super().__init__()
        self.default_capacity = kwargs.get('default_capacity')
        for p in kwargs.get('price'):
            self[p['capacity']] = StandardComputeCapacityPrice(**p)

    def get_price(self, capacity, period: int = 1):
        return self[capacity].get_period_price(period)


class StandardComputeCapacityPrice(list):

    def __init__(self, **kwargs):
        super().__init__()
        self.capacity = kwargs.get('capacity')
        for p in kwargs.get('period_price'):
            self.append(StandardComputePeriodPrice(**p))

    @property
    def periods(self):
        return [p.period for p in self]

    def get_period_price(self, period: int = 1):
        for p in self:
            if p.period == period:
                return p


class StandardComputePeriodPrice:

    def __init__(self, **kwargs):
        self.period = kwargs.get('period')
        self.price = float(kwargs.get('price'))
        self.discount = float(kwargs.get('discount'))
        self.price_unit = kwargs.get('price_unit')
