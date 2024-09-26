import allure
from service.base import BaseController
from service.database.db.api import *
from service.database.db.models import *
from service.database.consts import DEFAULT_TPCH_SAMPLE_DATABASES
from service.utils import objects_should_be_equal
from service.error import APIError

logger = logging.getLogger(__name__)


class DataBaseController(BaseController):
    _api_class = DataBaseAPI

    def __init__(self, _id=None, api_client=None):
        super().__init__(_id, api_client)

    @property
    def instance_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Instance-Id')

    @allure.step('查看实例的数据库列表')
    def get_db_tree(self):
        res = self.api.get_db_tree()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [DB(**d) for d in res['data']['db_list']]

    @allure.step('查看实例的数据库详情')
    def get_db_info(self):
        res = self.api.get_db_info()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [DBInfo(**d) for d in res['data']['result']]

    @allure.step('删除数据库')
    def drop_db(self, db):
        res = self.api.drop_db(db)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('查看发布')
    def get_publications(self, search_words=None, order_by='updadted_at', order='desc', readonly: bool = False):
        res = self.api.get_publications(search_words, order_by, order, readonly)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Publication(**p) for p in res['data']['pubs']]
    
    @allure.step('查看目标实例')
    def get_target_instance(self, internal=True):
        res = self.api.get_target_instance(internal)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [PublicationTargetInstances(**p) for p in res['data']['instances']]
    
    @allure.step('新建发布')
    def create_publication(self, name, database, target_instances: List[str], readonly=True, comments=''):
        res = self.api.create_publication(name, database, target_instances, readonly, comments)
        err = APIError(**res)
        if not err.is_ok():
            return err
    
    @allure.step('修改发布')
    def update_publication(self, name, database, target_instances: List[str], readonly=True, comments=''):
        res = self.api.update_publication(name, database, target_instances, readonly, comments)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
    
    @allure.step('删除发布')
    def delete_publication(self, name):
        res = self.api.delete_publication(name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('查询订阅')
    def get_subscriptions(self, search_words=None, order_by='pub_time', order='desc'):
        res = self.api.get_subscriptions(search_words, order_by, order)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Subscription(**s['publication']) for s in res['data']['subs']]

    @allure.step('新建订阅')
    def create_subscription(self, subs_name, pub_instance_id, pub_name):
        res = self.api.create_subscription(subs_name, pub_instance_id, pub_name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('修改订阅')
    def update_subscription(self, subs_name, new_subs_name):
        res = self.api.update_subscription(subs_name, new_subs_name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('删除订阅')
    def delete_subscriptions(self, subs_name):
        res = self.api.delete_subscriptions(subs_name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('查看数据库表和视图')
    def get_tables_and_views(self, db):
        res = self.api.get_tables_and_views(db)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [DB(**d) for d in res['data']]

    @allure.step('获取数据库表或视图的列信息')
    def get_table_or_veiw_columns(self, db, table):
        res = self.api.get_table_or_veiw_columns(db, table)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [DBColumn(**c) for c in res['data']['columns']]

    @allure.step('获取数据库表的列统计信息')
    def get_table_columns_stat(self, db, table):
        res = self.api.get_table_columns_stat(db, table)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [DBColumnStat(**c) for c in res['data']['columns']]

    @allure.step('查看数据库表或视图的创建SQL')
    def get_table_or_view_creation_sql(self, db, table):
        res = self.api.get_table_or_view_creation_sql(db, table)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data'].get('create_sql')

    @allure.step('导入TPCH样例数据')
    def load_tpch_sample_data(self):
        res = self.api.load_tpch_sample_data()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return res['data']

    def init_tpch_sample_data(self):
        dbs = [db.db_name for db in self.get_db_tree()]
        tpch_db_exists = 0
        for d in DEFAULT_TPCH_SAMPLE_DATABASES:
            if d in dbs:
                tpch_db_exists += 1
        if tpch_db_exists != 0:
            for d in DEFAULT_TPCH_SAMPLE_DATABASES:
                self.drop_db(d)
        assert objects_should_be_equal(self.load_tpch_sample_data()['subs_db_success'], DEFAULT_TPCH_SAMPLE_DATABASES)

    def clear_tpch_sample_data(self):
        dbs = [db.db_name for db in self.get_db_tree()]
        for d in DEFAULT_TPCH_SAMPLE_DATABASES:
            if d in dbs:
                self.drop_db(d)
