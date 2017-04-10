from .Base import QueryParamsBase
import six


class QueryOper:
    _AND = "$and"
    _OR = "$or"
    _Undef = None

    def __init__(self, oper, items):
        self._oper = oper
        self._items = items;

    @staticmethod
    def AND(items):
        return QueryOper(QueryOper._AND, items)

    @staticmethod
    def OR(items):
        return QueryOper(QueryOper._OR, items)

    def getOper(self):
        return self._oper

    def getItems(self):
        return self._items



class QueryType:
    Event = 1
    Story = 2
    Article = 3
    Undef = None


class _QueryCore(object):
    def __init__(self):
        self._queryObj = {}


    def getQuery(self):
        return self._queryObj


    def setQueryParam(self, paramName, val):
        self._queryObj[paramName] = val


    def _setValIfNotDefault(self, propName, value, defVal):
        if value != defVal:
            self._queryObj[propName] = value



class BaseQuery(_QueryCore):
    def __init__(self,
                 keywords = None,
                 conceptUri = None,
                 sourceUri = None,
                 locationUri = None,
                 categoryUri = None,
                 lang = None,
                 dateStart = None,
                 dateEnd = None,
                 dateMentionStart = None,
                 dateMentionEnd = None,
                 categoryIncludeSub = True,
                 minMaxArticlesInEvent = None):
        super(BaseQuery, self).__init__()

        self._setQueryArrVal("keywords", keywords)
        self._setQueryArrVal("conceptUri", conceptUri)
        self._setQueryArrVal("sourceUri", sourceUri)
        self._setQueryArrVal("locationUri", locationUri)
        self._setQueryArrVal("categoryUri", categoryUri)
        self._setQueryArrVal("lang", lang)

        # starting date of the published articles (e.g. 2014-05-02)
        if dateStart != None:
            self._queryObj["dateStart"] = QueryParamsBase.encodeDate(dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if dateEnd != None:
            self._queryObj["dateEnd"] = QueryParamsBase.encodeDate(dateEnd)

        # first valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionStart != None:
            self._queryObj["dateMentionStart"] = QueryParamsBase.encodeDate(dateMentionStart)
        # last valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionEnd != None:
            self._queryObj["dateMentionEnd"] = QueryParamsBase.encodeDate(dateMentionEnd)
        if minMaxArticlesInEvent != None:
            assert isinstance(minMaxArticlesInEvent, tuple), "minMaxArticlesInEvent parameter should either be None or a tuple with two integer values"
            self._queryObj["minArticlesInEvent"] = minMaxArticlesInEvent[0]
            self._queryObj["maxArticlesInEvent"] = minMaxArticlesInEvent[1]


    def _setQueryArrVal(self, propName, value):
        # by default we have None - so don't do anything
        if value is None:
            return
        # if we have an instance of QueryOper then apply it
        if isinstance(value, QueryOper):
            self._queryObj[propName] = { value.getOper(): value.getItems() }

        # if we have a string value, just use it
        elif isinstance(value, six.string_types):
            self._queryObj[propName] = value
        # there should be no other valid types
        else:
            assert False, "Parameter '%s' was of unsupported type" % (propName)



class CombinedQuery(_QueryCore):
    def __init__(self):
        super(CombinedQuery, self).__init__()


    @staticmethod
    def AND(queryArr):
        assert isinstance(queryArr, list), "provided argument as not a list"
        assert len(queryArr) > 0, "queryArr had an empty list"
        q = CombinedQuery()
        q.setQueryParam("$and", [])
        for item in queryArr:
            assert isinstance(item, (CombinedQuery, BaseQuery)), "item in the list was not a CombinedQuery or BaseQuery instance"
            q.getQuery()["$and"].append(item.getQuery())
        return q


    @staticmethod
    def OR(queryArr):
        assert isinstance(queryArr, list), "provided argument as not a list"
        assert len(queryArr) > 0, "queryArr had an empty list"
        q = CombinedQuery()
        q.setQueryParam("$or", [])
        for item in queryArr:
            assert isinstance(item, (CombinedQuery, BaseQuery)), "item in the list was not a CombinedQuery or BaseQuery instance"
            q.getQuery()["$or"].append(item.getQuery())
        return q



class ComplexArticleQuery(_QueryCore):
    def __init__(self,
                 includeQuery,
                 excludeQuery = None,
                 isDuplicateFilter = "keepAll",
                 hasDuplicateFilter = "keepAll",
                 eventFilter = "keepAll"):
        super(ComplexArticleQuery, self).__init__()

        assert isinstance(includeQuery, (CombinedQuery, BaseQuery)), "includeQuery parameter was not a CombinedQuery or BaseQuery instance"
        self._queryObj["include"] = includeQuery.getQuery()
        if excludeQuery != None:
            assert isinstance(excludeQuery, (CombinedQuery, BaseQuery)), "excludeQuery parameter was not a CombinedQuery or BaseQuery instance"
            self._queryObj["exclude"] = excludeQuery.getQuery()

        self._setValIfNotDefault("isDuplicateFilter", isDuplicateFilter, "keepAll")
        self._setValIfNotDefault("hasDuplicateFilter", hasDuplicateFilter, "keepAll")
        self._setValIfNotDefault("eventFilter", eventFilter, "keepAll")



class ComplexEventQuery(_QueryCore):
    def __init__(self,
                 includeQuery,
                 excludeQuery = None):
        super(ComplexEventQuery, self).__init__()

        assert isinstance(includeQuery, (CombinedQuery, BaseQuery)), "includeQuery parameter was not a CombinedQuery or BaseQuery instance"
        self._queryObj["include"] = includeQuery.getQuery()
        if excludeQuery != None:
            assert isinstance(excludeQuery, (CombinedQuery, BaseQuery)), "excludeQuery parameter was not a CombinedQuery or BaseQuery instance"
            self._queryObj["exclude"] = excludeQuery.getQuery()
