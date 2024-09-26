import re
import time
import logging
from enum import Enum
from functools import reduce
from kubernetes.watch import watch
from cloud.k8s.client import K8sClient


logger = logging.getLogger(__name__)


class PodPhase(Enum):
    running = 'Running'
    succeeded = 'Succeeded'
    pending = 'Pending'
    failed = 'Failed'
    unknown = 'Unknown'
    # TODO: to add more phase values


def namespaced_pods_are_running(k8s_client: K8sClient, namespace, **kwargs):
    for pod in k8s_client.v1_api.list_namespaced_pod(namespace, **kwargs).items:
        if PodPhase(pod.status.phase) != PodPhase.running:
            logger.debug(f"Pod '{namespace}/{pod.metadata.name}' is in phase of '{pod.status.phase}' not 'Running'.")
            return False
    return True


def namespaced_pod_is_running(k8s_client: K8sClient, name, namespace):
    return namespaced_pod_is_in_expected_phase(k8s_client, name, namespace, PodPhase.running)


def namespaced_pod_successfully_completed(k8s_client: K8sClient, name, namespace):
    pod = k8s_client.v1_api.read_namespaced_pod(name, namespace)
    if PodPhase(pod.status.phase) == PodPhase.failed:
        logs = k8s_client.v1_api.read_namespaced_pod_log(name, namespace)
        logger.debug(logs)
        raise Exception(f"Pod '{namespace}/{name}' failed to complete.")
    elif PodPhase(pod.status.phase) == PodPhase.succeeded:
        return True
    else:
        return False


def namespaced_pod_is_in_expected_phase(k8s_client: K8sClient, name, namespace, expected_phase: PodPhase):
    pod = k8s_client.v1_api.read_namespaced_pod(name, namespace)
    if PodPhase(pod.status.phase) == expected_phase:
        return True
    else:
        return False


def namespaced_pod_exists(k8s_client: K8sClient, name, namespace, **kwargs):
    if name:
        return name in [p.metadata.name for p in k8s_client.v1_api.list_namespaced_pod(namespace, **kwargs).items]
    else:
        return len([p.metadata.name for p in k8s_client.v1_api.list_namespaced_pod(namespace, **kwargs).items]) > 0


def watch_namespaced_pod_logs(k8s_client: K8sClient, name, namespace, duration=5, *keywords, **kwargs):
    start = time.time()
    _watch = watch.Watch()
    if 'tail_lines' not in kwargs:
        kwargs['tail_lines'] = 0
    if keywords:
        logger.info(f'Start to watch logs of pod {namespace}/{name}')
        for log in _watch.stream(k8s_client.v1_api.read_namespaced_pod_log, name, namespace, **kwargs):
            if reduce(lambda x, y: x and y, map(lambda k: True if re.search(re.compile(k), log) else False, keywords)):
                _watch.stop()
                logger.info(f"Log line '{log}' matches the regex expressions: {', '.join(keywords)}")
                return True
            if time.time() - start >= duration:
                _watch.stop()
    return False
