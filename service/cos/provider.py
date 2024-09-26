from cloud.k8s.client import K8sClient


class ProviderProfiles(list):

    def __init__(self, **kwargs):
        super().__init__()
        for profile in kwargs.get('profiles'):
            self.append(ProviderProfile(**profile))

    def get_profile_by_name(self, name):
        for p in self:
            if p.name == name:
                return p


class ProviderProfile:

    def __init__(self, **kwargs):
        super().__init__()
        self.name = kwargs.get('name')
        self.capacity_type = kwargs.get('capacityType')
        self.instance_types = kwargs.get('instanceTypes')
        if kwargs.get('resources'):
            self.requests_cpu = kwargs.get('resources').get('requests').get('cpu')
            self.requests_memory = kwargs.get('resources').get('requests').get('memory')
            self.limits_cpu = kwargs.get('resources').get('limits').get('cpu')
            self.limits_memory = kwargs.get('resources').get('limits').get('memory')
        if kwargs.get('volume'):
            self.volume_size = kwargs.get('volume').get('size')
            self.volume_sc = kwargs.get('volume').get('storageClassName')


class ProviderProfileController:

    def __init__(self, k8s_client: K8sClient = None):
        if k8s_client is None:
            k8s_client = K8sClient()
        self.k8s_client = k8s_client

    def get_profiles(self, name):
        provider = self.k8s_client.core_matrixone_cloud_v1alpha1_api.read_provider(name)
        assert provider[1] == 200, f"Failed to read provider '{name}'."
        return ProviderProfiles(**provider[0]['config'])
