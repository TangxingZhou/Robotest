import os
from kubernetes import config
from kubernetes.client import Configuration


class ClientConfig(object):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, config_file=None, **kwargs):
        if config_file:
            if os.path.isfile(config_file):
                config.load_kube_config(config_file)
            else:
                raise FileNotFoundError("Kube config file {} doesn't exists.".format(config_file))
        else:
            ClientConfig.set_default_client_configuration(**kwargs)

    @classmethod
    def set_default_client_configuration(cls, **kwargs):
        customized_config = Configuration()
        for k, v in kwargs.items():
            if hasattr(customized_config, k):
                setattr(customized_config, k, v)
        Configuration.set_default(customized_config)
