import re
from json import loads, JSONDecodeError
import functools
from six import iteritems
from kubernetes.client.rest import ApiException


def request(url, method, *request_params):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            all_params = list(args[1:])
            all_params.extend(list(request_params))
            all_params.append('async_req')
            all_params.append('_return_http_data_only')
            all_params.append('_preload_content')
            all_params.append('_request_timeout')
            params = locals()
            api_client = args[0].api_client
            del params['args']

            required = list()
            for path in re.findall(r'\{(\w*)\}', url):
                required.append(path)
            query = list(filter(lambda p: p not in required + ['body'], request_params))

            for key, val in iteritems(params['kwargs']):
                if key not in all_params:
                    raise TypeError("Got an unexpected keyword argument '{}' to method {}".format(key, func.__name__))
                params[key] = val
            del params['kwargs']

            collection_formats = {}

            # verify the required parameters are set
            path_params = {}
            for param in required:
                if (param not in params) or (params[param] is None):
                    raise ValueError("Missing the required parameter `{}` when calling `{}`".format(param, func.__name__))
                else:
                    path_params[param] = params[param]

            query_params = []
            for param in query:
                if param in params:
                    query_params.append((param, params[param]))

            header_params = {}
            form_params = []
            local_var_files = {}

            body_params = None
            if 'body' in params:
                body_params = params['body']

            # HTTP header `Accept`
            header_params['Accept'] = api_client.select_header_accept(['*/*'])

            # HTTP header `Content-Type`
            header_params['Content-Type'] = api_client.select_header_content_type(['application/json'])

            # Authentication setting
            auth_settings = ['BearerToken']

            headers = {}
            try:
                response = api_client.call_api(url, method,
                                               path_params,
                                               query_params,
                                               header_params,
                                               body=body_params,
                                               post_params=form_params,
                                               files=local_var_files,
                                               response_type=None,
                                               auth_settings=auth_settings,
                                               async_req=params.get('async_req'),
                                               _return_http_data_only=params.get('_return_http_data_only'),
                                               _preload_content=params.get('_preload_content', False),
                                               _request_timeout=params.get('_request_timeout'),
                                               collection_formats=collection_formats)
                response = (response[0].data, response[1], response[2])
            except ApiException as e:
                response = (e.body, e.status, e.headers)
            for k, v in response[2].iteritems():
                headers[k] = v
            try:
                response_body = loads(response[0].decode('utf-8'))
            except JSONDecodeError as e:
                response_body = response[0].decode('utf-8')
            return response_body, response[1], headers
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
