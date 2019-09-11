
from libs.apis import Configuration, ApiClient, request


class V1Api(object):

    def __init__(self, api_client=None, **kwargs):
        if api_client is None:
            customized_configuration = Configuration()
            for k, v in kwargs.items():
                if hasattr(customized_configuration, k):
                    setattr(customized_configuration, k, v)
            api_client = ApiClient(customized_configuration)
        self.api_client = api_client

    @request('/api/v1/namespaces/{name}', 'GET', 'name')
    def get_namespace(self, **kwargs):
        pass
