from __future__ import absolute_import

from kubernetes.client.api_client import ApiClient
from cloud.k8s import k8s_api_request


class MOIV1alpha1Api(object):

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets', 'POST', 'MOIV1alpha1CNClaimSet')
    def create_cn_claim_set(self, namespace, body, **kwargs):
        """
        create a CNClaimSet
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1CNClaimSet body: (required)
        :return: tuple(MOIV1alpha1CNClaimSet, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets', 'DELETE', 'V1Status')
    def delete_collection_cn_claim_set(self, namespace, **kwargs):
        """
        delete collection of CNClaimSet
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets/{name}', 'DELETE', 'V1Status')
    def delete_cn_claim_set(self, name, namespace, **kwargs):
        """
        delete a CNClaimSet
        :param str name: name of the CNClaimSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/', 'GET', 'V1APIResourceList')
    def get_api_resources(self, **kwargs):
        """
        get available resources
        :return: tuple(V1APIResourceList, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets', 'GET', 'MOIV1alpha1CNClaimSetList')
    def list_cn_claim_set(self, namespace, **kwargs):
        """
        list or watch objects of kind CNClaimSet
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(MOIV1alpha1CNClaimSetList, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets/{name}', 'PATCH', 'MOIV1alpha1CNClaimSet')
    def patch_cn_claim_set(self, name, namespace, body, **kwargs):
        """
        partially update the specified CNClaimSet
        :param str name: name of the CNClaimSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1CNClaimSet body: (required)
        :return: tuple(MOIV1alpha1CNClaimSet, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets/{name}', 'GET', 'MOIV1alpha1CNClaimSet')
    def read_cn_claim_set(self, name, namespace, **kwargs):
        """
        read the specified CNClaimSet
        :param str name: name of the CNClaimSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(MOIV1alpha1CNClaimSet, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnclaimsets/{name}', 'PUT', 'MOIV1alpha1CNClaimSet')
    def replace_cn_claim_set(self, name, namespace, body, **kwargs):
        """
        replace the specified CNClaimSet
        :param str name: name of the CNClaimSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1CNClaimSet body: (required)
        :return: tuple(MOIV1alpha1CNClaimSet, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters', 'POST', 'MOIV1alpha1MOCluster')
    def create_mo_cluster(self, namespace, body, **kwargs):
        """
        create a MO Cluster managed by operator
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1MOCluster body: (required)
        :return: tuple(MOIV1alpha1MOCluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters', 'DELETE', 'V1Status')
    def delete_collection_mo_cluster(self, namespace, **kwargs):
        """
        delete collection of MO Cluster managed by operator
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters/{name}', 'DELETE', 'V1Status')
    def delete_mo_cluster(self, name, namespace, **kwargs):
        """
        delete a MO Cluster managed by operator
        :param str name: name of the MO Cluster (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(V1Status, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters', 'GET', 'MOIV1alpha1MOClusterList')
    def list_mo_cluster(self, namespace, **kwargs):
        """
        list or watch objects of kind MatrixOneCluster
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(MOIV1alpha1MOClusterList, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters/{name}', 'PATCH', 'MOIV1alpha1MOCluster')
    def patch_mo_cluster(self, name, namespace, body, **kwargs):
        """
        partially update the specified MO Cluster managed by operator
        :param str name: name of the MO Cluster (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1MOCluster body: (required)
        :return: tuple(MOIV1alpha1MOCluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters/{name}', 'GET', 'MOIV1alpha1MOCluster')
    def read_mo_cluster(self, name, namespace, **kwargs):
        """
        read the specified MO Cluster managed by operator
        :param str name: name of the MO Cluster (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(MOIV1alpha1MOCluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/matrixoneclusters/{name}', 'PUT', 'MOIV1alpha1MOCluster')
    def replace_mo_cluster(self, name, namespace, body, **kwargs):
        """
        replace the specified MO Cluster managed by operator
        :param str name: name of the MO Cluster (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :param MOIV1alpha1MOCluster body: (required)
        :return: tuple(MOIV1alpha1MOCluster, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/logsets/{name}', 'GET')
    def read_logset(self, name, namespace, **kwargs):
        """
        read the specified LogSet
        :param str name: name of the LogSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(dict, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/dnsets/{name}', 'GET')
    def read_dnset(self, name, namespace, **kwargs):
        """
        read the specified DNSet
        :param str name: name of the DNSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(dict, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/cnsets/{name}', 'GET')
    def read_cnset(self, name, namespace, **kwargs):
        """
        read the specified CNSet
        :param str name: name of the CNSet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(dict, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass

    @k8s_api_request('/apis/core.matrixorigin.io/v1alpha1/namespaces/{namespace}/proxysets/{name}', 'GET')
    def read_proxyset(self, name, namespace, **kwargs):
        """
        read the specified ProxySet
        :param str name: name of the ProxySet (required)
        :param str namespace: object name and auth scope, such as for teams and projects (required)
        :return: tuple(dict, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously, returns the request thread.
        """
        pass
