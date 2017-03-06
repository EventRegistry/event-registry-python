"""
provides classes for getting new/updated events and articles
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class GetRecentEvents(QueryParamsBase):
    def __init__(self,
                 eventRegistry,
                 maxCount = 500,
                 mandatoryLang = None,
                 mandatoryLocation = True,
                 returnInfo = ReturnInfo()):
        """
        return info about recently modified events

        @param eventRegistry: instance of class EventRegistry
        @param maxCount: max events to return per call (max 500). use only if the provided number is too large
        @param mandatoryLang: set a lang or array of langs if you wish to only get events covered at least by the specified language
        @param mandatoryLocation: if set to True then return only events that have a known geographic location
        """
        QueryParamsBase.__init__(self)

        assert maxCount <= 500, "Maximum number of events returned per call is 500"
        self._er = eventRegistry
        self._setVal("addEvents", True)
        self._setVal("addArticles", False)
        self._setVal("recentActivityEventsMaxEventCount", maxCount)
        self._setVal("recentActivityEventsMandatoryLocation", mandatoryLocation)
        # return only events that have at least a story in the specified language
        if mandatoryLang != None:
            self._setVal("recentActivityEventsMandatoryLang", mandatoryLang)
        self._update(returnInfo.getParams("recentActivityEvents"))


    def _getPath(self):
        return "/json/minuteStream"


    def getUpdates(self):
        """
        Get the latest new or updated events from Event Registry
        NOTE: call this method exactly once per minute - calling it more frequently will return the same results multiple times,
        calling it less frequently will miss on some results. Results are computed once a minute.
        """
        # execute the query
        ret = self._er.execQuery(self)

        if ret and ret.get("recentActivity") and ret["recentActivity"].get("events"):
            # return the updated information
            return ret["recentActivity"]["events"]
        # or empty
        return {}



class GetRecentArticles(QueryParamsBase):
    def __init__(self,
                 eventRegistry,
                 maxCount = 500,
                 mandatorySourceLocation = False,
                 articleLang = None,
                 returnInfo = ReturnInfo()):
        """
        return info about recently added articles

        @param eventRegistry: instance of class EventRegistry
        @param maxCount: max articles to return per call (max 500). use only if the provided number is too large
        @param mandatorySourceLocation: if True then return only articles from sources for which we know geographic location
        @param articleLang: None, string or a list of strings, depending if we should return all articles, or articles in one or more languages
        """
        QueryParamsBase.__init__(self)

        assert maxCount <= 500, "Maximum number of articles returned per call is 500"
        self._er = eventRegistry
        self._setVal("addEvents", False)
        self._setVal("addArticles", True)
        self._setVal("recentActivityArticlesMaxArticleCount", maxCount)
        self._setVal("recentActivityArticlesMandatorySourceLocation", mandatorySourceLocation)
        if articleLang != None:
            self._setVal("recentActivityArticlesLang", articleLang)
        self._update(returnInfo.getParams("recentActivityArticles"))


    def _getPath(self):
        return "/json/minuteStream"


    def getUpdates(self):
        """
        Get the latest new or updated events articles Event Registry.
        NOTE: call this method exactly once per minute - calling it more frequently will return the same results multiple times,
        calling it less frequently will miss on some results. Results are computed once a minute.
        """
        # execute the query
        ret = self._er.execQuery(self)

        if ret and ret.get("recentActivity") and ret["recentActivity"].get("articles"):
            # return the latest articles
            return ret["recentActivity"]["articles"]["activity"]
        # or empty
        return []
