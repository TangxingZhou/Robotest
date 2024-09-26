import re
import time
import logging
from enum import Enum
from functools import reduce
from kubernetes.watch import watch
from cloud.k8s.client import K8sClient


logger = logging.getLogger(__name__)


def watch_namespaced_events(k8s_client: K8sClient, namespace, duration=0, *keywords, **kwargs):
    start = time.time()
    _watch = watch.Watch()
    if 'tail_lines' not in kwargs:
        kwargs['tail_lines'] = 0
    if keywords:
        logger.info(f'Start to watch events in namespace: {namespace}')
        for log in _watch.stream(k8s_client.events_v1_api.list_namespaced_event, namespace, **kwargs):
            if reduce(lambda x, y: x and y, map(lambda k: True if re.search(re.compile(k), log) else False, keywords)):
                _watch.stop()
                logger.info(f"Log line '{log}' matches the regex expressions: {', '.join(keywords)}")
                return True
            if time.time() - start >= duration:
                _watch.stop()
    return False
