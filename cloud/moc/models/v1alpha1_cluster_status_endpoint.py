import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterStatusEndpoint(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'address': 'str',
        'phase': 'str',
        'https_port': 'int',
        'port': 'int'
    }

    attribute_map = {
        'address': 'address',
        'phase': 'phase',
        'https_port': 'httpsPort',
        'port': 'port'
    }

    def __init__(self, address=None, phase=None, https_port=None, port=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterStatusEndpoint - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._address = None
        self._phase = None
        self._https_port = None
        self._port = None
        self.discriminator = None

        if address is not None:
            self.address = address
        if phase is not None:
            self.phase = phase
        if https_port is not None:
            self.https_port = https_port
        if port is not None:
            self.port = port

    @property
    def address(self):
        """Gets the address of this MOCV1alpha1ClusterStatusEndpoint.

        :return: The address of this MOCV1alpha1ClusterStatusEndpoint.
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this MOCV1alpha1ClusterStatusEndpoint.

        :param address: The address of this MOCV1alpha1ClusterStatusEndpoint.
        :type: str
        """
        self._address = address

    @property
    def phase(self):
        """Gets the phase of this MOCV1alpha1ClusterStatusEndpoint.

        :return: The phase of this MOCV1alpha1ClusterStatusEndpoint.
        :rtype: str
        """
        return self._phase

    @phase.setter
    def phase(self, phase):
        """Sets the phase of this MOCV1alpha1ClusterStatusEndpoint.

        :param phase: The phase of this MOCV1alpha1ClusterStatusEndpoint.
        :type: str
        """
        self._phase = phase

    @property
    def https_port(self):
        """Gets the httpsPort of this MOCV1alpha1ClusterStatusEndpoint.

        :return: The httpsPort of this MOCV1alpha1ClusterStatusEndpoint.
        :rtype: int
        """
        return self._https_port

    @https_port.setter
    def https_port(self, https_port):
        """Sets the httpsPort of this MOCV1alpha1ClusterStatusEndpoint.

        :param https_port: The httpsPort of this MOCV1alpha1ClusterStatusEndpoint.
        :type: int
        """
        self._https_port = https_port

    @property
    def port(self):
        """Gets the port of this MOCV1alpha1ClusterStatusEndpoint.

        :return: The port of this MOCV1alpha1ClusterStatusEndpoint.
        :rtype: int
        """
        return self._port

    @port.setter
    def port(self, port):
        """Sets the port of this MOCV1alpha1ClusterStatusEndpoint.

        :param port: The port of this MOCV1alpha1ClusterStatusEndpoint.
        :type: int
        """
        self._port = port

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
        if not isinstance(other, MOCV1alpha1ClusterStatusEndpoint):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterStatusEndpoint):
            return True

        return self.to_dict() != other.to_dict()
