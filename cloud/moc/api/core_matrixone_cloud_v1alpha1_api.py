from __future__ import absolute_import

from kubernetes.client.api_client import ApiClient
from cloud.k8s import k8s_api_request


class MOCV1alpha1Api(object):

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters', 'POST', 'MOCV1alpha1Cluster')
    def create_cluster(self, body, **kwargs):
        """
        create a Cluster
        :param MOCV1alpha1Cluster body: (required)
        :return: tuple(MOCV1alpha1Cluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters', 'DELETE', 'V1Status')
    def delete_collection_cluster(self, **kwargs):
        """
        delete collection of Cluster
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters/{name}', 'DELETE', 'V1Status')
    def delete_cluster(self, name, **kwargs):
        """
        delete a Cluster
        :param str name: name of the Cluster (required)
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/', 'GET', 'V1APIResourceList')
    def get_api_resources(self, **kwargs):
        """
        get available resources
        :return: tuple(V1APIResourceList, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters', 'GET', 'MOCV1alpha1ClusterList')
    def list_cluster(self, **kwargs):
        """
        list or watch objects of kind Cluster
        :return: tuple(MOCV1alpha1ClusterList, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters/{name}', 'PATCH', 'MOCV1alpha1Cluster')
    def patch_cluster(self, name, body, **kwargs):
        """
        partially update the specified Cluster
        :param str name: name of the Cluster (required)
        :param MOCV1alpha1Cluster body: (required)
        :return: tuple(MOCV1alpha1Cluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters/{name}', 'GET', 'MOCV1alpha1Cluster')
    def read_cluster(self, name, **kwargs):
        """
        read the specified Cluster
        :param str name: name of the Cluster (required)
        :return: tuple(MOCV1alpha1Cluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/clusters/{name}', 'PUT', 'MOCV1alpha1Cluster')
    def replace_cluster(self, name, body, **kwargs):
        """
        replace the specified Cluster
        :param str name: name of the Cluster (required)
        :param MOCV1alpha1Cluster body: (required)
        :return: tuple(MOCV1alpha1Cluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixone-cloud/v1alpha1/providers/{name}', 'GET')
    def read_provider(self, name, **kwargs):
        """
        read the specified Provider
        :param str name: name of the Provider (required)
        :return: tuple(dict, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass
