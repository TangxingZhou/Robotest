import allure
from service.moi.dify.api import DifyAPI
from service.moi.connect.connectors.models import DifyConnectorConfig
from service.moi.dify.models import *

logger = logging.getLogger(__name__)


class DifyController:

    def __init__(self, dify_connector: DifyConnectorConfig, api_client=None):
        self.api = DifyAPI(dify_connector, api_client)

    @allure.step('创建空的Dif知识库')
    def create_empty_dataset(self, name):
        res = self.api.create_empty_dataset(name)
        return DifyDataSet(**res)

    @allure.step('查看Dify知识库列表')
    def get_datasets(self,
                     keyword='',
                     page=1,
                     page_size=1000):
        res = self.api.get_datasets(keyword, page, page_size)
        return [DifyDataSet(**d) for d in res['data']], res.get('total', 0)

    @allure.step('查看Dify知识库的文档列表')
    def get_documents(self,
                      dataset_id: str,
                      keyword='',
                      page=1,
                      page_size=10):
        res = self.api.get_documents(dataset_id, keyword, page, page_size)
        return [DifyDocument(**d) for d in res['data']], res.get('total', 0)

    @allure.step('查看Dify知识库文档的分段列表')
    def get_segments(self,
                     dataset_id: str,
                     doc_id: str,
                     keyword='',
                     page=1,
                     page_size=10):
        res = self.api.get_segments(dataset_id, doc_id, keyword, page, page_size)
        return [DifySegment(**s) for s in res['data']], res.get('total', 0)

    @allure.step('删除Dify知识库')
    def delete_dataset(self, _id):
        self.api.delete_dataset(_id)
