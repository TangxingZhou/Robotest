import json
from yaml import safe_load
import os.path
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from jsonpath_ng.ext.parser import parse
from jsonpath_ng import Index, Slice, Fields, JSONPath


class JSONLib(object):

    ROBOT_LIBRARY_VERSION = 1.0
    ROBOT_EXIT_ON_FAILURE = True

    @classmethod
    def load_json_from_file(cls, file_path):
        """
        Load JSON from file.
        :param file_path: absolute json file path
        :return: json object (list or dictionary)
        Examples:
        | ${result}=  |  Load Json From File  | /path/to/file.json |
        """
        logger.debug("Check if file exists")
        if os.path.isfile(file_path) is False:
            logger.error("JSON file: " + file_path + " not found")
            raise IOError
        with open(file_path) as json_file:
            data = json.load(json_file)
        return data

    @classmethod
    def loads_strings_to_json(cls, str):
        """
        Dumps json object to strings.
        :param json_object: json as a dictionary object
        :return: str
        Examples:
        | ${result}=  |  Loads Strings To JSON  | json |
        """
        return json.loads(str)

    @classmethod
    def dumps_json_to_strings(cls, json_object):
        """
        Dumps json object to strings.
        :param json_object: json as a dictionary object
        :return: str
        Examples:
        | ${result}=  |  Dumps JSON To Strings  | json |
        """
        return json.dumps(json_object)

    @classmethod
    def convert_yaml_file_to_json(cls, file_path):
        """
        Load and convert YAML file to JSON.
        :param file_path: absolute yaml file path
        :return: json object (list or dictionary)
        Examples:
        | ${result}=  |  Convert YAML File To JSON  | /path/to/file.yaml |
        """
        logger.debug("Check if file exists")
        if os.path.isfile(file_path) is False:
            logger.error("YAML file: " + file_path + " not found")
            raise IOError
        with open(file_path) as yaml_file:
            return safe_load(yaml_file)

    @classmethod
    def add_object_to_json(cls, json_object, json_path, object_to_add):
        """
        Add an dictionary or list object to json object using json_path.
        :param json_object: json as a dictionary object
        :param json_path: jsonpath expression
        :param object_to_add: dictionary or list object to add to json_object which is matched by json_path
        :return: new json object
        Examples:
            | ${dict}=  | Create Dictionary    | latitude=13.1234 | longitude=130.1234 |
            | ${json}=  |  Add Object To Json  | ${json}          | $..address         |  ${dict} |
        """
        json_path_expr = parse(json_path)
        for match in json_path_expr.find(json_object):
            if type(match.value) is dict:
                match.value.update(object_to_add)
            if type(match.value) is list:
                match.value.append(object_to_add)
        return json_object

    @classmethod
    def get_value_from_json(cls, json_object, json_path):
        """
        Get Value From JSON using JSONPath.
        :param json_object: json as a dictionary object
        :param json_path: jsonpath expression
        :return: array of values
        Examples:
        | ${values}=  |  Get Value From Json  | ${json} |  $..phone_number |
        """
        json_path_expr = parse(json_path)
        matches = []
        try:
            matches = json_path_expr.find(json_object)
        except Exception as e:
            logger.error('Fails to parse the jsonpath {} for:\n{}\n{}'.format(json_path, json_object, e))
        return [match.value for match in matches]

    @classmethod
    def set_value_to_json(cls, json_object, json_path, value=None):
        """
        Update value to JSON using JSONPath.
        :param json_object: json as a dictionary object
        :param json_path: jsonpath expression for the target object
        :param value: value for the target object
        :return: updated json_object
        Examples:
        | ${json_object}=  |  Set Value To JSON | ${json} |  $.title  |  JSON |
        """
        if isinstance(json_path, JSONPath):
            json_path_ = json_path
        else:
            json_path_ = parse(json_path)
        parent_path_ = json_path_.left
        child_path_ = json_path_.right
        parent_matches = parent_path_.find(json_object)
        if parent_matches:
            for parent_match in parent_matches:
                if isinstance(parent_match.value, dict):
                    if isinstance(child_path_, Fields):
                        for field in child_path_.fields:
                            if isinstance(value, str):
                                if value.lower() in ('\'none\'', '"none"'):
                                    value = 'None'
                            parent_match.value[field] = value
                elif isinstance(parent_match.value, list):
                    child_matches = child_path_.find(parent_match.value)
                    if child_matches:
                        for child_match in child_matches:
                            if isinstance(child_match.path, Index):
                                parent_match.value[child_match.path.index] = value
                            elif isinstance(child_match.path, Slice):
                                for i in range(child_match.path.start, child_match.path.end, child_match.path.step):
                                    parent_match.value[i] = value
                    else:
                        if isinstance(child_path_, Index):
                            parent_match.value.append(value)
                        elif isinstance(child_path_, Slice):
                            for i in range(child_path_.start, child_path_.end, child_path_.step):
                                parent_match.value.append(value)
                elif parent_match.value is None:
                    if isinstance(child_path_, Fields):
                        parent_path_.update(json_object, {})
                    elif isinstance(child_path_, (Index, Slice)):
                        parent_path_.update(json_object, [])
                    return cls.set_value_to_json(json_object, json_path, value)
        else:
            if isinstance(child_path_, Fields):
                value_ = {child_path_.fields[0]: value}
            elif isinstance(child_path_, Index):
                value_ = ['' for i in range(child_path_.index)]
                value_.append(value)
            elif isinstance(child_path_, Slice):
                if child_path_.end is None:
                    raise ValueError('End should be set for the jsonpath.')
                else:
                    slice_ = [i for i in range(child_path_.end)][child_path_.start:child_path_.end:child_path_.step]
                    value_ = list(map(lambda i: value if i in slice_ else '', [i for i in range(child_path_.end)]))
            else:
                value_ = ''
            return cls.set_value_to_json(json_object, parent_path_, value_)
        return json_object

    @classmethod
    def set_values_to_json(cls, parent_path, json_object=None, **children):
        """
        Update sub elements for target object in JSON using JSONPath.
        :param json_object: json as a dictionary object
        :param parent_path: jsonpath expression for the parent object
        :param children: the pairs of jsonpath and value for the children
        :return: updated json_object
        Examples:
        | ${json_object}= | Set Values To JSON | $.people | ${json} | .name=JSON | .age=18 |
        """
        if json_object:
            new_json = json_object
        else:
            new_json = {}
        for k, v in children.items():
            if isinstance(v, dict):
                new_json = cls.set_values_to_json(parent_path + k, new_json, **v)
            elif isinstance(v, list):
                for index, val in enumerate(v):
                    new_json = cls.set_values_to_json(parent_path + k, new_json, **{'[{}]'.format(index): val})
            else:
                new_json = cls.set_value_to_json(new_json, parent_path + k, v)
        return new_json

    @classmethod
    def delete_object_from_json(cls, json_object, json_path):
        """
        Delete Object From JSON using json_path.
        :param json_object: json as a dictionary object
        :param json_path: jsonpath expression
        :return: new json_object
        Examples:
        | ${json_object}=  |  Delete Object From Json | ${json} |  $..address.streetAddress  |
        """
        json_path_expr = parse(json_path)
        for match in json_path_expr.find(json_object):
            path = match.path
            if isinstance(path, Index):
                del(match.context.value[match.path.index])
            elif isinstance(path, Fields):
                del(match.context.value[match.path.fields[0]])
        return json_object

    @classmethod
    def convert_json_to_string(cls, json_object):
        """
        Convert JSON object to string.
        :param json_object: json as a dictionary object
        :return: new json_string
        Examples:
        | ${json_str}=  |  Convert JSON To String | ${json_obj} |
        """
        return json.dumps(json_object)

    @classmethod
    def convert_string_to_json(cls, json_string):
        """
        Convert String to JSON object.
        :param json_string: JSON string
        :return: new json_object
        Examples:
        | ${json_object}=  |  Convert String to JSON | ${json_string} |
        """
        return json.loads(json_string)

    def json_field_should_be_equal(self, json_object, json_path, expected_value):
        """
        Check the field value of json.
        :param json_object: json as a dictionary object
        :param json_path: jsonpath expression
        :param expected_value: expected value for the field
        :return: None
        Examples:
        | JSON Field Should Be Equal | ${json_object} | ${json_path} | ${expected_value} |
        """
        BuiltIn().should_be_equal(self.get_value_from_json(json_object, json_path)[0], expected_value)
