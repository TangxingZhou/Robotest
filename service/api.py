from __future__ import absolute_import

import re
import datetime
import inspect
import importlib
from enum import EnumMeta
from .models import BaseModel

# from urllib3.exceptions import TimeoutError
import allure
import six
import logging
import functools
from json import loads, JSONDecodeError
from urllib3.response import HTTPResponse
from kubernetes.client import ApiClient
from kubernetes.client.exceptions import (
    ApiTypeError,
    ApiException
)


logger = logging.getLogger(__name__)


@allure.step('调用API')
def log_calls_of_moc_api(api_client: ApiClient, url, method, body, query_params, path_params, response, request_at, elapsed):
    logger.debug("request url: %s, request method: %s, request body: %s, request query params: %s, request path params: %s,\nresponse body:\n%s,\nrequest at: %s, response elapsed: %s",
                 f'{api_client.configuration.host}{url}', method, body, query_params, path_params, response, request_at, elapsed)


def moc_api_request(url, method: str, response_type=None, status_code=200, *extra_params, **extra_args):
    def decorator(func):
        @functools.wraps(func)
        def api_request(*args, **kwargs):
            local_var_params = locals()
            api_client: ApiClient = args[0].api_client

            all_params = list(extra_params)
            all_params.extend(
                [
                    'async_req',
                    '_return_http_data_only',
                    '_preload_content',
                    '_request_timeout'
                ]
            )

            for key, val in six.iteritems(extra_args):
                if key not in all_params:
                    raise ApiTypeError(
                        f"Got an unexpected keyword argument '{key}' to method {func.__name__}"
                    )
                local_var_params[key] = val
            del local_var_params['extra_args']

            collection_formats = {}

            # verify the required parameters are set
            body_params = None
            path_params = {}
            query_params = []
            func_result = func(*args, **kwargs)
            if isinstance(func_result, tuple):
                func_params = (p for p in func_result)
                try:
                    body_params = next(func_params)
                    query_params = next(func_params)
                    path_params = next(func_params)
                except StopIteration:
                    pass
            else:
                body_params = func_result
            # for index, param in enumerate(func.__code__.co_varnames[1:-1]):
            #     if index >= len(args) - 1 or args[index + 1] is None:
            #         if api_client.client_side_validation:
            #             raise ApiValueError(f"Missing the required parameter `{param}` when calling `{func.__name__}`")
            #     else:
            #         if param == 'body':
            #             body_params = args[index + 1]
            #         else:
            #             path_params[param] = args[index + 1]
            del local_var_params['args']
            del local_var_params['kwargs']

            # query_params = []
            for param in query_params:
                if param[1] is None:
                    query_params.remove(param)
            for param in extra_params:
                if param in local_var_params and local_var_params[param] is not None:
                    query_params.append((param, local_var_params[param]))

            header_params = {}
            form_params = []
            local_var_files = {}

            # HTTP header `Accept`
            header_params['Accept'] = api_client.select_header_accept(
                ['application/json', 'application/yaml', 'application/vnd.kubernetes.protobuf'])

            # HTTP header `Content-Type`
            if method.lower() == 'patch':
                header_params['Content-Type'] = api_client.select_header_content_type(
                    ['application/merge-patch+json', 'application/json-patch+json',
                     'application/strategic-merge-patch+json', 'application/apply-patch+yaml'])

            # Authentication setting
            auth_settings = ['BearerToken']
            start_time = datetime.datetime.now()
            try:
                response = api_client.call_api(
                    url, method,
                    path_params,
                    query_params,
                    header_params,
                    body=body_params,
                    post_params=form_params,
                    files=local_var_files,
                    response_type=response_type,
                    auth_settings=auth_settings,
                    async_req=local_var_params.get('async_req'),
                    _return_http_data_only=local_var_params.get('_return_http_data_only'),
                    _preload_content=local_var_params.get('_preload_content',  True if response_type else False),
                    _request_timeout=local_var_params.get('_request_timeout'),
                    collection_formats=collection_formats)
            except ApiException as e:
                if e.body:
                    try:
                        if response_type:
                            return BaseModel(**loads(e.body))
                        else:
                            return loads(e.body)
                    except JSONDecodeError as je:
                        logger.debug(je.msg)
                        if response_type:
                            return BaseModel(code=e.status, msg=e.body.decode('utf-8') if isinstance(e.body, bytes) else e.body)
                        else:
                            return {'code': e.status, 'msg': e.body.decode('utf-8') if isinstance(e.body, bytes) else e.body}
                else:
                    if response_type:
                        return BaseModel(code=e.status, msg=e.reason)
                    else:
                        return {'code': e.status, 'msg': e.reason}
            # except TimeoutError as e:
            #     logger.error(f"Timeout to request {url} within {local_var_params.get('_request_timeout')} seconds. {e}")
            #     return
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            if local_var_params.get('_return_http_data_only'):
                response_data = response
                if isinstance(response_data, HTTPResponse):
                    assert response_data.status == status_code, f"Expected status code for response is {status_code} rather than {response_data.status}"
            else:
                response_data = response[0]
                assert response[1] == status_code, f"Expected status code for response is {status_code} rather than {response[1]}"
            if isinstance(response_data, HTTPResponse):
                try:
                    response_data = loads(response_data.data)
                except JSONDecodeError as e:
                    logger.debug(e.msg)
                    response_data = response_data.data
                    if isinstance(response_data, bytes):
                        response_data = response_data.decode('utf-8')
            # logger.debug("request url: %s, request method: %s, request body: %s,\nresponse body: %s,\nresponse elapsed: %.3fs", f'{api_client.configuration.host}{url}', method, body_params, response_data, elapsed_time)
            log_calls_of_moc_api(api_client, url, method, body_params, query_params, path_params, response_data, start_time.strftime('%Y-%m-%d %H:%M:%S.%f'), '{:.3f}s'.format(elapsed_time))
            if local_var_params.get('_return_http_data_only'):
                return response_data
            else:
                return response_data
                # return response_data, response[1], response[2]
        return api_request
    return decorator


