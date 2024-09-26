import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterSpecUnitSelector(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'match_labels': 'dict(str, str)'
    }

    attribute_map = {
        'match_labels': 'matchLabels'
    }

    def __init__(self, match_labels=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecUnitSelector - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._match_labels = None
        self.discriminator = None

        if match_labels is not None:
            self.match_labels = match_labels

    @property
    def match_labels(self):
        """Gets the matchLabels of this MOCV1alpha1ClusterSpecUnitSelector.

        :return: The matchLabels of this MOCV1alpha1ClusterSpecUnitSelector.
        :rtype: dict(str, str)
        """
        return self._match_labels

    @match_labels.setter
    def match_labels(self, match_labels):
        """Sets the matchLabels of this MOCV1alpha1ClusterSpecUnitSelector.

        :param match_labels: The matchLabels of this MOCV1alpha1ClusterSpecUnitSelector.
        :type: dict(str, str)
        """
        self._match_labels = match_labels

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
        if not isinstance(other, MOCV1alpha1ClusterSpecUnitSelector):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecUnitSelector):
            return True

        return self.to_dict() != other.to_dict()
