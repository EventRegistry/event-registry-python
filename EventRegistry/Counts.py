"""
provides classes for obtaining information about how frequently individual concepts or categories
have been mentioned in news articles (if source == "news") of in social media (if source == "social")
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class CountsBase(QueryParamsBase):
    def _getPath(self):
        return "/json/counters"

class GetCounts(CountsBase):
    """
    obtain information about how frequently a concept or category is mentioned in the articles on particular dates
    by specifying source="custom" one can obtain counts for custom concepts, such as stocks, macroeconomic indicators, etc. The uri
    for these can be found using EventRegistry.getCustomConceptUri() method.
    Usage example:
        q = GetCounts([er.getConceptUri("Obama"), er.getConceptUri("ebola")])
        ret = er.execQuery(q)
    Return object:
        {
            "http://en.wikipedia.org/wiki/Barack_Obama": [
                {
                    "count": 1,
                    "date": "2015-05-07"
                },
                {
                    "count": 4,
                    "date": "2015-05-08"
                },
                ...
            ],
            "http://en.wikipedia.org/wiki/Ebola_virus_disease": [
                {
                    "count": 0,
                    "date": "2015-05-07"
                },
                ...
            ]
        }
    """
    def __init__(self,
                 uriOrUriList = None, # concept/category uri or a list of uris
                 source = "news",   # input source information from which to compute top trends. Options: "news", "social", "custom", "geo" or "sentiment"
                 type = "concept",  # what do the uris represent? "concept" or "category"
                 startDate = None,  # starting date from which to provide counts onwards (either None, datetime.date or "YYYY-MM-DD")
                 endDate = None,    # ending date until which to provide counts (either None, datetime.date or "YYYY-MM-DD")
                 returnInfo = ReturnInfo()):     # specify the details of the concepts/categories to return
        CountsBase.__init__(self)
        self._setVal("action", "getCounts")
        self._setVal("source", source)
        self._setVal("type", type)
        self._update(returnInfo.getParams())
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        if startDate != None or endDate != None:
            self.setDateRange(startDate, endDate)

    def queryById(self, idOrIdList):
        """search concepts by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search concepts by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def setDateRange(self, startDate, endDate):
        """set the starting and ending dates for the returned counts"""
        if startDate != None:
            self._setDateVal("startDate", startDate)
        if endDate != None:
            self._setDateVal("endDate", endDate)


class GetCountsEx(CountsBase):
    """
    obtain information about how frequently a concept or category is mentioned in the articles on particular dates
    Similar to GetCounts, but the output is more friendly for a larger set of provided uris/ids at once
    Usage example:
        q = GetCountsEx(type = "category")
        q.queryById(range(10))  # return trends of first 10 categories
        ret = er.execQuery(q)
    Return object:
        {
            "categoryInfo": [
                {
                    "id": 0,
                    "label": "Root",
                    "uri": "http://www.dmoz.org"
                },
                {
                    "id": 1,
                    "label": "Recreation",
                    "uri": "http://www.dmoz.org/Recreation"
                },
                ...
            ],
            "counts": [
                {
                    "0": 23, "1": 42, "2": 52, "3": 32, "4": 21, "5": 65, "6": 32, "7": 654, "8": 1, "9": 34,
                    "date": "2015-05-07"
                },
                ...
            ]
        }
    """
    def __init__(self,
                 uriOrUriList = None, # concept/category uri or a list of uris
                 source = "news",   # input source information from which to compute top trends. Options: "news", "social"
                 type = "concept",  # what do the uris represent? "concept" or "category"
                 startDate = None,  # starting date from which to provide counts onwards (either None, datetime.date or "YYYY-MM-DD")
                 endDate = None,    # ending date until which to provide counts (either None, datetime.date or "YYYY-MM-DD")
                 returnInfo = ReturnInfo()):     # specify the details of the concepts/categories to return
        CountsBase.__init__(self)
        self._setVal("action", "getCountsEx")
        self._setVal("source", source)
        self._setVal("type", type)
        self._update(returnInfo.getParams())
        if uriOrUriList != None:
            self.queryByUri(uriOrUriList)
        if startDate != None or endDate != None:
            self.setDateRange(startDate, endDate)

    def queryById(self, idOrIdList):
        """search concepts by id(s)"""
        self._setVal("id", idOrIdList)

    def queryByUri(self, uriOrUriList):
        """search concepts by uri(s)"""
        self._setVal("uri", uriOrUriList)

    def setDateRange(self, startDate, endDate):
        """set the starting and ending dates for the returned counts"""
        if startDate != None:
            self._setDateVal("startDate", startDate)
        if endDate != None:
            self._setDateVal("endDate", endDate)
