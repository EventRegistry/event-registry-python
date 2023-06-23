"""
utility classes for Event Registry
"""

import six, warnings, os, sys, re, datetime, time
from eventregistry.Logger import logger
from typing import Union, List, Dict

mainLangs = ["eng", "deu", "zho", "slv", "spa"]
allLangs = [ "eng", "deu", "spa", "cat", "por", "ita", "fra", "rus", "ara", "tur", "zho", "slv", "hrv", "srp" ]
conceptTypes = ["loc", "person", "org", "keyword", "wiki", "conceptClass", "conceptFolder"]


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
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
    return invalidCharRe.sub("", text)


def tryParseInt(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val


class Struct(object):
    """
    helper class for converting dict to a native python object
    instead of a["b"]["c"] we can write a.b.c
    """
    def __init__(self, data: dict):
        for name, value in data.items():
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
    """method to convert a list or dict to a native python object"""
    if isinstance(data, list):
        return type(data)([createStructFromDict(v) for v in data])
    else:
        return Struct(data)


class QueryItems:
    _AND = "$and"
    _OR = "$or"
    _Undef = None

    def __init__(self, oper, items):
        self._oper = oper
        self._items = items

    @staticmethod
    def AND(items):
        return QueryItems(QueryItems._AND, items)

    @staticmethod
    def OR(items):
        return QueryItems(QueryItems._OR, items)

    def getOper(self):
        return self._oper

    def getItems(self):
        return self._items


class QueryParamsBase(object):
    """
    Base class for Query and AdminQuery
    used for storing parameters for a query. Parameter values can either be
    simple values (set by _setVal()) or an array of values (set by multiple
    calls to _addArrayVal() method)
    """
    def __init__(self):
        self.queryParams: dict = {}


    @staticmethod
    def copy(obj: "QueryParamsBase"):
        assert isinstance(obj, QueryParamsBase)
        ret = QueryParamsBase()
        ret.queryParams = dict(obj.queryParams)
        return ret


    @staticmethod
    def encodeDate(val: Union[datetime.datetime, datetime.date, str]):
        """encode val that can be a date in different forms as a date that can be sent to Er"""
        if isinstance(val, datetime.datetime):
            return val.date().isoformat()
        elif isinstance(val, datetime.date):
            return val.isoformat()
        elif isinstance(val, six.string_types):
            assert re.match(r"^\d{4}-\d{2}-\d{2}$", val), f"date value '{val}' was not provided in the 'YYYY-MM-DD' format"
            return val
        raise AssertionError("date was not in the expected format")


    @staticmethod
    def encodeDateTime(val: Union[datetime.datetime, str]):
        """encode datetime into UTC ISO format which can be sent to ER"""
        if isinstance(val, datetime.datetime):
            # if we have a datetime in some tz, we convert it first to UTC
            if val.utcoffset() is not None:
                import pytz
                val = val.astimezone(pytz.utc)
            return val.isoformat()
        elif isinstance(val, six.string_types):
            assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$", val), f"datetime value '{val}' was not provided in the 'YYYY-MM-DDTHH:MM:SS.SSSS' format"
            return val
        raise AssertionError("datetime was not in the recognizable data type. Use datetime or string in ISO format")


    def _clearVal(self, propName: str):
        """remove the value of a property propName (if existing)"""
        if propName in self.queryParams:
            del self.queryParams[propName]


    def _hasVal(self, propName: str) -> bool:
        """do we have in the query property named propName"""
        return propName in self.queryParams


    def _setVal(self, propName: str, val):
        """set a value of a property in the query"""
        if isinstance(val, six.string_types):
            # in python 2 we need to first encode, before removing the invalid characters
            if six.PY2:
                val = val.encode("utf8")
            val = removeInvalidChars(val)
        self.queryParams[propName] = val


    def _setValIfNotDefault(self, propName: str, val, defVal):
        """set to queryParams property propName to val if val != defVal"""
        if val != defVal:
            self._setVal(propName, val)


    def _setDateVal(self, propName: str, val):
        """set a property value that represents date. Value can be string in YYYY-MM-DD format, datetime.date or datetime.datetime"""
        encodedVal = self.encodeDate(val)
        self._setVal(propName, encodedVal)


    def _addArrayVal(self, propName: str, val):
        """add a value to an array of values for a property"""
        if isinstance(val, six.string_types):
            # in python 2 we need to first encode, before removing the invalid characters
            if six.PY2:
                val = val.encode("utf8")
            val = removeInvalidChars(val)
        if propName not in self.queryParams:
            self.queryParams[propName] = []
        self.queryParams[propName].append(val)


    def _update(self, object: Dict):
        self.queryParams.update(object)


    def _getQueryParams(self) -> Dict:
        """return the parameters."""
        return dict(self.queryParams)


    def _setQueryArrVal(self, value: Union[str, QueryItems, List, None], propName: str, propOperName: Union[str, None], defaultOperName: str):
        """
        parse the value "value" and use it to set the property propName and the operator with name propOperName
        @param value: None, string, QueryItems or list. Values to be set using property name propName
        @param propOperName: property to set containing the "and" or "or". Relevant only if multiple items are provided in "value". Can be None if only one value is possible
        @param defaultOperName: which operator should be used in case "value" is a list. If a list, we will print also a warning to suggest use of QueryItems
        """
        # by default we have None - so don't do anything
        if value is None or value == "":
            return
        # if we have an instance of QueryItems then apply it
        if isinstance(value, QueryItems):
            self.queryParams[propName] = value.getItems()
            # if we need to specify the operator for the property
            if propOperName is not None:
                self.queryParams[propOperName] = value.getOper().replace("$", "")
            # if the user specified the QueryItems class but used the invalid operator type then raise an error
            assert propOperName is not None or value.getOper().replace("$", "") == defaultOperName, "An invalid operator type '%s' was used for property '%s'" % (value.getOper().replace("$", ""), propName)

        # if we have a string value, just use it
        elif isinstance(value, six.string_types):
            self.queryParams[propName] = value

        # if we have a list, set it, but also weport
        elif isinstance(value, list):
            self.queryParams[propName] = value
            # if we need to specify the operator for the property
            if propOperName is not None:
                self.queryParams[propOperName] = defaultOperName
                if len(value) > 1:
                    logger.warning("Warning: The value of parameter '%s' was provided as a list and '%s' operator was used implicitly between the items. We suggest specifying the list using the QueryItems.AND() or QueryItems.OR() to ensure the appropriate operator is used.", propName, defaultOperName)

        # there should be no other valid types
        else:
            assert False, f"Parameter '{propName}' was of unsupported type. It should either be None, a string or an instance of QueryItems"



class Query(QueryParamsBase):
    def __init__(self):
        QueryParamsBase.__init__(self)
        self.resultTypeList = []


    def _getQueryParams(self):
        """encode the request."""
        allParams = {}
        if len(self.resultTypeList) == 0:
            raise ValueError("The query does not have any result type specified. No sense in performing such a query")
        allParams.update(self.queryParams)
        for request in self.resultTypeList:
            allParams.update(request.__dict__)
        # all requests in resultTypeList have "resultType" so each call to .update() overrides the previous one
        # since we want to store them all we have to add them here:
        allParams["resultType"] = [request.__dict__["resultType"] for request in self.resultTypeList]
        return allParams


