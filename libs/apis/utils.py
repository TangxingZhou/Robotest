import time
import six
import logging
import functools
import importlib
import inspect
import pprint
from enum import Enum
from collections.abc import Iterable


logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _default = {}

    def __call__(cls, key='default', *args, **kwargs):
        if cls._default.get(key) is None:
            cls._default[key] = super(SingletonMeta, cls).__call__(key, *args, **kwargs)
        return cls._default[key]


class FactoryMeta(type):
    _sub_classes = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        _type_name = attrs.get('_type_name', name)
        cls._type_name = _type_name
        cls._sub_classes[_type_name] = cls

        def to_dict(self):
            # return obj_to_dict(getattr(self, f'_{type(self).__bases__[0].__name__}__data'))
            return obj_to_dict(self)
        cls.to_dict = to_dict

        def eq(self, other):
            if isinstance(other, type(self).__bases__[0]):
                return self.to_dict() == other.to_dict()
            elif isinstance(other, dict):
                return self.__data == other
            else:
                return False
        cls.__eq__ = eq
        cls.__repr__ = lambda self: pprint.pformat(self.to_dict())

    def __call__(cls, _type_name=None, *args, **kwargs):
        if not _type_name:
            _type_name = getattr(cls, '_type_name')
        if _type_name not in cls._sub_classes:
            raise ValueError(f"Unknown type: {_type_name}")
        subclass = cls._sub_classes[_type_name]
        if cls is subclass:
            return super().__call__(*args, **kwargs)
        else:
            return subclass(_type_name, *args, **kwargs)


def objects_should_be_equal(obj1, obj2):
    def sort_key(item):
        if isinstance(item, list):
            return sorted(item, key=sort_key)
        elif isinstance(item, dict):
            return sorted((k, sort_key(v)) for k, v in item.items())
        else:
            return item

    logger.debug(f"To compare objects:\n{obj1}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{obj2}")
    if type(obj1) is not type(obj2):
        return False

    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False

        obj1 = sorted(obj1, key=sort_key)
        obj2 = sorted(obj2, key=sort_key)

        for i in range(len(obj1)):
            if not objects_should_be_equal(obj1[i], obj2[i]):
                logger.debug(f"{obj1[i]} is not equal to {obj2[i]}.")
                return False

    elif isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False

        for key in obj1:
            if key not in obj2:
                return False

            if not objects_should_be_equal(obj1[key], obj2[key]):
                logger.debug(f"{obj1[key]} is not equal to {obj2[key]}.")
                return False

    else:
        if obj1 != obj2:
            return False

    return True


def wait_for(f, interval: int = 0, _timeout: int = 1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            if kwargs.get('_timeout'):
                timeout = kwargs.get('_timeout')
            else:
                timeout = _timeout
            while time.time() - start < timeout if timeout > 0 else False:
                result = func(*args, **kwargs)
                if f(result):
                    return result
                logger.debug(f"Wait for the conditions evaluated by '{f.__name__}' with args:\n{result}")
                time.sleep(interval)
            if kwargs.get('_timeout'):
                msg = f"Timeout to achieve the conditions by '{f.__name__}' with args:\n{result}"
                raise Exception(msg)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def _wait_for(f, func, interval: int = 0, _timeout: int = 1, *args, **kwargs):
    start = time.time()
    if kwargs.get('_timeout'):
        timeout = kwargs.get('_timeout')
    else:
        timeout = _timeout
    while time.time() - start < timeout if timeout > 0 else True:
        result = func(*args, **kwargs)
        if f(result):
            return result
        logger.debug(f"Wait for the conditions by '{f.__name__}' with args:\n{result}")
        time.sleep(interval)
    if kwargs.get('_timeout'):
        msg = f"Timeout to achieve the conditions by '{f.__name__}' with args:\n{result}"
        raise Exception(msg)
    else:
        return func(*args, **kwargs)


def retrieve_module(_base='src.service', _modules=()):
    base = importlib.import_module(_base)
    for attr in dir(base):
        if inspect.ismodule(getattr(base, attr)):
            if getattr(base, attr).__name__.startswith(_base):
                _modules=retrieve_module(getattr(base, attr).__name__, _modules)
        elif inspect.isclass(getattr(base, attr)):
            if getattr(base, attr).__module__.startswith(_base) and 'models' in getattr(base, attr).__module__:
                _modules = tuple(list(_modules) + [getattr(base, attr)])
    return _modules


def wait_and_filter(*extra_params, **extra_args):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            local_var_params = locals()

            all_params = list(extra_params)
            all_params.extend(
                [
                    '_interval',
                    '_timeout'
                ]
            )

            for key, val in six.iteritems(extra_args):
                if key not in all_params:
                    raise ValueError(
                        f"Got an unexpected keyword argument '{key}' when decorating method '{func.__name__}'"
                    )
                local_var_params[key] = val
            del local_var_params['extra_args']

            filter_fields, expected_condition = {}, kwargs.pop('expected_condition', lambda x: True if x else False)
            for k, v in six.iteritems(kwargs):
                if k in all_params:
                    local_var_params[k] = v
                if k not in inspect.signature(func).parameters.keys() and k not in local_var_params:
                    filter_fields[k] = v
            del local_var_params['args']
            del local_var_params['kwargs']

            start = time.time()
            _timeout: int = local_var_params.get('_timeout', 0)
            result, total = [], None
            if _timeout > 0:
                while time.time() - start < _timeout:
                    func_result = func(*args, **kwargs)
                    if isinstance(func_result, tuple):
                        func_results = (p for p in func_result)
                        try:
                            result = next(func_results)
                            total = next(func_results)
                        except StopIteration:
                            pass
                    else:
                        result = func_result

                    if isinstance(result, Iterable):
                        result_list = list(result)
                    else:
                        result_list = [result]

                    filter_results = []
                    for r in result_list:
                        match_fields = True
                        for k, v in six.iteritems(filter_fields):
                            if not match_fields:
                                break
                            if hasattr(r, k):
                                if callable(v):
                                    if not v(getattr(r, k)):
                                        match_fields = False
                                else:
                                    if getattr(r, k) != v:
                                        match_fields = False
                            else:
                                match_fields = False
                        if match_fields:
                            filter_results.append(r)
                    logger.debug(f"Wait for the conditions evaluated by filters: {filter_fields} and evaluator: {expected_condition}.")
                    return_result = filter_results if isinstance(result, Iterable) else filter_results[0] if len(filter_results) > 0 else None
                    if expected_condition(return_result):
                        if total is None:
                            return return_result
                        else:
                            return return_result, total
                    else:
                        time.sleep(local_var_params.get('_interval', 2))
                msg = f"Timeout({_timeout}s) to achieve the conditions evaluated by filters: {filter_fields} and evaluator: {expected_condition}."
                raise Exception(msg)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def obj_to_dict(o) -> dict:
    result = {}

    def _to_dict(v):
        if isinstance(v, (list, set)):
            return [_to_dict(i) for i in v]
        elif hasattr(v, "to_dict"):
            return v.to_dict()
        elif isinstance(v, dict):
            return {i: _to_dict(j) for i, j in v.items()}
        elif isinstance(v, Enum):
            return v.value
        else:
            return v

    for attr in dir(o):
        if attr in ('openapi_types', 'attribute_map', 'err', *getattr(o, '_ignore_attrs', [])):
            continue
        if attr in getattr(o, '_ignore_none_value', []) and getattr(o, attr) is None:
            continue
        if not attr.startswith('_') and not callable(getattr(o, attr)):
            result[attr] = _to_dict(getattr(o, attr))
    return result
