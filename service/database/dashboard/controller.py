import allure
from service.base import BaseController
from service.database.dashboard.api import *
from service.database.dashboard.models import *
from service.error import APIError

logger = logging.getLogger(__name__)


class DashboardController(BaseController):
    _api_class = DashboardAPI

    def __init__(self, _id=None, api_client=None):
        super().__init__(_id, api_client)

    @property
    def instance_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Instance-Id')

    @allure.step('获取metrics数据')
    def get_runtime(self,
                    start='',
                    end='',
                    recent_mins: int = 30,
                    metrics_name: MetricsType = MetricsType.QPS,
                    metrics_agg: MetricsAgg = MetricsAgg.AVG):
        res = self.api.get_runtime(start, end, recent_mins, metrics_name, metrics_agg)
        err = APIError(**res)
        if err.is_ok():
            return None, res['data']['metrics']
        else:
            return err, None
