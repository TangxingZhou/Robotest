import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterSpecCnSet(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'name': 'str',
        'profile': 'str',
        'replicas': 'int',
        'reserve_info': 'MOCV1alpha1ClusterSpecCnSetReserveInfo',
        'scaling_config': 'MOCV1alpha1ClusterSpecCnSetScalingConfig',
        'managed': 'MOCV1alpha1ClusterSpecCnSetManaged'
    }

    attribute_map = {
        'name': 'name',
        'profile': 'profile',
        'replicas': 'replicas',
        'reserve_info': 'reserveInfo',
        'scaling_config': 'scalingConfig',
        'managed': 'managed'
    }

    def __init__(self, name=None, profile=None, replicas=None, reserve_info=None, scaling_config=None, managed=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecCnSet - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._profile = None
        self._replicas = None
        self._reserve_info = None
        self._scaling_config = None
        self._managed = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if profile is not None:
            self.profile = profile
        if replicas is not None:
            self.replicas = replicas
        if reserve_info is not None:
            self.reserve_info = reserve_info
        if scaling_config is not None:
            self.scaling_config = scaling_config
        if managed is not None:
            self.managed = managed

    @property
    def name(self):
        """Gets the name of this MOCV1alpha1ClusterSpecCnSet.

        :return: The name of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this MOCV1alpha1ClusterSpecCnSet.

        :param name: The name of this MOCV1alpha1ClusterSpecCnSet.
        :type: str
        """
        self._name = name

    @property
    def profile(self):
        """Gets the profile of this MOCV1alpha1ClusterSpecCnSet.

        :return: The profile of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: str
        """
        return self._profile

    @profile.setter
    def profile(self, profile):
        """Sets the profile of this MOCV1alpha1ClusterSpecCnSet.

        :param profile: The profile of this MOCV1alpha1ClusterSpecCnSet.
        :type: str
        """
        self._profile = profile

    @property
    def replicas(self):
        """Gets the kind of this MOCV1alpha1ClusterSpecCnSet.

        :return: The kind of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: int
        """
        return self._replicas

    @replicas.setter
    def replicas(self, replicas):
        """Sets the replicas of this MOCV1alpha1ClusterSpecCnSet.

        :param replicas: The replicas of this MOCV1alpha1ClusterSpecCnSet.
        :type: int
        """
        self._replicas = replicas

    @property
    def reserve_info(self):
        """Gets the reserveInfo of this MOCV1alpha1ClusterSpecCnSet.

        :return: The reserveInfo of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: MOCV1alpha1ClusterSpecCnSetReserveInfo
        """
        return self._reserve_info

    @reserve_info.setter
    def reserve_info(self, reserve_info):
        """Sets the reserveInfo of this MOCV1alpha1ClusterSpecCnSet.

        :param reserve_info: The reserveInfo of this MOCV1alpha1ClusterSpecCnSet.
        :type: MOCV1alpha1ClusterSpecCnSetReserveInfo
        """
        self._reserve_info = reserve_info

    @property
    def scaling_config(self):
        """Gets the scalingConfig of this MOCV1alpha1ClusterSpecCnSet.

        :return: The scalingConfig of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: MOCV1alpha1ClusterSpecCnSetScalingConfig
        """
        return self._scaling_config

    @scaling_config.setter
    def scaling_config(self, scaling_config):
        """Sets the scalingConfig of this MOCV1alpha1ClusterSpecCnSet.

        :param scaling_config: The scalingConfig of this MOCV1alpha1ClusterSpecCnSet.
        :type: MOCV1alpha1ClusterSpecCnSetScalingConfig
        """
        self._scaling_config = scaling_config

    @property
    def managed(self):
        """Gets the managed of this MOCV1alpha1ClusterSpecCnSet.

        :return: The managed of this MOCV1alpha1ClusterSpecCnSet.
        :rtype: MOCV1alpha1ClusterSpecCnSetManaged
        """
        return self._managed

    @managed.setter
    def managed(self, managed):
        """Sets the managed of this MOCV1alpha1ClusterSpecCnSet.

        :param managed: The managed of this MOCV1alpha1ClusterSpecCnSet.
        :type: MOCV1alpha1ClusterSpecCnSetManaged
        """
        self._managed = managed

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSet):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSet):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterSpecCnSetScalingConfig(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'max_replicas': 'int',
        'min_replicas': 'int',
        'policy': 'str'
    }

    attribute_map = {
        'max_replicas': 'maxReplicas',
        'min_replicas': 'minReplicas',
        'policy': 'policy'
    }

    def __init__(self, max_replicas=None, min_replicas=None, policy=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecCnSetScalingConfig - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._max_replicas = None
        self._min_replicas = None
        self._policy = None
        self.discriminator = None

        if max_replicas is not None:
            self.max_replicas = max_replicas
        if min_replicas is not None:
            self.min_replicas = min_replicas
        if policy is not None:
            self.policy = policy

    @property
    def max_replicas(self):
        """Gets the maxReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :return: The maxReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :rtype: int
        """
        return self._max_replicas

    @max_replicas.setter
    def max_replicas(self, max_replicas):
        """Sets the maxReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :param max_replicas: The maxReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :type: int
        """
        self._max_replicas = max_replicas

    @property
    def min_replicas(self):
        """Gets the minReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :return: The minReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :rtype: int
        """
        return self._min_replicas

    @min_replicas.setter
    def min_replicas(self, min_replicas):
        """Sets the minReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :param min_replicas: The minReplicas of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :type: int
        """
        self._min_replicas = min_replicas

    @property
    def policy(self):
        """Gets the policy of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :return: The policy of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :rtype: str
        """
        return self._policy

    @policy.setter
    def policy(self, policy):
        """Sets the policy of this MOCV1alpha1ClusterSpecCnSetScalingConfig.

        :param policy: The policy of this MOCV1alpha1ClusterSpecCnSetScalingConfig.
        :type: str
        """
        self._policy = policy

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetScalingConfig):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetScalingConfig):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterSpecCnSetReserveInfo(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'charge_type': 'str',
        'expiration_date': 'str',
        'is_reserved': 'bool'
    }

    attribute_map = {
        'charge_type': 'chargeType',
        'expiration_date': 'expirationDate',
        'is_reserved': 'isReserved'
    }

    def __init__(self, charge_type=None, expiration_date=None, is_reserved=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecCnSetReserveInfo - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._charge_type = None
        self._expiration_date = None
        self._is_reserved = None
        self.discriminator = None

        if charge_type is not None:
            self.charge_type = charge_type
        if expiration_date is not None:
            self.expiration_date = expiration_date
        if is_reserved is not None:
            self.is_reserved = is_reserved

    @property
    def charge_type(self):
        """Gets the chargeType of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :return: The chargeType of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :rtype: str
        """
        return self._charge_type

    @charge_type.setter
    def charge_type(self, charge_type):
        """Sets the chargeType of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :param charge_type: The chargeType of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :type: str
        """
        self._charge_type = charge_type

    @property
    def expiration_date(self):
        """Gets the expirationDate of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :return: The expirationDate of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :rtype: str
        """
        return self._expiration_date

    @expiration_date.setter
    def expiration_date(self, expiration_date):
        """Sets the expirationDate of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :param expiration_date: The expirationDate of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :type: str
        """
        self._expiration_date = expiration_date

    @property
    def is_reserved(self):
        """Gets the isReserved of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :return: The isReserved of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :rtype: bool
        """
        return self._is_reserved

    @is_reserved.setter
    def is_reserved(self, is_reserved):
        """Sets the isReserved of this MOCV1alpha1ClusterSpecCnSetReserveInfo.

        :param is_reserved: The isReserved of this MOCV1alpha1ClusterSpecCnSetReserveInfo.
        :type: bool
        """
        self._is_reserved = is_reserved

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetReserveInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetReserveInfo):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterSpecCnSetManaged(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'component_backend': 'str',
        'resources': 'V1ResourceRequirements',
        'storage_class_name': 'str',
        'storage_size': 'str'
    }

    attribute_map = {
        'component_backend': 'componentBackend',
        'resources': 'resources',
        'storage_class_name': 'storageClassName',
        'storage_size': 'storageSize'
    }

    def __init__(self, component_backend=None, resources=None, storage_class_name=None, storage_size=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecCnSetManaged - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._component_backend = None
        self._resources = None
        self._storage_class_name = None
        self._storage_size = None
        self.discriminator = None

        if component_backend is not None:
            self.component_backend = component_backend
        if resources is not None:
            self.resources = resources
        if storage_class_name is not None:
            self.storage_class_name = storage_class_name
        if storage_size is not None:
            self.storage_size = storage_size

    @property
    def component_backend(self):
        """Gets the componentBackend of this MOCV1alpha1ClusterSpecCnSetManaged.

        :return: The componentBackend of this MOCV1alpha1ClusterSpecCnSetManaged.
        :rtype: str
        """
        return self._component_backend

    @component_backend.setter
    def component_backend(self, component_backend):
        """Sets the componentBackend of this MOCV1alpha1ClusterSpecCnSetManaged.

        :param component_backend: The componentBackend of this MOCV1alpha1ClusterSpecCnSetManaged.
        :type: str
        """
        self._component_backend = component_backend

    @property
    def resources(self):
        """Gets the resources of this MOCV1alpha1ClusterSpecCnSetManaged.

        :return: The resources of this MOCV1alpha1ClusterSpecCnSetManaged.
        :rtype: V1ResourceRequirements
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """Sets the resources of this MOCV1alpha1ClusterSpecCnSetManaged.

        :param resources: The expirationDate of this MOCV1alpha1ClusterSpecCnSetManaged.
        :type: V1ResourceRequirements
        """
        self._resources = resources

    @property
    def storage_class_name(self):
        """Gets the storageClassName of this MOCV1alpha1ClusterSpecCnSetManaged.

        :return: The storageClassName of this MOCV1alpha1ClusterSpecCnSetManaged.
        :rtype: str
        """
        return self._storage_class_name

    @storage_class_name.setter
    def storage_class_name(self, storage_class_name):
        """Sets the storageClassName of this MOCV1alpha1ClusterSpecCnSetManaged.

        :param storage_class_name: The storageClassName of this MOCV1alpha1ClusterSpecCnSetManaged.
        :type: str
        """
        self._storage_class_name = storage_class_name

    @property
    def storage_size(self):
        """Gets the storageSize of this MOCV1alpha1ClusterSpecCnSetManaged.

        :return: The storageSize of this MOCV1alpha1ClusterSpecCnSetManaged.
        :rtype: str
        """
        return self._storage_size

    @storage_size.setter
    def storage_size(self, storage_size):
        """Sets the storageSize of this MOCV1alpha1ClusterSpecCnSetManaged.

        :param storage_size: The storageSize of this MOCV1alpha1ClusterSpecCnSetManaged.
        :type: str
        """
        self._storage_size = storage_size

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetManaged):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecCnSetManaged):
            return True

        return self.to_dict() != other.to_dict()
