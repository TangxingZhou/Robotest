import allure
import requests
from uuid import uuid4
from queue import Empty
from urllib.parse import unquote
from service.base import BaseController
from service.database.editor.api import *
from service.database.editor.models import *
from service.database.consts import DEFAULT_TPCH_SAMPLE_DATABASES
from service.error import APIError

logger = logging.getLogger(__name__)


class EditorController(BaseController):
    _api_class = EditorAPI

    def __init__(self, _id=None, api_client=None):
        super().__init__(_id, api_client)
        logger.debug(f"Connect to websocket server for instance_ of '{self.instance_id}'")

    @property
    def instance_id(self) -> str:
        return self.api.api_client.default_headers.get('X-Instance-Id')

    @allure.step('获取工作簿列表')
    def get_workbooks(self, offset=0, limit=100):
        res = self.api.get_workbooks(offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [Workbook(**w) for w in res['data']['result']]

    @allure.step('获取工作簿版本列表')
    def get_workbook_versions(self, _id, offset=0, limit=25):
        res = self.api.get_workbook_versions(_id, offset, limit)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return [WorkbookVersion(**w) for w in res['data']['result']]

    @allure.step('新建工作簿')
    def create_workbook(self):
        res = self.api.create_workbook()
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return Workbook(**res['data'])

    @allure.step('修改工作簿')
    def update_workbook(self, _id, name):
        res = self.api.update_workbook(_id, name)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('删除工作簿')
    def delete_workbook(self, _id):
        res = self.api.delete_workbook(_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('获取工作簿详情')
    def get_workbook_details(self, _id, version_id):
        res = self.api.get_workbook_details(_id, version_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return WorkbookVersionDetail(**res['data'])

    @allure.step('获取数据库表信息')
    def get_table_info(self, _id, db, table):
        res = self.api.get_table_info(_id, db, table)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        columns_schema = [TableColumnSchema(**c) for c in res['data']['columns']]
        assert len(columns_schema) == res['data']['total']
        return columns_schema

    @allure.step('新建工作簿版本')
    def create_workbook_version(self, _id, sql):
        res = self.api.create_workbook_version(_id, sql)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        return WorkbookVersion(**res['data'])

    @allure.step('修改工作簿版本')
    def update_workbook_version(self, _id, version_id, sql):
        res = self.api.update_workbook_version(_id, version_id, sql)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('保存工作簿版本')
    def save_workbook_version(self, _id, version_id, sql):
        res = self.api.save_workbook_version(_id, version_id, sql)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"

    @allure.step('下载查询结果')
    def download_query_result(self, statement_id):
        res = self.api.download_query_result(statement_id)
        assert APIError(**res).is_ok(), f"response code: {res.get('code')}, message: {res.get('msg')}"
        response = requests.get(res['data']['link'])
        assert response.status_code == 200
        file_path = unquote(res['data']['link'].split('?')[0].split('/')[3]).replace('/', '_')
        with open(file_path, 'wb') as file:
            file.write(response.content)
        allure.attach.file(file_path, file_path, allure.attachment_type.CSV)
        return file_path

    @allure.step('SQL Editor里执行SQL语句')
    def execute_sql(self, sql, db='', sql_type='', offset=0, limit=1000):
        for i in range(3):
            try:
                return QueryResult(**self.api.execute_sql(f'{uuid4()}', sql, db, sql_type, offset, limit))
            except Empty:
                continue
        raise Exception(f"Failed to execute SQL: {sql}")

    @allure.step('导入TPCH样例数据')
    def load_tpch_sample_data(self):
        res = self.api.load_tpch_sample_data()
        err = APIError(**res)
        if err.is_ok():
            return None, res['data']['subs_db_success']
        else:
            return err, None

    @allure.step('导入你的数据')
    def load_oss_data(self, db, table, bucket, file_path, ak, sk):
        endpoint = 'oss-cn-hangzhou-internal.aliyuncs.com'
        sql = (f"/* cloud_user */load data url s3option {'{'}\"bucket\"='{bucket}',\"filepath\"='{file_path}',"
               f"\"access_key_id\"='{ak}',\"secret_access_key\"='{sk}',\"compression\"='auto',\"endpoint\"='{endpoint}',{'}'} "
               f"into table `{db}`.`{table}` FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' PARALLEL \"TRUE\";")
        return self.execute_sql(sql, db, 'load')

    def run_tpch_queries(self, sql_file='src/data/sql_data/tpch.sql', db=DEFAULT_TPCH_SAMPLE_DATABASES[0], rounds=1):
        results = []
        with open(sql_file, 'r') as file:
            sql = file.read()
        for i in range(rounds):
            for q in sql.split(';'):
                if q.strip('\n'):
                    results.append(self.execute_sql(q.strip('\n'), db))
        return results

    def ws_close(self):
        self.api.ws.close()
