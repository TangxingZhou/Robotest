import pprint
import re  # noqa: F401

import six

from kubernetes.client.configuration import Configuration


class MOCV1alpha1ClusterSpec(object):
    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'account_id': 'str',
        'main_cluster_ref': 'str',
        'readable_state': 'str',
        'state': 'str',
        'unit_name': 'str',
        'version': 'str',
        'managed': 'MOCV1alpha1ClusterSpecManaged',
        'cn_sets': 'list[MOCV1alpha1ClusterSpecCnSet]',
        'endpoint': 'MOCV1alpha1ClusterSpecEndpoint',
        'unit_selector': 'MOCV1alpha1ClusterSpecUnitSelector'
    }

    attribute_map = {
        'account_id': 'accountID',
        'main_cluster_ref': 'mainClusterRef',
        'readable_state': 'readableState',
        'state': 'state',
        'unit_name': 'unitName',
        'version': 'version',
        'managed': 'managed',
        'cn_sets': 'cnSets',
        'endpoint': 'endpoint',
        'unit_selector': 'unitSelector'
    }

    def __init__(self,
                 account_id=None,
                 main_cluster_ref=None,
                 readable_state=None,
                 state=None,
                 unit_name=None,
                 version=None,
                 managed=None,
                 cn_sets=None,
                 endpoint=None,
                 unit_selector=None,
                 local_vars_configuration=None):
        """MOCV1alpha1ClusterSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._account_id = None
        self._main_cluster_ref = None
        self._readable_state = None
        self._state = None
        self._unit_name = None
        self._version = None
        self._managed = None
        self._cn_sets = None
        self._endpoint = None
        self._unit_selector = None
        self.discriminator = None

        if account_id is not None:
            self.account_id = account_id
        if main_cluster_ref is not None:
            self.main_cluster_ref = main_cluster_ref
        if readable_state is not None:
            self.readable_state = readable_state
        if state is not None:
            self.state = state
        if unit_name is not None:
            self.unit_name = unit_name
        if version is not None:
            self.version = version
        if managed is not None:
            self.managed = managed
        if cn_sets is not None:
            self.cn_sets = cn_sets
        if endpoint is not None:
            self.endpoint = endpoint
        if unit_selector is not None:
            self.unit_selector = unit_selector

    @property
    def account_id(self):
        """Gets the accountID of this MOCV1alpha1ClusterSpec.

        :return: The accountID of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._account_id

    @account_id.setter
    def account_id(self, account_id):
        """Sets the accountID of this MOCV1alpha1ClusterSpec.

        :param account_id: The accountID of this MOCV1alpha1ClusterSpec.
        :type: str
        """
        self._account_id = account_id

    @property
    def main_cluster_ref(self):
        """Gets the mainClusterRef of this MOCV1alpha1ClusterSpec.

        :return: The mainClusterRef of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._main_cluster_ref

    @main_cluster_ref.setter
    def main_cluster_ref(self, main_cluster_ref):
        """Sets the mainClusterRef of this MOCV1alpha1ClusterSpec.

        :param main_cluster_ref: The mainClusterRef of this MOCV1alpha1ClusterSpec.
        :type: int
        """
        self._main_cluster_ref = main_cluster_ref

    @property
    def readable_state(self):
        """Gets the readableState of this MOCV1alpha1ClusterSpec.

        :return: The readableState of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._readable_state

    @readable_state.setter
    def readable_state(self, readable_state):
        """Sets the readableState of this MOCV1alpha1ClusterSpec.

        :param readable_state: The readableState of this MOCV1alpha1ClusterSpec.
        :type: str
        """
        self._readable_state = readable_state

    @property
    def state(self):
        """Gets the state of this MOCV1alpha1ClusterSpec.

        :return: The state of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this MOCV1alpha1ClusterSpec.

        :param state: The state of this MOCV1alpha1ClusterSpec.
        :type: str
        """
        self._state = state

    @property
    def unit_name(self):
        """Gets the unitName of this MOCV1alpha1ClusterSpec.

        :return: The unitName of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._unit_name

    @unit_name.setter
    def unit_name(self, unit_name):
        """Sets the unitName of this MOCV1alpha1ClusterSpec.

        :param unit_name: The unitName of this MOCV1alpha1ClusterSpec.
        :type: str
        """
        self._unit_name = unit_name

    @property
    def version(self):
        """Gets the version of this MOCV1alpha1ClusterSpec.

        :return: The version of this MOCV1alpha1ClusterSpec.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this MOCV1alpha1ClusterSpec.

        :param version: The version of this MOCV1alpha1ClusterSpec.
        :type: str
        """
        self._version = version

    @property
    def managed(self):
        """Gets the managed of this MOCV1alpha1ClusterSpec.

        :return: The managed of this MOCV1alpha1ClusterSpec.
        :rtype: MOCV1alpha1ClusterSpecManaged
        """
        return self._managed

    @managed.setter
    def managed(self, managed):
        """Sets the managed of this MOCV1alpha1ClusterSpec.

        :param managed: The managed of this MOCV1alpha1ClusterSpec.
        :type: MOCV1alpha1ClusterSpecManaged
        """
        self._managed = managed

    @property
    def cn_sets(self):
        """Gets the cnSets of this MOCV1alpha1ClusterSpec.

        cn_sets is the list of MOCV1alpha1ClusterSpecCnSet.

        :return: The cnSets of this MOCV1alpha1ClusterSpec.
        :rtype: list[MOCV1alpha1ClusterSpecCnSet]
        """
        return self._cn_sets

    @cn_sets.setter
    def cn_sets(self, cn_sets):
        """Sets the cnSets of this MOCV1alpha1ClusterSpec.

        cn_sets is the list of MOCV1alpha1ClusterSpecCnSet.

        :param cn_sets: The cnSets of this MOCV1alpha1ClusterSpec.
        :type: list[MOCV1alpha1ClusterSpecCnSet]
        """
        if self.local_vars_configuration.client_side_validation and cn_sets is None:
            raise ValueError("Invalid value for `cn_sets`, must not be `None`")
        self._cn_sets = cn_sets

    @property
    def endpoint(self):
        """Gets the endpoint of this MOCV1alpha1ClusterSpec.

        :return: The endpoint of this MOCV1alpha1ClusterSpec.
        :rtype: MOCV1alpha1ClusterSpecEndpoint
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        """Sets the endpoint of this MOCV1alpha1ClusterSpec.

        :param endpoint: The endpoint of this MOCV1alpha1ClusterSpec.
        :type: MOCV1alpha1ClusterSpecEndpoint
        """
        if self.local_vars_configuration.client_side_validation and endpoint is None:
            raise ValueError("Invalid value for `endpoint`, must not be `None`")
        self._endpoint = endpoint

    @property
    def unit_selector(self):
        """Gets the unitSelector of this MOCV1alpha1ClusterSpec.

        :return: The unitSelector of this MOCV1alpha1ClusterSpec.
        :rtype: MOCV1alpha1ClusterSpecUnitSelector
        """
        return self._unit_selector

    @unit_selector.setter
    def unit_selector(self, unit_selector):
        """Sets the unitSelector of this MOCV1alpha1ClusterSpec.

        :param unit_selector: The unitSelector of this MOCV1alpha1ClusterSpec.
        :type: MOCV1alpha1ClusterSpecUnitSelector
        """
        if self.local_vars_configuration.client_side_validation and unit_selector is None:
            raise ValueError("Invalid value for `unitSelector`, must not be `None`")
        self._unit_selector = unit_selector

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
        if not isinstance(other, MOCV1alpha1ClusterSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MOCV1alpha1ClusterSpec):
            return True

        return self.to_dict() != other.to_dict()
