"""
utility classes for Event Registry
"""

import copy, functools, warnings, re, datetime
from eventregistry.Exceptions import QueryError
from eventregistry.Logger import logger
from typing import Union, List, Dict

# the names exported by "from eventregistry import *"
__all__ = ["mainLangs", "allLangs", "conceptTypes", "deprecated", "removeInvalidChars", "tryParseInt",
           "Struct", "createStructFromDict", "QueryItems", "QueryParamsBase", "Query", "QueryResultsIter",
           "IterableQuery"]

mainLangs = ["eng", "deu", "zho", "slv", "spa"]
allLangs = [ "eng", "deu", "spa", "cat", "por", "ita", "fra", "rus", "ara", "tur", "zho", "slv", "hrv", "srp" ]
conceptTypes = ["loc", "person", "org", "keyword", "wiki", "conceptClass", "conceptFolder"]


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return new_func


invalidCharRe = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
def removeInvalidChars(text):
    return invalidCharRe.sub("", text)


def tryParseInt(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val


class Struct:
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


class QueryParamsBase:
    """
    Base class for Query and AdminQuery
    used for storing parameters for a query. Parameter values can either be
    simple values (set by _setVal()) or an array of values (set by multiple
    calls to _addArrayVal() method)
    """
    def __init__(self):
        self.queryParams: dict = {}


    def __repr__(self):
        """show the parameters of the query, e.g. QueryArticles(keyword='Tesla', lang='eng')"""
        params = ", ".join("%s=%r" % (key, val) for key, val in self.queryParams.items())
        return "%s(%s)" % (type(self).__name__, params)


    def _getPath(self):
        raise NotImplementedError("This method should be implemented in the child class to return the path to which the query should be sent")


    @staticmethod
    def copy(params: "QueryParamsBase"):
        if not (isinstance(params, QueryParamsBase)):
            raise TypeError("params should be of type QueryParamsBase")
        ret = QueryParamsBase()
        ret.queryParams = dict(params.queryParams)
        return ret


    @staticmethod
    def _toNaiveUtc(val: datetime.datetime) -> datetime.datetime:
        """
        Event Registry works with UTC times without a timezone offset. A datetime with a timezone is converted
        to UTC and the timezone is removed. A datetime without a timezone is considered to already be in UTC
        """
        if val.utcoffset() is not None:
            val = val.astimezone(datetime.timezone.utc).replace(tzinfo = None)
        return val


    @staticmethod
    def encodeDate(val: Union[datetime.datetime, datetime.date, str]):
        """
        encode val that can be a date in different forms as a date that can be sent to ER.
        For a datetime with a timezone we use the date in UTC (a datetime without a timezone is considered to be in UTC)
        """
        if isinstance(val, datetime.datetime):
            return QueryParamsBase._toNaiveUtc(val).date().isoformat()
        elif isinstance(val, datetime.date):
            return val.isoformat()
        elif isinstance(val, str):
            if not (re.match(r"^\d{4}-\d{2}-\d{2}$", val)):
                raise ValueError(f"date value '{val}' was not provided in the 'YYYY-MM-DD' format")
            return val
        raise TypeError("date should be a datetime, date or a string in the 'YYYY-MM-DD' format")


    @staticmethod
    def encodeDateTime(val: Union[datetime.datetime, str]):
        """
        encode datetime into the UTC ISO format without a timezone offset, which can be sent to ER.
        A datetime (or a string) with a timezone is converted to UTC. One without a timezone is considered to be in UTC.
        Strings can be in the 'YYYY-MM-DDTHH:MM:SS[.SSSS]' format, optionally followed by 'Z' or an offset like '+02:00'
        """
        if isinstance(val, datetime.datetime):
            return QueryParamsBase._toNaiveUtc(val).isoformat()
        elif isinstance(val, str):
            match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?)(Z|[+-]\d{2}:?\d{2})?$", val)
            if not match:
                raise ValueError(f"datetime value '{val}' was not provided in the 'YYYY-MM-DDTHH:MM:SS.SSSS' format")
            offset = match.group(3)
            if offset is None:
                return val
            if offset == "Z":
                return match.group(1)
            # convert the time with an offset to UTC. the fraction of a second is padded to the 6 digits that strptime needs
            fraction = (match.group(2) or ".0")[1:7].ljust(6, "0")
            parsed = datetime.datetime.strptime(match.group(1)[:19] + "." + fraction + offset.replace(":", ""), "%Y-%m-%dT%H:%M:%S.%f%z")
            return QueryParamsBase._toNaiveUtc(parsed).isoformat()
        raise TypeError("datetime was not in the recognizable data type. Use datetime or string in ISO format")


    def _clearVal(self, propName: str):
        """remove the value of a property propName (if existing)"""
        if propName in self.queryParams:
            del self.queryParams[propName]


    def _hasVal(self, propName: str) -> bool:
        """do we have in the query property named propName"""
        return propName in self.queryParams


    def _setVal(self, propName: str, val):
        """set a value of a property in the query"""
        if isinstance(val, str):
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
        if isinstance(val, str):
            val = removeInvalidChars(val)
        if propName not in self.queryParams:
            self.queryParams[propName] = []
        self.queryParams[propName].append(val)


    def _update(self, params: Dict):
        self.queryParams.update(params)


    def _getQueryParams(self) -> Dict:
        """return the parameters."""
        return dict(self.queryParams)


    def _setQueryArrVal(self, value: Union[str, QueryItems, List, None], propName: str, propOperName: Union[str, None], defaultOperName: str):
        """
        parse the value "value" and use it to set the property propName and the operator with name propOperName

        Args:
            value: None, string, QueryItems or list. Values to be set using property name propName
            propOperName: property to set containing the "and" or "or". Relevant only if multiple items are provided in "value". Can be None if only one value is possible
            defaultOperName: which operator should be used in case "value" is a list. If a list, we will print also a warning to suggest use of QueryItems
        """
        # by default we have None - so don't do anything. An empty list (or QueryItems without items) is ignored as well
        if value is None or value == "" or value == []:
            return
        if isinstance(value, QueryItems) and len(value.getItems()) == 0:
            return
        # if we have an instance of QueryItems then apply it
        if isinstance(value, QueryItems):
            oper = value.getOper().replace("$", "")
            # if the user specified the QueryItems class but used the invalid operator type then raise an error
            if not (propOperName is not None or oper == defaultOperName):
                raise ValueError("An invalid operator type '%s' was used for property '%s'" % (oper, propName))
            self.queryParams[propName] = value.getItems()
            # if we need to specify the operator for the property
            if propOperName is not None:
                self.queryParams[propOperName] = oper

        # if we have a string value, just use it
        elif isinstance(value, str):
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
            raise TypeError(f"Parameter '{propName}' was of unsupported type. It should either be None, a string or an instance of QueryItems")



