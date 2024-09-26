import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterSpecManaged(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'image_repository': 'str',
        'local_service_ref': 'MOCV1alpha1ClusterSpecManagedLocalServiceRef',
        'object_storage': 'MOCV1alpha1ClusterSpecManagedObjectStorage'
    }

    attribute_map = {
        'image_repository': 'imageRepository',
        'local_service_ref': 'localServiceRef',
        'object_storage': 'objectStorage'
    }

    def __init__(self, image_repository=None, local_service_ref=None, object_storage=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecManaged - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._image_repository = None
        self._local_service_ref = None
        self._object_storage = None
        self.discriminator = None

        if image_repository is not None:
            self.image_repository = image_repository
        if local_service_ref is not None:
            self.local_service_ref = local_service_ref
        if object_storage is not None:
            self.object_storage = object_storage

    @property
    def image_repository(self):
        """Gets the imageRepository of this MOCV1alpha1ClusterSpecManaged.

        :return: The imageRepository of this MOCV1alpha1ClusterSpecManaged.
        :rtype: str
        """
        return self._image_repository

    @image_repository.setter
    def image_repository(self, image_repository):
        """Sets the imageRepository of this MOCV1alpha1ClusterSpecManaged.

        :param image_repository: The imageRepository of this MOCV1alpha1ClusterSpecManaged.
        :type: str
        """
        self._image_repository = image_repository

    @property
    def local_service_ref(self):
        """Gets the localServiceRef of this MOCV1alpha1ClusterSpecManaged.

        :return: The localServiceRef of this MOCV1alpha1ClusterSpecManaged.
        :rtype: str
        """
        return self._local_service_ref

    @local_service_ref.setter
    def local_service_ref(self, local_service_ref):
        """Sets the localServiceRef of this MOCV1alpha1ClusterSpecManaged.

        :param local_service_ref: The localServiceRef of this MOCV1alpha1ClusterSpecManaged.
        :type: str
        """
        self._local_service_ref = local_service_ref

    @property
    def object_storage(self):
        """Gets the objectStorage of this MOCV1alpha1ClusterSpecManaged.

        :return: The objectStorage of this MOCV1alpha1ClusterSpecManaged.
        :rtype: int
        """
        return self._object_storage

    @object_storage.setter
    def object_storage(self, object_storage):
        """Sets the objectStorage of this MOCV1alpha1ClusterSpecManaged.

        :param object_storage: The objectStorage of this MOCV1alpha1ClusterSpecManaged.
        :type: int
        """
        self._object_storage = object_storage

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
        if not isinstance(other, MOCV1alpha1ClusterSpecManaged):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecManaged):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterSpecManagedLocalServiceRef(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'name': 'str'
    }

    attribute_map = {
        'name': 'name'
    }

    def __init__(self, name=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecManagedLocalServiceRef - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self.discriminator = None

        if name is not None:
            self.name = name

    @property
    def name(self):
        """Gets the name of this MOCV1alpha1ClusterSpecManagedLocalServiceRef.

        :return: The name of this MOCV1alpha1ClusterSpecManagedLocalServiceRef.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this MOCV1alpha1ClusterSpecManagedLocalServiceRef.

        :param name: The name of this MOCV1alpha1ClusterSpecManagedLocalServiceRef.
        :type: str
        """
        self._name = name

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
        if not isinstance(other, MOCV1alpha1ClusterSpecManagedLocalServiceRef):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecManagedLocalServiceRef):
            return True

        return self.to_dict() != other.to_dict()


class MOCV1alpha1ClusterSpecManagedObjectStorage(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'path': 'str',
        'region': 'str',
        'restored': 'bool'
    }

    attribute_map = {
        'path': 'path',
        'region': 'region',
        'restored': 'restored'
    }

    def __init__(self, path=None, region=None, restored=None, local_vars_configuration=None):
        """MOCV1alpha1ClusterSpecManagedObjectStorage - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._path = None
        self._region = None
        self._restored = None
        self.discriminator = None

        if path is not None:
            self.path = path
        if region is not None:
            self.region = region
        if restored is not None:
            self.restored = restored

    @property
    def path(self):
        """Gets the path of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :return: The path of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :param path: The path of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :type: str
        """
        self._path = path

    @property
    def region(self):
        """Gets the region of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :return: The region of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :param region: The region of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :type: str
        """
        self._region = region

    @property
    def restored(self):
        """Gets the restored of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :return: The restored of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :rtype: int
        """
        return self._restored

    @restored.setter
    def restored(self, restored):
        """Sets the restored of this MOCV1alpha1ClusterSpecManagedObjectStorage.

        :param restored: The restored of this MOCV1alpha1ClusterSpecManagedObjectStorage.
        :type: int
        """
        self._restored = restored

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
        if not isinstance(other, MOCV1alpha1ClusterSpecManagedObjectStorage):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpecManagedObjectStorage):
            return True

        return self.to_dict() != other.to_dict()
