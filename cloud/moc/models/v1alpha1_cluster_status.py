import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterStatus(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'admin_url': 'str',
        'phase': 'str',
        'version': 'str',
        'endpoint': 'MOCV1alpha1ClusterStatusEndpoint',
        'aliyun_status': 'MOCV1alpha1ClusterStatusAliyunStatus',
        'conditions': 'list[V1Condition]'
    }

    attribute_map = {
        'admin_url': 'adminURL',
        'phase': 'phase',
        'version': 'version',
        'endpoint': 'endpoint',
        'aliyun_status': 'aliyunStatus',
        'conditions': 'conditions'
    }

    def __init__(self, admin_url=None, phase=None, version=None, endpoint=None, aliyun_status=None, conditions=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterStatus - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._admin_url = None
        self._phase = None
        self._version = None
        self._endpoint = None
        self._aliyun_status = None
        self._conditions = None
        self.discriminator = None

        if admin_url is not None:
            self.admin_url = admin_url
        if phase is not None:
            self.phase = phase
        if version is not None:
            self.version = version
        if endpoint is not None:
            self.endpoint = endpoint
        if aliyun_status is not None:
            self.aliyun_status = aliyun_status
        if conditions is not None:
            self.conditions = conditions

    @property
    def admin_url(self):
        """Gets the adminURL of this MOCV1alpha1ClusterStatus.

        :return: The adminURL of this MOCV1alpha1ClusterStatus.
        :rtype: str
        """
        return self._admin_url

    @admin_url.setter
    def admin_url(self, admin_url):
        """Sets the adminURL of this MOCV1alpha1ClusterStatus.

        :param admin_url: The adminURL of this MOCV1alpha1ClusterStatus.
        :type: str
        """
        self._admin_url = admin_url

    @property
    def phase(self):
        """Gets the phase of this MOCV1alpha1ClusterStatus.

        :return: The phase of this MOCV1alpha1ClusterStatus.
        :rtype: str
        """
        return self._phase

    @phase.setter
    def phase(self, phase):
        """Sets the phase of this MOCV1alpha1ClusterStatus.

        :param phase: The phase of this MOCV1alpha1ClusterStatus.
        :type: str
        """
        self._phase = phase

    @property
    def version(self):
        """Gets the version of this MOCV1alpha1ClusterStatus.

        :return: The version of this MOCV1alpha1ClusterStatus.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this MOCV1alpha1ClusterStatus.

        :param version: The version of this MOCV1alpha1ClusterStatus.
        :type: str
        """
        self._version = version

    @property
    def endpoint(self):
        """Gets the endpoint of this MOCV1alpha1ClusterStatus.

        :return: The endpoint of this MOCV1alpha1ClusterStatus.
        :rtype: MOCV1alpha1ClusterStatusEndpoint
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        """Sets the endpoint of this MOCV1alpha1ClusterStatus.

        :param endpoint: The endpoint of this MOCV1alpha1ClusterStatus.
        :type: MOCV1alpha1ClusterStatusEndpoint
        """
        self._endpoint = endpoint

    @property
    def aliyun_status(self):
        """Gets the aliyunStatus of this MOCV1alpha1ClusterStatus.

        :return: The aliyunStatus of this MOCV1alpha1ClusterStatus.
        :rtype: MOCV1alpha1ClusterStatusAliyunStatus
        """
        return self._aliyun_status

    @aliyun_status.setter
    def aliyun_status(self, aliyun_status):
        """Sets the aliyunStatus of this MOCV1alpha1ClusterStatus.

        :param aliyun_status: The aliyunStatus of this MOCV1alpha1ClusterStatus.
        :type: MOCV1alpha1ClusterStatusAliyunStatus
        """
        self._aliyun_status = aliyun_status

    @property
    def conditions(self):
        """Gets the conditions of this MOCV1alpha1ClusterStatus.

        :return: The conditions of this MOCV1alpha1ClusterStatus.
        :rtype: list[V1Condition]
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions):
        """Sets the conditions of this MOCV1alpha1ClusterStatus.

        :param conditions: The conditions of this MOCV1alpha1ClusterStatus.
        :type: list[V1Condition]
        """
        self._conditions = conditions

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
        if not isinstance(other, MOCV1alpha1ClusterStatus):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterStatus):
            return True

        return self.to_dict() != other.to_dict()
