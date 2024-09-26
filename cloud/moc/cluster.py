import logging
from enum import Enum
from typing import List, Dict
from cloud.k8s.client import K8sClient
from cloud.moc import MOCV1alpha1Cluster


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
    serverless = 'serverless'
    standard = 'standard'


class MOCluster:

    def __init__(self, cluster: MOCV1alpha1Cluster):
        self.cluster = cluster
        self.name = cluster.metadata.name
        self.main_cluster_ref = cluster.spec.main_cluster_ref
        self.phase: MOClusterPhase = MOClusterPhase(cluster.status.phase if cluster.status else None)
        self.organization = None
        self.plan_type = None
        self.internal_version = None
        if cluster.metadata.labels:
            if 'matrixone.cloud/organization' in cluster.metadata.labels:
                self.organization = cluster.metadata.labels['matrixone.cloud/organization']
            if 'matrixone.cloud/plan-type' in cluster.metadata.labels:
                self.plan_type = cluster.metadata.labels['matrixone.cloud/plan-type']
            if 'matrixone.cloud/internal-version' in cluster.metadata.labels:
                self.internal_version = cluster.metadata.labels['matrixone.cloud/internal-version']

    @property
    def is_root(self):
        return self.main_cluster_ref is None

    @property
    def cluster(self):
        return self.__cluster

    @cluster.setter
    def cluster(self, cluster):
        self.__cluster = cluster

    @property
    def id_is_account_name(self):
        return self.internal_version == '1'

    def cluster_is_in_expected_phase(self, expected_phase: MOClusterPhase):
        if self.phase == expected_phase:
            logger.debug(f"Cluster '{self.name}' is in phase of '{self.phase.value}' as expected.")
            return True
        else:
            logger.debug(f"Cluster '{self.name}' is in phase of '{self.phase.value}' but not '{expected_phase.value}'.")
            return False

    def is_active(self):
        return self.cluster_is_in_expected_phase(MOClusterPhase.active)


class MOClusterManager:

    def __init__(self, k8s_client: K8sClient):
        self.__k8s_client = k8s_client
        self.__clusters: List[MOCV1alpha1Cluster] = []
        self.clusters: List[MOCluster] = []
        self.__instances: Dict[str: list] = {}
        self.__proxy_to_cluster = []
        self.refresh()
        # for c in self.clusters:
        #     if c.is_root:
        #         if 'matrixone.cloud/cordoned' in c.cluster.metadata.labels:
        #             pass
        #         else:
        #             self.__proxy_to_cluster.append(c.name)

    def refresh(self):
        clusters = self.__k8s_client.core_matrixone_cloud_v1alpha1_api.list_cluster()
        if clusters[1] == 200:
            self.__clusters = clusters[0].items
            self.clusters = []
            self.__instances = {}
            self.__proxy_to_cluster = []
            for c in clusters[0].items:
                cluster = MOCluster(c)
                self.clusters.append(cluster)
                if cluster.is_root:
                    if 'matrixone.cloud/cordoned' in cluster.cluster.metadata.labels:
                        pass
                    else:
                        self.__proxy_to_cluster.append(cluster.name)
                else:
                    if cluster.main_cluster_ref in self.__instances:
                        self.__instances[cluster.main_cluster_ref].append(cluster.name)
                    else:
                        self.__instances[cluster.main_cluster_ref] = [cluster.name]
        else:
            raise Exception('Failed to list clusters.')

    @property
    def root_clusters(self):
        return [c for c in self.clusters if c.is_root]

    def get_instances(self, name):
        self.refresh()
        if name in self.__instances:
            return self.__instances.get(name)
        else:
            return []

    def get_cluster(self, name):
        self.refresh()
        for c in self.clusters:
            if c.name == name:
                return c

    def set_proxy(self, name):
        if self.__k8s_client.name != 'controller':
            raise Exception("K8s client is not for 'controller' cluster.")
        if self.get_cluster(name):
            for cluster in self.root_clusters:
                if 'matrixone.cloud/cordoned' in cluster.cluster.metadata.labels:
                    if cluster.cluster.metadata.name == name:
                        cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = None
                    else:
                        cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = 'Y'
                else:
                    if cluster.cluster.metadata.name != name:
                        cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = 'Y'
                self.__k8s_client.core_matrixone_cloud_v1alpha1_api.patch_cluster(
                    cluster.cluster.metadata.name,
                    {"metadata": {"labels": cluster.cluster.metadata.labels}}
                )
            return True
        else:
            logger.warning(f"Cluster '{name}' is not found, won't modify the proxy.")
            return False

    def unset_proxy(self):
        if self.__k8s_client.name != 'controller':
            raise Exception('K8s client is not for controller cluster.')
        for cluster in self.root_clusters:
            if 'matrixone.cloud/cordoned' in cluster.cluster.metadata.labels:
                if cluster.cluster.metadata.name in self.__proxy_to_cluster:
                    cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = None
                else:
                    cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = 'Y'
            else:
                if cluster.cluster.metadata.name not in self.__proxy_to_cluster:
                    cluster.cluster.metadata.labels['matrixone.cloud/cordoned'] = 'Y'
            self.__k8s_client.core_matrixone_cloud_v1alpha1_api.patch_cluster(
                cluster.cluster.metadata.name, {'metadata': {'labels': cluster.cluster.metadata.labels}})


def cluster_is_in_expected_phase(k8s_client: K8sClient, name, expected_phase: MOClusterPhase):
    cluster = k8s_client.core_matrixone_cloud_v1alpha1_api.read_cluster(name)
    if cluster[1] == 200:
        if cluster[0].status.phase is None:
            return False
        if MOClusterPhase(cluster[0].status.phase) == expected_phase:
            logger.debug(f"Cluster '{name}' is in phase of '{cluster[0].status.phase}' as expected.")
            return True
        else:
            logger.debug(f"Cluster '{name}' is in phase of '{cluster[0].status.phase}' rather than '{expected_phase.value}'.")
            return False
    else:
        msg = f"Cluster '{name}' is not found."
        logger.error(msg)
        raise Exception(msg)


def cluster_is_active(k8s_client: K8sClient, name):
    return cluster_is_in_expected_phase(k8s_client, name, MOClusterPhase.active)
