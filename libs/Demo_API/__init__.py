
from libs.apis import Configuration, ApiClient, k8s_api_request


class V1Api(object):

    def __init__(self, api_client=None, **kwargs):
        if api_client is None:
            customized_configuration = Configuration()
            for k, v in kwargs.items():
                if hasattr(customized_configuration, k):
                    setattr(customized_configuration, k, v)
            api_client = ApiClient(customized_configuration)
        self.api_client = api_client

    @k8s_api_request('/api/v1/namespaces/{name}', 'GET', 'V1Namespace')
    def get_namespace(self, name, **kwargs):
        pass
