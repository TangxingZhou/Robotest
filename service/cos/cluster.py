import logging
from enum import Enum
from cloud.k8s.client import K8sClient
from kubernetes.client.models import V1Pod
from cloud.k8s.secret import read_secret
from cloud.moc.models.v1alpha1_cluster import MOCV1alpha1Cluster

logger = logging.getLogger(__name__)


class MOClusterPhase(Enum):
    pending = 'Pending'
    creating = 'Creating'
    active = 'Active'
    upgrading = 'Upgrading'
    suspended = 'Suspended'
    hibernated = 'Hibernated'
    deleting = 'Deleting'
    restricted = 'Restricted'
    none = None


class MOClusterType(Enum):
    serverless_free = 1
    serverless_paid = 2
    standard_postpaid = 3
    standard_prepaid = 4


class MOCNPoolPhase(Enum):
    bound = 'Bound'
    idle = 'Idle'


class CNPod:

    def __init__(self, k8s_client: K8sClient, name, namespace):
        if k8s_client is None:
            k8s_client = K8sClient()
        self.k8s_client = k8s_client
        self.pod: V1Pod = self.k8s_client.v1_api.read_namespaced_pod(name, namespace)
        self.cn_uuid = self.pod.metadata.labels.get('matrixone.cloud/cn-uuid')
        self.component = self.pod.metadata.labels.get('matrixone.cloud/component')
        self.main_cluster = self.pod.metadata.labels.get('matrixone.cloud/main-cluster')
        self.organization = self.pod.metadata.labels.get('matrixone.cloud/organization')
        self.profile = self.pod.metadata.labels.get('matrixone.cloud/profile')
        self.last_owner = self.pod.metadata.labels.get('matrixorigin.io/last-owner')
        self.owner = self.pod.metadata.labels.get('matrixorigin.io/owner')
        self.pool_phase = self.pod.metadata.labels.get('pool.matrixorigin.io/phase')
        self.pool_name = self.pod.metadata.labels.get('pool.matrixorigin.io/pool-name')
        # self.pool_claimed_by = self.pod.metadata.labels.get('pool.matrixorigin.io/claimed-by')

    @property
    def is_default(self):
        return self.pool_name is None

    @property
    def is_in_limited_pool(self):
        return self.pool_name == f'{self.main_cluster}-limited'

    @property
    def is_in_localpv_pool(self):
        return self.pool_name == f'{self.main_cluster}-localpv'

    def is_bounded(self, _id):
        if self.pool_name:
            if self.pool_phase == 'Bound' and self.owner == _id:
                return True
            else:
                return False
        else:
            return

    def get_pvcs(self, volume_name='mo-data'):
        pvcs = []
        for volume in self.pod.spec.volumes:
            if volume.persistent_volume_claim:
                if volume.name == volume_name:
                    return self.k8s_client.v1_api.read_namespaced_persistent_volume_claim(
                        volume.persistent_volume_claim.claim_name, self.pod.metadata.namespace)
                else:
                    pvcs.append(self.k8s_client.v1_api.read_namespaced_persistent_volume_claim(
                        volume.persistent_volume_claim.claim_name, self.pod.metadata.namespace))
        return pvcs

    def get_resources(self, container_name='main'):
        resources = {}
        for container in self.pod.spec.containers:
            if container.name == container_name:
                return container.resources
            else:
                resources[container.name] = container.resources
        return resources

    @property
    def host_node_instance_type(self):
        return self.k8s_client.v1_api.read_node(self.pod.spec.node_name).metadata.labels.get('node.kubernetes.io/instance_-type')


class RootCluster:

    def __init__(self, k8s_client: K8sClient, name=''):
        if k8s_client is None:
            k8s_client = K8sClient()
        self.k8s_client = k8s_client
        if name:
            cluster = self.k8s_client.core_matrixone_cloud_v1alpha1_api.read_cluster(name)
            assert cluster[1] == 200, f"Failed to read cluster '{name}'."
            self.cluster: MOCV1alpha1Cluster = cluster[0]
        else:
            clusters = self.k8s_client.core_matrixone_cloud_v1alpha1_api.list_cluster()
            assert clusters[1] == 200, f"Failed to list clusters."
            root_clusters_in_use = []
            for cluster in clusters[0].items:
                if not cluster.spec.main_cluster_ref and cluster.metadata.labels.get('matrixone.cloud/role') == 'root':
                    if cluster.metadata.labels.get('matrixone.cloud/cordoned') != 'Y':
                        root_clusters_in_use.append(cluster)
            if root_clusters_in_use:
                if len(root_clusters_in_use) > 1:
                    raise Exception(f"More than one root clusters are in use: {', '.join([c.metadata.name for c in root_clusters_in_use])}.")
            else:
                raise Exception('No root cluster is in use.')
            self.cluster: MOCV1alpha1Cluster = root_clusters_in_use[0]
        self.name = self.cluster.metadata.name
        root_secret = read_secret(self.k8s_client, 'root', self.name)
        self.mo = {
            'host': self.cluster.status.endpoint.address,
            'port': self.cluster.status.endpoint.port,
            'user': root_secret.get('username'),
            'password': root_secret.get('password')}

    def default_cns(self):
        cn_pods = []
        for pod in self.k8s_client.v1_api.list_namespaced_pod(self.name, label_selector='matrixorigin.io/component=CNSet'):
            cn_pod = CNPod(self.k8s_client, pod.metadata.name, self.name)
            if cn_pod.is_default:
                cn_pods.append(cn_pod)
        return cn_pods

    def limited_pool_cns(self):
        cn_pods = []
        for pod in self.k8s_client.v1_api.list_namespaced_pod(self.name, label_selector='matrixorigin.io/component=CNSet'):
            cn_pod = CNPod(self.k8s_client, pod.metadata.name, self.name)
            if cn_pod.is_in_limited_pool:
                cn_pods.append(cn_pod)
        return cn_pods

    def localpv_pool_cns(self):
        cn_pods = []
        for pod in self.k8s_client.v1_api.list_namespaced_pod(self.name, label_selector='matrixorigin.io/component=CNSet'):
            cn_pod = CNPod(self.k8s_client, pod.metadata.name, self.name)
            if cn_pod.is_in_localpv_pool:
                cn_pods.append(cn_pod)
        return cn_pods

    def bound_cns(self, _id):
        cn_pods = []
        for pod in self.k8s_client.v1_api.list_namespaced_pod(self.name, label_selector='matrixorigin.io/component=CNSet'):
            cn_pod = CNPod(self.k8s_client, pod.metadata.name, self.name)
            if cn_pod.is_bounded(_id):
                cn_pods.append(cn_pod)
        return cn_pods


