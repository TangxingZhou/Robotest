import logging
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from service.base import BaseAPI
from service.api import moc_api_request
from service.database.models import SQLType
from service.database.dashboard.models import *

logger = logging.getLogger(__name__)


class DashboardAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/metric/runtime', 'POST')
    def get_runtime(self,
                    start='',
                    end='',
                    recent_mins: int = 30,
                    metrics_name: MetricsType = MetricsType.QPS,
                    metrics_agg: MetricsAgg = MetricsAgg.AVG):
        if start and end:
            try:
                start_at = datetime.strptime(start, '%Y-%m-%dT%H:%M:00%z')
                end_at = datetime.strptime(end, '%Y-%m-%dT%H:%M:00%z')
            except ValueError as e:
                raise e
            if start_at > end_at:
                raise ValueError(f"{start} must less then {end}")
            else:
                if (end_at - start_at).total_seconds() > 5 * 60:
                    interval = 60
                else:
                    interval = 30
        else:
            end = datetime.now().astimezone(timezone(timedelta(hours=8), 'UTC'))
            start = (end + relativedelta(minutes=0 - recent_mins)).strftime('%Y-%m-%dT%H:%M:00%z')
            end = end.strftime('%Y-%m-%dT%H:%M:00%z')
            if recent_mins > 5:
                interval = 60
            else:
                interval = 30
        metrics_filter = {"name": metrics_name.value, "agg": metrics_agg.value}
        if metrics_name in (MetricsType.QueryLatency, MetricsType.StatementTotalCount, MetricsType.StatementErrorCount):
            metrics_filter.update(types=[k for k in SQLType._value2member_map_.keys()])
        payload = {
            "metrics": [metrics_filter],
            "start": f'{start[:-2]}:{start[-2:]}',
            "end": f'{end[:-2]}:{end[-2:]}',
            "interval":interval
        }
        return payload
