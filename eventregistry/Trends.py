"""
trending information is computed by comparing how frequently are individual concepts/categories
mentioned in the articles. By default trends are computed by comparing the total number of mentions of a concept/category
in the last two days compared to the number of mentions in the two weeks before. The trend for each concept/category
is computed as the Pearson residual. The returned concepts/categories are the ones that have the highest residual.
"""
from typing import List, Union
from eventregistry.Base import QueryParamsBase
from eventregistry.ReturnInfo import ReturnInfo

# the names exported by "from eventregistry import *"
__all__ = ["TrendsBase", "GetTrendingConcepts", "GetTrendingCategories", "GetTrendingCustomItems",
           "GetTrendingConceptGroups"]


class TrendsBase(QueryParamsBase):
    def _getPath(self):
        return "/api/v1/trends"


class GetTrendingConcepts(TrendsBase):
    def __init__(self,
                 source: str = "news",
                 count: int = 20,
                 conceptType: Union[str, List[str], None] = None,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get currently top trending concepts

        Args:
            source: source information from which to compute top trends. Options: "news", "social", "pr", "blogs"
            count: number of top trends to return
            conceptType: which types of concepts are we interested in
            returnInfo: what details should be included in the returned information
        """
        TrendsBase.__init__(self)
        self._setVal("action", "getTrendingConcepts")
        self._setVal("source", source)
        if source != "social":
            self._setVal("dataType", source)
        self._setVal("conceptCount", count)
        self._setVal("conceptType", conceptType if conceptType is not None else ["person", "org", "loc"])
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())



class GetTrendingCategories(TrendsBase):
    def __init__(self,
                 source: str = "news",
                 count: int = 20,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get currently top trending categories

        Args:
            source: source information from which to compute top trends. Options: "news", "social", "pr", "blogs"
            count: number of top trends to return
            returnInfo: what details should be included in the returned information
        """
        TrendsBase.__init__(self)
        self._setVal("action", "getTrendingCategories")
        self._setVal("source", source)
        if source != "social":
            self._setVal("dataType", source)
        self._setVal("categoryCount", count)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())



class GetTrendingCustomItems(TrendsBase):
    def __init__(self,
                 count: int = 20,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get currently top trending items for which the users provided the data
        this data can be stock prices, energy prices, etc...

        Args:
            count: number of top trends to return
            returnInfo: what details should be included in the returned information
        """
        TrendsBase.__init__(self)
        self._setVal("action", "getTrendingCustom")
        self._setVal("conceptCount", count)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())



class GetTrendingConceptGroups(TrendsBase):
    def __init__(self,
                 source: str = "news",
                 count: int = 20,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get currently top trending groups of concepts
        a group can be identified by the concept type or by a concept class uri

        Args:
            source: source information from which to compute top trends. Options: "news", "social"
            count: number of top trends to return
            returnInfo: what details should be included in the returned information
        """
        TrendsBase.__init__(self)
        self._setVal("action", "getConceptTrendGroups")
        self._setVal("source", source)
        self._setVal("conceptCount", count)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())


    def getConceptTypeGroups(self, types: Union[str, List[str], None] = None):
        """request trending of concepts of specified types"""
        self._setVal("conceptType", types if types is not None else ["person", "org", "loc"])


    def getConceptClassUris(self, conceptClassUris: Union[str, List[str]]):
        """request trending of concepts assigned to the specified concept classes"""
        self._setVal("conceptClassUri", conceptClassUris)

