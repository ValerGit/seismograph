# -*- coding: utf-8 -*-

import sys
import time
from . import pyv

from ..exceptions import TimeoutException


def waiting_for(func, timeout=None, exc_cls=None, message=None, delay=None, args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or dict()

    timeout = timeout or 0
    message = message or 'Timeout "{}" exceeded'.format(timeout)

    if timeout:
        t_start = time.time()

        while time.time() <= t_start + timeout:
            result = func(*args, **kwargs)

            if result:
                return result

            if delay:
                time.sleep(delay)
        else:
            if exc_cls:
                raise exc_cls(message)
            raise TimeoutException(message)

    result = func(*args, **kwargs)

    if result:
        return result
    if exc_cls:
        raise exc_cls(message)
    raise TimeoutException(message)


def call_to_chain(chain, method_name, *args, **kwargs):
    for obj in chain:
        if method_name:
            getattr(obj, method_name)(*args, **kwargs)
        else:
            obj(*args, **kwargs)


def measure_time():
    start_time = time.time()
    return lambda: time.time() - start_time


def pythonpaths(*paths):
    def wrapper(f):
        for path in paths:
            if path not in sys.path:
                sys.path.append(path)
        return f
    return wrapper


def get_dict_from_list(lst, **kwargs):
    """
    Get dictionary by equal filters from kwargs

    Example:

        lst = [
            {
                'name': 'hello',
            },
            {
                'name': 'world',
            }
        ]

        dct = get_dict_from_list(lst, name='hello')
    """
    if kwargs and isinstance(lst, (list, tuple)):
        for item in lst:
            comparison = all(
                item.get(k) == v
                if isinstance(v, (int, pyv.basestring))
                else
                True
                for k, v in kwargs.items()
            )
            if comparison:
                return item
        else:
            raise LookupError(
                'Dictionary from list is not found by filters: {}'.format(kwargs),
            )

    return lst


def reduce_dict(d1, **kwargs):
    """
    Leads dictionaries to the same species.
    The standard dictionary is d2.
    """
    def prepare_lists(l1, l2):
        assert len(l1) == len(l2)

        for i in l1:
            if isinstance(i, dict):
                l1[l1.index(i)] = reduce_dict(i, **l2[l1.index(i)])

        return l1

    return dict(
        (
            k,
            reduce_dict(v, **kwargs[k])
            if isinstance(v, dict) and isinstance(kwargs[k], dict)
            else
            v.sort() or kwargs[k].sort() or prepare_lists(v, kwargs[k])
            if isinstance(v, list) and isinstance(kwargs[k], list)
            else
            v,
        )
        for k, v in d1.items()
        if k in kwargs
    )
