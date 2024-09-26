from __future__ import absolute_import

import sys

from cloud.moc.models.v1alpha1_cluster import MOCV1alpha1Cluster
from cloud.moc.models.v1alpha1_cluster_list import MOCV1alpha1ClusterList
from cloud.moc.models.v1alpha1_cluster_spec import MOCV1alpha1ClusterSpec
from cloud.moc.models.v1alpha1_cluster_spec_managed import *
from cloud.moc.models.v1alpha1_cluster_spec_cnsets import *
from cloud.moc.models.v1alpha1_cluster_spec_endpoint import *
from cloud.moc.models.v1alpha1_cluster_spec_unit_selector import *

from cloud.moc.models.v1alpha1_cluster_status import MOCV1alpha1ClusterStatus
from cloud.moc.models.v1alpha1_cluster_status_aliyun_status import *
from cloud.moc.models.v1alpha1_cluster_status_endpoint import MOCV1alpha1ClusterStatusEndpoint
from cloud.moc.models.v1alpha1_cn_claim_set import MOIV1alpha1CNClaimSet
from cloud.moc.models.v1alpha1_cn_claim_set_list import MOIV1alpha1CNClaimSetList
from cloud.moc.models.v1alpha1_cn_claim_set_spec import MOIV1alpha1CNClaimSetSpec
from cloud.moc.models.v1alpha1_cn_claim_set_status import MOIV1alpha1CNClaimSetStatus
from cloud.moc.models.v1alpha1_mo_cluster import MOIV1alpha1MOCluster
from cloud.moc.models.v1alpha1_mo_cluster_list import MOIV1alpha1MOClusterList
from cloud.moc.models.v1alpha1_mo_cluster_spec import MOIV1alpha1MOClusterSpec
from cloud.moc.models.v1alpha1_mo_cluster_status import MOIV1alpha1MOClusterStatus

setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1Cluster', MOCV1alpha1Cluster)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterList', MOCV1alpha1ClusterList)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpec', MOCV1alpha1ClusterSpec)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecManaged', MOCV1alpha1ClusterSpecManaged)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecManagedLocalServiceRef', MOCV1alpha1ClusterSpecManagedLocalServiceRef)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecManagedObjectStorage', MOCV1alpha1ClusterSpecManagedObjectStorage)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecCnSet', MOCV1alpha1ClusterSpecCnSet)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecCnSetScalingConfig', MOCV1alpha1ClusterSpecCnSetScalingConfig)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecCnSetReserveInfo', MOCV1alpha1ClusterSpecCnSetReserveInfo)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecCnSetManaged', MOCV1alpha1ClusterSpecCnSetManaged)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecEndpoint', MOCV1alpha1ClusterSpecEndpoint)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterSpecUnitSelector', MOCV1alpha1ClusterSpecUnitSelector)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterStatus', MOCV1alpha1ClusterStatus)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterStatusAliyunStatus', MOCV1alpha1ClusterStatusAliyunStatus)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterStatusAliyunPrivateLink', MOCV1alpha1ClusterStatusAliyunPrivateLink)
setattr(sys.modules.get('kubernetes.client.models'), 'MOCV1alpha1ClusterStatusEndpoint', MOCV1alpha1ClusterStatusEndpoint)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1CNClaimSet', MOIV1alpha1CNClaimSet)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1CNClaimSetList', MOIV1alpha1CNClaimSetList)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1CNClaimSetSpec', MOIV1alpha1CNClaimSetSpec)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1CNClaimSetStatus', MOIV1alpha1CNClaimSetStatus)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1MOCluster', MOIV1alpha1MOCluster)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1MOClusterList', MOIV1alpha1MOClusterList)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1MOClusterSpec', MOIV1alpha1MOClusterSpec)
setattr(sys.modules.get('kubernetes.client.models'), 'MOIV1alpha1MOClusterStatus', MOIV1alpha1MOClusterStatus)
