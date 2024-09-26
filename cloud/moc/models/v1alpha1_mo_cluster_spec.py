import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOIV1alpha1MOClusterSpec(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'image_repository': 'str',
        'image_pull_policy': 'str',
        'metric_reader_enabled': 'bool',
        'restore_from': 'str',
        'version': 'str'
    }

    attribute_map = {
        'image_repository': 'imageRepository',
        'image_pull_policy': 'imagePullPolicy',
        'metric_reader_enabled': 'metricReaderEnabled',
        'restore_from': 'restoreFrom',
        'version': 'version'
    }

    def __init__(self,
                 image_repository=None,
                 image_pull_policy=None,
                 metric_reader_enabled=None,
                 restore_from=None,
                 version=None,
                 local_vars_configuration=None):
        """MOIV1alpha1MOClusterSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._image_repository = None
        self._image_pull_policy = None
        self._metric_reader_enabled = None
        self._restore_from = None
        self._version = None
        self.discriminator = None

        if image_repository is not None:
            self.image_repository = image_repository
        if image_pull_policy is not None:
            self.image_pull_policy = image_pull_policy
        if metric_reader_enabled is not None:
            self.metric_reader_enabled = metric_reader_enabled
        if restore_from is not None:
            self.restore_from = restore_from
        if version is not None:
            self.version = version

    @property
    def image_repository(self):
        """Gets the imageRepository of this MOIV1alpha1MOClusterSpec.

        :return: The imageRepository of this MOIV1alpha1MOClusterSpec.
        :rtype: str
        """
        return self._image_repository

    @image_repository.setter
    def image_repository(self, image_repository):
        """Sets the imageRepository of this MOIV1alpha1MOClusterSpec.

        :param image_repository: The imageRepository of this MOIV1alpha1MOClusterSpec.
        :type: str
        """
        self._image_repository = image_repository

    @property
    def image_pull_policy(self):
        """Gets the imagePullPolicy of this MOIV1alpha1MOClusterSpec.

        :return: The imagePullPolicy of this MOIV1alpha1MOClusterSpec.
        :rtype: str
        """
        return self._image_pull_policy

    @image_pull_policy.setter
    def image_pull_policy(self, image_pull_policy):
        """Sets the imagePullPolicy of this MOIV1alpha1MOClusterSpec.

        :param image_pull_policy: The imagePullPolicy of this MOIV1alpha1MOClusterSpec.
        :type: int
        """
        self._image_pull_policy = image_pull_policy

    @property
    def metric_reader_enabled(self):
        """Gets the metricReaderEnabled of this MOIV1alpha1MOClusterSpec.

        :return: The metricReaderEnabled of this MOIV1alpha1MOClusterSpec.
        :rtype: bool
        """
        return self._metric_reader_enabled

    @metric_reader_enabled.setter
    def metric_reader_enabled(self, metric_reader_enabled):
        """Sets the metricReaderEnabled of this MOIV1alpha1MOClusterSpec.

        :param metric_reader_enabled: The metricReaderEnabled of this MOIV1alpha1MOClusterSpec.
        :type: bool
        """
        self._metric_reader_enabled = metric_reader_enabled

    @property
    def restore_from(self):
        """Gets the restoreFrom of this MOIV1alpha1MOClusterSpec.

        :return: The restoreFrom of this MOIV1alpha1MOClusterSpec.
        :rtype: str
        """
        return self._restore_from

    @restore_from.setter
    def restore_from(self, restore_from):
        """Sets the restoreFrom of this MOIV1alpha1MOClusterSpec.

        :param restore_from: The restoreFrom of this MOIV1alpha1MOClusterSpec.
        :type: str
        """
        self._restore_from = restore_from

    @property
    def version(self):
        """Gets the version of this MOIV1alpha1MOClusterSpec.

        :return: The version of this MOIV1alpha1MOClusterSpec.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this MOIV1alpha1MOClusterSpec.

        :param version: The version of this MOIV1alpha1MOClusterSpec.
        :type: str
        """
        self._version = version

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
        if not isinstance(other, MOIV1alpha1MOClusterSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOIV1alpha1MOClusterSpec):
            return True

        return self.to_dict() != other.to_dict()