class Query(QueryParamsBase):
    def __init__(self):
        QueryParamsBase.__init__(self)
        self.resultTypeList = []


    def __repr__(self):
        """show the parameters of the query and the requested result types, e.g. QueryArticles(keyword='Tesla', resultType=['articles'])"""
        ret = QueryParamsBase.__repr__(self)
        if self.resultTypeList:
            resultTypes = [request.__dict__.get("resultType") for request in self.resultTypeList]
            ret = ret[:-1] + ("" if ret.endswith("()") else ", ") + "resultType=%r)" % resultTypes
        return ret


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


    def _copyWithRequest(self, request) -> "Query":
        """a copy of the query that asks for the given result. used to make a request without changing the query itself"""
        query = copy.copy(self)
        query.queryParams = dict(self.queryParams)
        query.resultTypeList = [request]
        return query



class QueryResultsIter:
    """
    iterator over the results of a query, returned by the execQuery() method of the QueryArticlesIter, QueryEventsIter,
    QueryMentionsIter and QueryEventArticlesIter classes. The results are downloaded page by page, as needed.
    The iterator keeps the paging state itself and does not change the query, so each execQuery() call gives an
    independent iteration - also when several of them are used at the same time.
    Iterating over the same iterator again starts from the first result (the query is executed again).
    """
    def __init__(self, eventRegistry, query: Query, createRequest, getResults, maxItems: int = -1):
        """
        Args:
            eventRegistry: instance of EventRegistry class used to make the requests
            query: the query whose results we iterate over
            createRequest: function that returns the Request* instance for the given page number
            getResults: function that returns from the response the part with the "results" and "pages" properties
            maxItems: maximum number of items to be returned (-1 for all)
        """
        self._er = eventRegistry
        self._query = query
        self._createRequest = createRequest
        self._getResults = getResults
        self._maxItems = maxItems
        self._reset()


    def _reset(self):
        self._page = 0
        self._totalPages = None
        self._currItem = 0
        # downloaded items that are yet to be returned
        self._items = []


    def _getNextBatch(self):
        """download the next page of results"""
        self._page += 1
        # if we have already obtained all pages, then exit
        if self._totalPages is not None and self._page > self._totalPages:
            return
        logger.debug("Downloading page %d of the results of %s", self._page, type(self._query).__name__)
        res = self._er.execQuery(self._query._copyWithRequest(self._createRequest(self._page)))
        if "error" in res:
            raise QueryError(str(res["error"]), statusCode = 200, responseText = str(res["error"]))
        data = self._getResults(res)
        self._totalPages = data.get("pages", 0)
        self._items.extend(data.get("results", []))


    def __iter__(self):
        # a new iteration starts from the first result again
        self._reset()
        return self


    def __next__(self):
        self._currItem += 1
        # if we want to return only the first X items, then finish once reached
        if self._maxItems >= 0 and self._currItem > self._maxItems:
            raise StopIteration
        if len(self._items) == 0:
            self._getNextBatch()
        if len(self._items) > 0:
            return self._items.pop(0)
        raise StopIteration



class IterableQuery:
    """
    mixin for the *Iter query classes. Their execQuery() returns a QueryResultsIter. For compatibility with the
    code that calls execQuery() and then iterates over the query object itself, iterating over the query iterates
    over the results of the last execQuery() call
    """
    def _setResultsIter(self, resultsIter: QueryResultsIter) -> QueryResultsIter:
        self._lastResultsIter = resultsIter
        return resultsIter


    def __iter__(self):
        if getattr(self, "_lastResultsIter", None) is None:
            raise RuntimeError("Iterating is only possible after calling the execQuery() method first")
        return iter(self._lastResultsIter)


