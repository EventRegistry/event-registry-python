"""
trending information is computed by comparing how frequently are individual concepts/categories
mentioned in the articles. By default trends are computed by comparing the total number of mentions of a concept/category
in the last two days compared to the number of mentions in the two weeks before. The trend for each concept/category
is computed as the Pearson residual. The returned concepts/categories are the ones that have the highest residual.
"""
from eventregistry.Base import *
from eventregistry.ReturnInfo import *


class TrendsBase(QueryParamsBase):
    def _getPath(self):
        return "/json/trends"


class GetTrendingConcepts(TrendsBase):
    def __init__(self,
                 source = "news",
                 count = 20,
                 conceptType = ["person", "org", "loc"],
                 returnInfo = ReturnInfo()):
        """
        get currently top trending concepts
        @param source: source information from which to compute top trends. Options: "news", "social"
        @param count: number of top trends to return
        @param conceptType: which types of concepts are we interested in
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getTrendingConcepts")
        self._setVal("source", source)
        self._setVal("conceptCount", count)
        self._setVal("conceptType", conceptType)
        self._update(returnInfo.getParams())



class GetTrendingCategories(TrendsBase):
    def __init__(self,
                 source = "news",
                 count = 20,
                 returnInfo = ReturnInfo()):
        """
        get currently top trending categories
        @param source: source information from which to compute top trends. Options: "news", "social"
        @param count: number of top trends to return
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getTrendingCategories")
        self._setVal("source", source)
        self._setVal("categoryCount", count)
        self._update(returnInfo.getParams())



class GetTrendingCustomItems(TrendsBase):
    def __init__(self,
                 count = 20,
                 returnInfo = ReturnInfo()):
        """
        get currently top trending items for which the users provided the data
        this data can be stock prices, energy prices, etc...
        @param count: number of top trends to return
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getTrendingCustom")
        self._setVal("conceptCount", count)
        self._update(returnInfo.getParams())



class GetTrendingConceptGroups(TrendsBase):
    def __init__(self,
                 source = "news",
                 count = 20,
                 returnInfo = ReturnInfo()):
        """
        get currently top trending groups of concepts
        a group can be identified by the concept type or by a concept class uri
        @param source: source information from which to compute top trends. Options: "news", "social"
        @param count: number of top trends to return
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)
        self._setVal("action", "getConceptTrendGroups")
        self._setVal("source", source)
        self._setVal("conceptCount", count)
        self._update(returnInfo.getParams())


    def getConceptTypeGroups(self, types = ["person", "org", "loc"]):
        """request trending of concepts of specified types"""
        self._setVal("conceptType", types)


    def getConceptClassUris(self, conceptClassUris):
        """request trending of concepts assigned to the specified concept classes"""
        self._setVal("conceptClassUri", conceptClassUris)

