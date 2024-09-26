import logging
import base64
from enum import Enum
from cloud.k8s.client import K8sClient


logger = logging.getLogger(__name__)


class SecretType(Enum):
    opaque = 'Opaque'
    service_account_token = 'kubernetes.io/service-account-token'
    docker_cfg = 'kubernetes.io/dockercfg'
    docker_config_json = 'kubernetes.io/dockerconfigjson'
    basic_auth = 'kubernetes.io/basic-auth'
    ssh_auth = 'kubernetes.io/ssh-auth'
    tls = 'kubernetes.io/tls'
    token = 'bootstrap.kubernetes.io/token'


def read_secret(k8s_client: K8sClient, name: str, namespace: str, decode=True):
    secrets = [s.metadata.name for s in k8s_client.v1_api.list_namespaced_secret(namespace).items]
    if name in secrets:
        secret = k8s_client.v1_api.read_namespaced_secret(name, namespace)
        data = {}
        for k, v in secret.data.items():
            if decode:
                data[k] = base64.b64decode(v).decode()
            else:
                data[k] = v
        return data
    else:
        logger.debug(f"Secret {namespace}/{name} does not exist.")


def create_or_patch_secret(k8s_client: K8sClient,
                           name: str,
                           namespace: str,
                           stype: str = 'Opaque',
                           encrypted=False,
                           update_if_exists=False,
                           **kwargs):
    data = {}
    for k, v in kwargs.items():
        if encrypted:
            data[k] = v
        else:
            data[k] = base64.b64encode(v.encode()).decode()
    secrets = [s.metadata.name for s in k8s_client.v1_api.list_namespaced_secret(namespace).items]
    if name in secrets:
        if update_if_exists:
            logger.debug(f"Secret {name} already exists. Try to patch it with data: {data}.")
            return k8s_client.v1_api.patch_namespaced_secret(name, namespace, {'data': data})
        else:
            logger.debug(f"Secret {name} already exists. Skip to create it.")
    else:
        return k8s_client.v1_api.create_namespaced_secret(namespace, {
            'type': stype,
            'metadata': {
                'name': name
            },
            'data': data
        })


def create_docker_registry_secret(k8s_client: K8sClient,
                                  name: str,
                                  namespace: str,
                                  registry: str,
                                  username: str,
                                  password: str):
    secrets = [s.metadata.name for s in k8s_client.v1_api.list_namespaced_secret(namespace).items]
    if name in secrets:
        logger.debug(f"Secret '{name}' already exists. Skip to create it.")
    else:
        config_jsonf = "{{\"auths\":{{\"{}\":{{\"username\":\"{}\",\"password\":\"{}\",\"auth\":\"{}\"}}}}}}".format(
            registry,
            username,
            password,
            base64.b64encode(f"{username}:{password}".encode()).decode())
        return k8s_client.v1_api.create_namespaced_secret(
            namespace,
            {
                'type': 'kubernetes.io/dockerconfigjson',
                'metadata': {
                    'name': name
                },
                'data': {
                    '.dockerconfigjson': base64.b64encode(config_jsonf.encode()).decode()
                }
            }
        )
