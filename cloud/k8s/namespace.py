import logging
from enum import Enum
from cloud.k8s.client import K8sClient


logger = logging.getLogger(__name__)


def create_ns(k8s_client: K8sClient, name: str):
    namespaces = [s.metadata.name for s in k8s_client.v1_api.list_namespace().items]
    if name in namespaces:
        logger.debug(f"Namespace '{name}' already exists. Skip to create it.")
    else:
        return k8s_client.v1_api.create_namespace({'metadata': {'name': name}})


def namespaces_exist(k8s_client: K8sClient, *namespaces, **kwargs):
    all_namespaces = [n.metadata.name for n in k8s_client.v1_api.list_namespace(**kwargs).items]
    cnt = None
    for name in namespaces:
        if cnt is None:
            cnt = 0
        if name in all_namespaces:
            cnt += 1
    if cnt:
        return len(namespaces) == cnt
    else:
        return None
