"""
provides classes for getting new/updated events and articles
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class GetRecentEvents(QueryParamsBase):
    def __init__(self,
            maxEventCount = 60,
            maxMinsBack = 10 * 60,
            mandatoryLang = None,
            mandatoryLocation = True,
            lastActivityId = 0,
            returnInfo = ReturnInfo()):
        """
        return info about recently modified events

        @param maxEventCount: determines the maximum number of events to return in a single call (max 250)
        @param maxMinsBack: sets how much in the history are we interested to look
        @param mandatoryLang: set a lang or array of langs if you wish to only get events covered at least by the specified language
        @param mandatoryLocation: if set to True then return only events that have a known geographic location
        @param lastActivityId: this is another way of settings how much in the history are we interested to look. Set when you have repeated calls of the method. Set it to lastActivityId obtained in the last response
        """
        QueryParamsBase.__init__(self)

        assert maxEventCount <= 1000
        self._setVal("action", "getRecentActivity")
        self._setVal("addEvents", True)
        self._setVal("addArticles", False)
        self._setVal("recentActivityEventsMaxEventCount", maxEventCount)
        self._setVal("recentActivityEventsMaxMinsBack", maxMinsBack)
        self._setVal("recentActivityEventsMandatoryLocation", mandatoryLocation)
        self._setVal("recentActivityEventsLastActivityId", lastActivityId)
        # return only events that have at least a story in the specified language
        if mandatoryLang != None:
            self._setVal("recentActivityEventsMandatoryLang", mandatoryLang)
        self._update(returnInfo.getParams("recentActivityEvents"))

    def _getPath(self):
        return "/json/overview"

    def getUpdates(self, er):
        """
        Get the latest new or updated events from Event Registry
        This method is to be called repeatedly, each it will return only events that were changed since the last call
        @param er: instance of EventRegistry class
        """
        # execute the query
        ret = er.execQuery(self)

        # extract the latest activity id and remember it for the next query
        if ret and ret.get("recentActivity") and ret["recentActivity"].get("events"):
            lastActivityId =  ret["recentActivity"]["events"].get("newestActivityId", 0)
            self._setVal("recentActivityEventsLastActivityId", lastActivityId)
            # return the updated information
            return ret["recentActivity"]["events"]
        # or empty
        return {}


class GetRecentArticles(QueryParamsBase):
    def __init__(self,
            maxArticleCount = 60,
            maxMinsBack = 10 * 60,
            mandatorySourceLocation = False,
            lastActivityId = 0,
            returnInfo = ReturnInfo()):
        """
        return info about recently added articles
        @param maxArticleCount: determines the maximum number of articles to return in a single call (max 250)
        @param maxMinsBack: sets how much in the history are we interested to look
        @param mandatorySourceLocation: if True then return only articles from sources for which we know geographic location
        @param lastActivityId: another way of settings how much in the history are we interested to look. Set when you have repeated calls of the method. Set it to lastActivityId obtained in the last response
        """
        QueryParamsBase.__init__(self)

        assert maxArticleCount <= 1000
        self._setVal("action", "getRecentActivity")
        self._setVal("addEvents", False)
        self._setVal("addArticles", True)
        self._setVal("recentActivityArticlesMaxArticleCount", maxArticleCount)
        self._setVal("recentActivityArticlesMaxMinsBack", maxMinsBack)
        self._setVal("recentActivityArticlesMandatorySourceLocation", mandatorySourceLocation)
        self._setVal("recentActivityArticlesLastActivityId", lastActivityId)
        self._update(returnInfo.getParams("recentActivityArticles"))

    def _getPath(self):
        return "/json/overview"

    def getUpdates(self, er):
        """
        Get the latest new or updated events articles Event Registry
        This method is to be called repeatedly, each it will return only articles that were added since the last call
        @param er: instance of EventRegistry class
        """
        # execute the query
        ret = er.execQuery(self)

        # extract the latest activity id and remember it for the next query
        if ret and ret.get("recentActivity") and ret["recentActivity"].get("articles"):
            lastActivityId = ret["recentActivity"]["articles"].get("lastActivityId", 0)
            self._setVal("recentActivityArticlesLastActivityId", lastActivityId)
            # return the latest articles
            return ret["recentActivity"]["articles"]["activity"]
        # or empty
        return []
