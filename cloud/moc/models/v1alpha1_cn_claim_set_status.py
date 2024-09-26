import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOIV1alpha1CNClaimSetStatus(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'replicas': 'int',
        'ready_replicas': 'int',
    }

    attribute_map = {
        'replicas': 'replicas',
        'ready_replicas': 'readyReplicas'
    }

    def __init__(self, replicas=None, ready_replicas=None, local_vars_configuration=None):
        """MOIV1alpha1CNClaimSetStatus - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._replicas = None
        self._ready_replicas = None

        if replicas is not None:
            self.replicas = replicas
        if ready_replicas is not None:
            self.ready_replicas = ready_replicas

    @property
    def replicas(self):
        """Gets the replicas of this MOIV1alpha1CNClaimSetStatus.

        :return: The replicas of this MOIV1alpha1CNClaimSetStatus.
        :rtype: int
        """
        return self._replicas

    @replicas.setter
    def replicas(self, replicas):
        """Sets the replicas of this MOIV1alpha1CNClaimSetStatus.

        :param replicas: The replicas of this MOIV1alpha1CNClaimSetStatus.
        :type: int
        """
        self._replicas = replicas

    @property
    def ready_replicas(self):
        """Gets the readyReplicas of this MOIV1alpha1CNClaimSetStatus.

        :return: The readyReplicas of this MOIV1alpha1CNClaimSetStatus.
        :rtype: int
        """
        return self._ready_replicas

    @ready_replicas.setter
    def ready_replicas(self, ready_replicas):
        """Sets the readyReplicas of this MOIV1alpha1CNClaimSetStatus.

        :param ready_replicas: The readyReplicas of this MOIV1alpha1CNClaimSetStatus.
        :type: int
        """
        self._ready_replicas = ready_replicas

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
        if not isinstance(other, MOIV1alpha1CNClaimSetStatus):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOIV1alpha1CNClaimSetStatus):
            return True

        return self.to_dict() != other.to_dict()
