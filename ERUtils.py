"""
utility classes for Event Registry
"""

import warnings, os, sys

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning) #turn off filter 
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning) #reset filter
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


invalidCharRe = re.compile(r"[\x00-\x08]|\x0b|\x0c|\x0e|\x0f|[\x10-\x19]|[\x1a-\x1f]", re.IGNORECASE)
def removeInvalidChars(text):
    return invalidCharRe.sub("", text);


class Struct(object):
    """
    general class for converting dict to a native python object
    instead of a["b"]["c"] we can write a.b.c
    """
    def __init__(self, data):
        for name, value in data.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

    # does the object have the key
    def has(self, key):
        return hasattr(self, key)


def createStructFromDict(data):
    """
    method to convert a list or dict to a native python object
    """
    if isinstance(data, list):
        return type(data)([createStructFromDict(v) for v in data])
    else:
        return Struct(data)
