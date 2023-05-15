"""
provides classes for obtaining information about how frequently individual concepts or categories
have been mentioned in news articles (if source == "news") of in social media (if source == "social")
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from typing import Union, List


class CountsBase(QueryParamsBase):
    def _getPath(self):
        return "/api/v1/counters"



class GetCounts(CountsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str]],
                 type: Union[str, List[str]] = "concept",
                 returnInfo: ReturnInfo = ReturnInfo()):
        """
        obtain information about how frequently a concept or category is mentioned in the articles on particular dates
        The uri for these can be found using EventRegistry.getCustomConceptUri() method.
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

        @param uriOrUriList: concept/category uri or a list of uris
        @param type: what do the uris represent? "concept" or "category"
        @param returnInfo: what details should be included in the returned information
        """
        CountsBase.__init__(self)
        self._setVal("action", "getCounts")
        self._setVal("type", type)
        self._update(returnInfo.getParams())
        self._setVal("uri", uriOrUriList)



class GetCountsEx(CountsBase):
    def __init__(self,
                 uriOrUriList: Union[str, List[str]],
                 type: str = "concept",
                 returnInfo: ReturnInfo = ReturnInfo()):
        """
        obtain information about how frequently a concept or category is mentioned in the articles on particular dates
        Similar to GetCounts, but the output is more friendly for a larger set of provided uris/ids at once
        Usage example:
            q = GetCountsEx(type = "category")
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

        @param uriOrUriList: concept/category uri or a list of uris
        @param source: input source information from which to compute top trends. Options: "news", "social"
        @param type: what do the uris represent? "concept" or "category"
        @param returnInfo: what details should be included in the returned information
        """
        CountsBase.__init__(self)
        self._setVal("action", "getCountsEx")
        self._setVal("type", type)
        self._update(returnInfo.getParams())
        self._setVal("uri", uriOrUriList)
