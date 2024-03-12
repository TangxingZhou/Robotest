from __future__ import absolute_import

import six
import logging
import functools
from json import loads, JSONDecodeError
from urllib3.response import HTTPResponse
from kubernetes.client import ApiClient
from kubernetes.client.exceptions import (
    ApiTypeError,
    ApiValueError,
    ApiException
)


logger = logging.getLogger(__name__)


def k8s_api_request(url, method: str, response_type=None, *extra_params):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
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

            for key, val in six.iteritems(local_var_params['kwargs']):
                if key not in all_params:
                    raise ApiTypeError(
                        f"Got an unexpected keyword argument '{key}' to method {func.__name__}"
                    )
                local_var_params[key] = val
            del local_var_params['kwargs']

            collection_formats = {}

            # verify the required parameters are set
            path_params = {}
            body_params = None
            for index, param in enumerate(func.__code__.co_varnames[1:-1]):
                if index >= len(args) - 1 or args[index + 1] is None:
                    if api_client.client_side_validation:
                        raise ApiValueError(f"Missing the required parameter `{param}` when calling `{func.__name__}`")
                else:
                    if param == 'body':
                        body_params = args[index + 1]
                    else:
                        path_params[param] = args[index + 1]
            del local_var_params['args']

            query_params = []
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

            # response_headers = {}
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
                if local_var_params.get('_return_http_data_only'):
                    return response
                else:
                    if isinstance(response[0], HTTPResponse):
                        response = [response[0].data, response[1], response[2]]
            except ApiException as e:
                response = [e.body, e.status, e.headers]
            if isinstance(response[0], bytes):
                response[0] = response[0].decode('utf-8')
            if isinstance(response[0], str):
                try:
                    response[0] = loads(response[0])
                except JSONDecodeError as e:
                    logger.debug(e.msg)
            func(*args, **kwargs)
            return tuple(response)
        return wrapper
    return decorator


def async_request(sync_method):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['_return_http_data_only'] = True
            if hasattr(args[0], sync_method):
                sync_request = getattr(args[0], sync_method)
            else:
                raise AttributeError("The synchronous request method '{}' is not found for asynchronous request method "
                                     "of {}".format(sync_method, func.__name__))
            if kwargs.get('async_req'):
                return sync_request(**kwargs)
            else:
                (data) = sync_request(**kwargs)
                return data
        return wrapper
    return decorator


def parse_http_response(response):
    headers = {}
    for k, v in response[2].iteritems():
        headers[k] = v
    return loads(response[0].data.decode('utf-8')), response[1], headers
