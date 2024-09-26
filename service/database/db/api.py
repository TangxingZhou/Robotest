import logging
from typing import List
from service.base import BaseAPI
from service.api import moc_api_request

logger = logging.getLogger(__name__)


class DataBaseAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)

    @moc_api_request('/subscribe/tpchsample', 'POST')
    def load_tpch_sample_data(self):
        return {}

    @moc_api_request('/meta/db/tree', 'POST')
    def get_db_tree(self):
        return {}

    @moc_api_request('/meta/db/info', 'POST')
    def get_db_info(self):
        return {}

    @moc_api_request('/meta/db/drop', 'POST')
    def drop_db(self, db):
        return {"db_name": db}

    @moc_api_request('/publication/list', 'POST')
    def get_publications(self, search_words=None, order_by='updadted_at', order='desc', readonly: bool = False):
        payload, _filter = {}, {}
        if search_words:
            _filter['search_words'] = search_words
        if readonly:
            _filter['permission'] = 'readonly'
        if _filter:
            payload['filetr'] = _filter
        if order_by and order:
            payload.update(order_by=order_by, order=order)
        return payload

    @moc_api_request('/target_instance/search', 'POST')
    def get_target_instance(self, internal=True):
        return {'search_internal_instance': internal}

    @moc_api_request('/publication/create', 'POST')
    def create_publication(self, name, database, target_instances: List[str], readonly=True, comments=''):
        payload = {
            "pub_name": name,
            "database": database,
            "permission": "readonly" if readonly else None,
            "target_instances": target_instances
        }
        if comments:
            payload.update(comments=comments)
        return payload

    @moc_api_request('/publication/update', 'POST')
    def update_publication(self, name, database, target_instances: List[str], readonly=True, comments=''):
        payload = {
            "pub_name": name,
            "database": database,
            "permission": "readonly" if readonly else None,
            "target_instances": target_instances
        }
        if comments:
            payload.update(comments=comments)
        return payload

    @moc_api_request('/publication/delete', 'POST')
    def delete_publication(self, name):
        return {"pub_name": name}

    @moc_api_request('/subscribe/list', 'POST')
    def get_subscriptions(self, search_words=None, order_by='pub_time', order='desc'):
        payload, _filter = {}, {}
        if search_words:
            _filter['search_words'] = search_words
        if _filter:
            payload['filetr'] = _filter
        if order_by and order:
            payload.update(order_by=order_by, order=order)
        return payload

    @moc_api_request('/subscribe/create', 'POST')
    def create_subscription(self, subs_name, pub_instance_id, pub_name):
        payload = {
            "subs_name": subs_name,
            "pub_instance_id": pub_instance_id,
            "pub_name": pub_name
        }
        return payload

    @moc_api_request('/subscribe/update', 'POST')
    def update_subscription(self, subs_name, new_subs_name):
        payload = {"subs_name": subs_name, "new_subs_name": new_subs_name}
        return payload

    @moc_api_request('/subscribe/create', 'POST')
    def delete_subscriptions(self, subs_name):
        payload = {"subs_name": subs_name}
        return payload

    @moc_api_request('/meta/db/table', 'POST')
    def get_tables_and_views(self, db):
        return {"name": db}

    @moc_api_request('/meta/table/column', 'POST')
    def get_table_or_veiw_columns(self, db, table):
        return {"db_name": db, "table_name": table}

    @moc_api_request('/meta/table/column_stat', 'POST')
    def get_table_columns_stat(self, db, table):
        return {"db_name": db, "table_name": table}

    @moc_api_request('/meta/table/ddl', 'POST')
    def get_table_or_view_creation_sql(self, db, table):
        return {"db_name": db, "table_name": table}

