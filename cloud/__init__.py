# import logging
# from utils.json import JSONFactory
#
#
# logger = logging.getLogger(__name__)
#
#
# def k8s_resource_field_should_be_equal(k8s_resource: dict, json_path: str, expected_value) -> int:
#     matches = JSONFactory.get_value_from_json(k8s_resource, json_path)
#     if matches:
#         for match in matches:
#             if match != expected_value:
#                 return 0
#     else:
#         return -1
#     return 1