class Cluster:

    def __init__(self, k8s_client: K8sClient, name):
        if k8s_client is None:
            k8s_client = K8sClient()
        self.k8s_client = k8s_client
        cluster = self.k8s_client.core_matrixone_cloud_v1alpha1_api.read_cluster(name)
        assert cluster[1] == 200, f"Failed to read cluster '{name}'."
        self.cluster: MOCV1alpha1Cluster = cluster[0]
        self.name = self.cluster.metadata.name
        self.account_id = self.cluster.spec.account_id
        self.main_cluster_ref = self.cluster.spec.main_cluster_ref
        self.phase: MOClusterPhase = MOClusterPhase(self.cluster.status.phase)
        self.cluster_type = self.cluster.metadata.labels.get('matrixone.cloud/cluster-type')
        self.plan_type = self.cluster.metadata.labels.get('matrixone.cloud/plan-type')
        self.organization = self.cluster.metadata.labels.get('matrixone.cloud/organization')
        self.version = self.cluster.status.version
        self.creation_timestamp = self.cluster.metadata.creation_timestamp
        self.type: MOClusterType = None
        if self.plan_type == 'standard':
            if self.cluster.spec.cn_sets:
                if self.cluster.spec.cn_sets[0].reserve_info.charge_type == 'PrePaid':
                    self.type = MOClusterType.standard_prepaid
                elif self.cluster.spec.cn_sets[0].reserve_info.charge_type == 'PostPaid':
                    self.type = MOClusterType.standard_postpaid
        elif self.plan_type == 'serverless':
            if self.cluster.spec.cn_sets:
                self.type = MOClusterType.serverless_paid
            else:
                self.type = MOClusterType.serverless_free

    @property
    def id_is_account_name(self):
        return self.cluster.metadata.labels.get('matrixone.cloud/internal-version') == '1'

    def cluster_is_in_expected_phase(self, expected_phase: MOClusterPhase):
        if self.phase == expected_phase:
            logger.debug(f"Cluster '{self.name}' is in phase of '{self.phase.value}' as expected.")
            return True
        else:
            logger.debug(f"Cluster '{self.name}' is in phase of '{self.phase.value}' but not '{expected_phase.value}'.")
            return False

    @property
    def is_active(self):
        return self.cluster_is_in_expected_phase(MOClusterPhase.active)

    @property
    def ip_white_list(self):
        return self.cluster.spec.endpoint.white_list_ip_ranges

    @property
    def expiration_date(self):
        if self.cluster.spec.cn_sets:
            if self.cluster.spec.cn_sets[0].reserve_info:
                return self.cluster.spec.cn_sets[0].reserve_info.expiration_date

    def get_cn_pods(self):
        if self.plan_type == 'standard':
            return [CNPod(self.k8s_client, pod.metadata.name, pod.metadata.namespace) for pod in
                    self.k8s_client.v1_api.list_namespaced_pod(self.name, label_selector=f'matrixorigin.io/component=CNSet').items]
        else:
            return [CNPod(self.k8s_client, pod.metadata.name, pod.metadata.namespace) for pod in
                    self.k8s_client.v1_api.list_namespaced_pod(self.main_cluster_ref, label_selector=f'matrixorigin.io/component=CNSet').items if pod.metadata.labels.get('matrixorigin.io/owner') == self.name]

    @property
    def cn_replicas(self):
        if self.cluster.spec.cn_sets:
            return self.cluster.spec.cn_sets[0].replicas

    @property
    def cn_resources(self):
        if self.cluster.spec.cn_sets:
            return self.cluster.spec.cn_sets[0].managed.resources

    @property
    def cn_profile(self):
        if self.cluster.spec.cn_sets:
            return self.cluster.spec.cn_sets[0].profile

    @property
    def cn_storage(self):
        if self.cluster.spec.cn_sets:
            return self.cluster.spec.cn_sets[0].managed.storage_class_name, self.cluster.spec.cn_sets[0].managed.storage_size

    @property
    def cn_unit(self):
        return self.cluster.spec.unit_selector.match_labels.get('matrixone.cloud/cloud'), self.cluster.spec.unit_selector.match_labels.get('matrixone.cloud/region')
