import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterStatusAliyunStatus(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'private_link': 'MOCV1alpha1ClusterStatusAliyunPrivateLink'
    }

    attribute_map = {
        'private_link': 'privateLink'
    }

    def __init__(self, private_link=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterStatusAliyunStatus - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._private_link = None
        self.discriminator = None

        if private_link is not None:
            self.private_link = private_link

    @property
    def private_link(self):
        """Gets the privateLink of this MOCV1alpha1ClusterStatusAliyunStatus.

        :return: The privateLink of this MOCV1alpha1ClusterStatusAliyunStatus.
        :rtype: MOCV1alpha1ClusterStatusAliyunPrivateLink
        """
        return self._private_link

    @private_link.setter
    def private_link(self, private_link):
        """Sets the privateLink of this MOCV1alpha1ClusterStatusAliyunStatus.

        :param private_link: The privateLink of this MOCV1alpha1ClusterStatusAliyunStatus.
        :type: MOCV1alpha1ClusterStatusAliyunPrivateLink
        """
        self._private_link = private_link

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
        if not isinstance(other, MOCV1alpha1ClusterStatusAliyunStatus):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterStatusAliyunStatus):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterStatusAliyunPrivateLink(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'service_id': 'str',
        'service_name': 'str',
        'zones': 'list[str]'
    }

    attribute_map = {
        'service_id': 'serviceID',
        'service_name': 'serviceName',
        'zones': 'zones'
    }

    def __init__(self, service_id=None, service_name=None, zones=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterStatusAliyunPrivateLink - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._service_id = None
        self._service_name = None
        self._zones = None
        self.discriminator = None

        if service_id is not None:
            self.service_id = service_id
        if service_name is not None:
            self.service_name = service_name
        if zones is not None:
            self.zones = zones

    @property
    def service_id(self):
        """Gets the serviceID of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :return: The serviceID of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :rtype: str
        """
        return self._service_id

    @service_id.setter
    def service_id(self, service_id):
        """Sets the serviceID of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :param service_id: The serviceID of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :type: str
        """
        self._service_id = service_id

    @property
    def service_name(self):
        """Gets the serviceName of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :return: The serviceName of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :rtype: str
        """
        return self._service_name

    @service_name.setter
    def service_name(self, service_name):
        """Sets the serviceName of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :param service_name: The serviceName of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :type: str
        """
        self._service_name = service_name

    @property
    def zones(self):
        """Gets the zones of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :return: The zones of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :rtype: list[str]
        """
        return self._zones

    @zones.setter
    def zones(self, zones):
        """Sets the zones of this MOCV1alpha1ClusterStatusAliyunPrivateLink.

        :param zones: The zones of this MOCV1alpha1ClusterStatusAliyunPrivateLink.
        :type: list[str]
        """
        self._zones = zones

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
        if not isinstance(other, MOCV1alpha1ClusterStatusAliyunPrivateLink):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterStatusAliyunPrivateLink):
            return True

        return self.to_dict() != other.to_dict()

