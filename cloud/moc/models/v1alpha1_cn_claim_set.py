import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOIV1alpha1CNClaimSet(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'api_version': 'str',
        'kind': 'str',
        'metadata': 'V1ObjectMeta',
        'spec': 'MOIV1alpha1CNClaimSetSpec',
        'status': 'MOIV1alpha1CNClaimSetStatus'
    }

    attribute_map = {
        'api_version': 'apiVersion',
        'kind': 'kind',
        'metadata': 'metadata',
        'spec': 'spec',
        'status': 'status'
    }

    def __init__(self, api_version=None, kind=None, metadata=None, spec=None, status=None,
                 local_vars_configuration=None):
        """MOIV1alpha1CNClaimSet - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._api_version = None
        self._kind = None
        self._metadata = None
        self._spec = None
        self._status = None
        self.discriminator = None

        if api_version is not None:
            self.api_version = api_version
        if kind is not None:
            self.kind = kind
        if metadata is not None:
            self.metadata = metadata
        if spec is not None:
            self.spec = spec
        if status is not None:
            self.status = status

    @property
    def api_version(self):
        """Gets the api_version of this MOIV1alpha1CNClaimSet.

        :return: The api_version of this MOIV1alpha1CNClaimSet.
        :rtype: str
        """
        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        """Sets the api_version of this MOIV1alpha1CNClaimSet.

        :param api_version: The api_version of this MOIV1alpha1CNClaimSet.
        :type: str
        """

        self._api_version = api_version

    @property
    def kind(self):
        """Gets the kind of this MOIV1alpha1CNClaimSet.

        :return: The kind of this MOIV1alpha1CNClaimSet.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """Sets the kind of this MOIV1alpha1CNClaimSet.

        :param kind: The kind of this MOIV1alpha1CNClaimSet.
        :type: str
        """
        self._kind = kind

    @property
    def metadata(self):
        """Gets the metadata of this MOIV1alpha1CNClaimSet.

        :return: The metadata of this MOIV1alpha1CNClaimSet.
        :rtype: V1ObjectMeta
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this MOIV1alpha1CNClaimSet.

        :param metadata: The metadata of this MOIV1alpha1CNClaimSet.
        :type: V1ObjectMeta
        """
        self._metadata = metadata

    @property
    def spec(self):
        """Gets the spec of this MOIV1alpha1CNClaimSet.

        :return: The spec of this MOIV1alpha1CNClaimSet.
        :rtype: MOIV1alpha1CNClaimSetSpec
        """
        return self._spec

    @spec.setter
    def spec(self, spec):
        """Sets the spec of this MOIV1alpha1CNClaimSet.

        :param spec: The spec of this MOIV1alpha1CNClaimSet.
        :type: MOIV1alpha1CNClaimSetSpec
        """
        self._spec = spec

    @property
    def status(self):
        """Gets the status of this MOIV1alpha1CNClaimSet.

        :return: The status of this MOIV1alpha1CNClaimSet.
        :rtype: MOIV1alpha1CNClaimSetStatus
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this MOIV1alpha1CNClaimSet.

        :param status: The status of this MOIV1alpha1CNClaimSet.
        :type: MOIV1alpha1CNClaimSetStatus
        """

        self._status = status

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
        if not isinstance(other, MOIV1alpha1CNClaimSet):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOIV1alpha1CNClaimSet):
            return True

        return self.to_dict() != other.to_dict()
