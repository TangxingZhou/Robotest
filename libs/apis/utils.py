import time
import logging
import functools
import importlib
import inspect

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
        type_name = attrs.get('type_name', name.lower())
        cls._sub_classes[type_name] = cls

    # def __new__(cls, name, bases, attrs, **kwargs):
    #     type_name = kwargs.get('type_name', name.lower())
    #     new_cls = super().__new__(cls, name, bases, attrs)
    #     cls._sub_classes[type_name] = new_cls
    #     return new_cls

    def __call__(cls, type_name=None, *args, **kwargs):
        if not type_name:
            type_name = getattr(cls, 'type_name')
        if type_name not in cls._sub_classes:
            raise ValueError(f"Unknown type: {type_name}")
        subclass = cls._sub_classes[type_name]
        if cls is subclass:
            return super().__call__(*args, **kwargs)
        else:
            return subclass(type_name, *args, **kwargs)

    # def __call__(cls, type_name, *args, **kwargs):
    #     for subclass in cls.__subclasses__():
    #         if getattr(subclass, 'type_name', None) == type_name:
    #             return super().__call__(*args, **kwargs)
    #     raise ValueError(f"Unknown type: {type_name}")


def compare_objects(obj1, obj2):
    def sort_key(item):
        if isinstance(item, list):
            return sorted(item, key=sort_key)
        elif isinstance(item, dict):
            return sorted((k, sort_key(v)) for k, v in item.items())
        else:
            return item

    if type(obj1) is not type(obj2):
        return False

    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False

        obj1 = sorted(obj1, key=sort_key)
        obj2 = sorted(obj2, key=sort_key)

        for i in range(len(obj1)):
            if not compare_objects(obj1[i], obj2[i]):
                return False

    elif isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False

        for key in obj1:
            if key not in obj2:
                return False

            if not compare_objects(obj1[key], obj2[key]):
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
