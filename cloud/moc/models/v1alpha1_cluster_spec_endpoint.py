import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterSpecEndpoint(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'mode': 'str',
        'white_list_ip_ranges': 'list[str]'
    }

    attribute_map = {
        'mode': 'mode',
        'white_list_ip_ranges': 'whitelistIPRanges'
    }

    def __init__(self, mode=None, white_list_ip_ranges=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecEndpoint - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._mode = None
        self._white_list_ip_ranges = None
        self.discriminator = None

        if mode is not None:
            self.mode = mode
        if white_list_ip_ranges is not None:
            self.white_list_ip_ranges = white_list_ip_ranges

    @property
    def mode(self):
        """Gets the mode of this MOCV1alpha1ClusterSpecEndpoint.

        :return: The mode of this MOCV1alpha1ClusterSpecEndpoint.
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Sets the mode of this MOCV1alpha1ClusterSpecEndpoint.

        :param mode: The name of this MOCV1alpha1ClusterSpecEndpoint.
        :type: str
        """
        self._mode = mode

    @property
    def white_list_ip_ranges(self):
        """Gets the whitelistIPRanges of this MOCV1alpha1ClusterSpecEndpoint.

        :return: The whitelistIPRanges of this MOCV1alpha1ClusterSpecEndpoint.
        :rtype: list[str]
        """
        return self._white_list_ip_ranges

    @white_list_ip_ranges.setter
    def white_list_ip_ranges(self, white_list_ip_ranges):
        """Sets the whitelistIPRanges of this MOCV1alpha1ClusterSpecEndpoint.

        :param white_list_ip_ranges: The whitelistIPRanges of this MOCV1alpha1ClusterSpecEndpoint.
        :type: list[str]
        """
        self._white_list_ip_ranges = white_list_ip_ranges

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
        if not isinstance(other, MOCV1alpha1ClusterSpecEndpoint):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecEndpoint):
            return True

        return self.to_dict() != other.to_dict()