class MOCApiClient(ApiClient):

    def __repr__(self):
        return self.configuration.host

    @staticmethod
    def retrieve_sub_element(data, *args):
        for p in args:
            _data = None
            if isinstance(data, list):
                if p.isdigit():
                    p = int(p)
                if isinstance(p, int) and p < len(data):
                    _data = data[p]
            elif isinstance(data, dict):
                if isinstance(p, str):
                    if '|' in p:
                        for _p in p.split('|'):
                            if _p in data:
                                _data = data[_p]
                                break
                    else:
                        _data = data.get(p)
            data = _data
        return data

    def deserialize(self, response, response_type):
        """Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialized object, or string of class name.

        :return: deserialized object.
        """
        # handle file downloading
        # save response body into a tmp file and return the instance_
        if response_type == "file":
            return self._ApiClient__deserialize_file(response)

        # fetch data from response object
        try:
            data = loads(response.data)
        except ValueError:
            data = response.data

        return self.__deserialize(data, response_type)

    def __deserialize(self, data, klass):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith('list['):
                sub_kls = re.match(r'list\[(.*)\]', klass).group(1)
                return [self.__deserialize(sub_data, sub_kls)
                        for sub_data in data]

            if klass.startswith('dict('):
                sub_kls = re.match(r'dict\(([^,]*), (.*)\)', klass).group(2)
                return {k: self.__deserialize(v, sub_kls)
                        for k, v in six.iteritems(data)}

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                module_klass = klass.rsplit('.', 1)
                if module_klass[0] in ('', klass):
                    raise ValueError(f"'{klass}' is invalid")
                else:
                    klass = getattr(importlib.import_module(module_klass[0]), module_klass[1])
                    if klass:
                        if not inspect.isclass(klass):
                            raise ValueError(f"'{'.'.join(module_klass)}' is not referred to a Class.")
                    else:
                        raise ValueError(f"Class '{'.'.join(module_klass)}' is not found")

        if klass in self.PRIMITIVE_TYPES:
            return self._ApiClient__deserialize_primitive(data, klass)
        elif klass == object:
            return self._ApiClient__deserialize_object(data)
        elif klass == datetime.date:
            return self._ApiClient__deserialize_date(data)
        elif klass == datetime.datetime:
            return self._ApiClient__deserialize_datetime(data)
        elif isinstance(klass, EnumMeta):
            return self.__deserialize_enum(data, klass)
        else:
            return self.__deserialize_model(data, klass)

    def __deserialize_enum(self, value, klass):
        """Deserializes string to Enum type.

        :param value: str.
        :param klass: class literal.

        :return: Enum.
        """
        return klass(value)

    def __deserialize_model(self, data, klass):
        """Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """

        if not klass.openapi_types and not hasattr(klass,
                                                   'get_real_child_model'):
            return data

        kwargs = {}
        if (data is not None and
                klass.openapi_types is not None and
                isinstance(data, (list, dict))):
            for attr, attr_type in six.iteritems(klass.openapi_types):
                value = self.retrieve_sub_element(data, *klass.attribute_map[attr].split('.'))
                kwargs[attr] = self.__deserialize(value, attr_type)

        instance = klass(**kwargs)

        if hasattr(instance, 'get_real_child_model'):
            klass_name = instance.get_real_child_model(data)
            if klass_name:
                instance = self.__deserialize(data, klass_name)
        return instance
