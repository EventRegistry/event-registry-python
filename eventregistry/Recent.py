"""
provides classes for getting new/updated events and articles
"""

from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List

class GetRecentEvents(QueryParamsBase):
    def __init__(self,
                 eventRegistry: EventRegistry,
                 mandatoryLang: Union[str, List[str], None] = None,
                 mandatoryLocation: bool = True,
                 returnInfo: ReturnInfo = ReturnInfo(),
                 **kwargs):
        """
        Return info about recently added/modified events
        @param eventRegistry: instance of class EventRegistry
        @param mandatoryLang: set a lang or array of langs if you wish to only get events covered at least by the specified language
        @param mandatoryLocation: if set to True then return only events that have a known geographic location
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)

        self._er = eventRegistry
        self._setVal("recentActivityEventsMandatoryLocation", mandatoryLocation)
        # return only events that have at least a story in the specified language
        if mandatoryLang is not None:
            self._setVal("recentActivityEventsMandatoryLang", mandatoryLang)
        self.queryParams.update(kwargs)
        self._update(returnInfo.getParams("recentActivityEvents"))


    def _getPath(self):
        return "/api/v1/minuteStreamEvents"


    def getUpdates(self):
        """
        Get the latest new or updated events from Event Registry
        NOTE: call this method exactly once per minute - calling it more frequently will return the same results multiple times,
        calling it less frequently will miss on some results. Results are computed once a minute.
        """
        # execute the query
        ret = self._er.execQuery(self)

        if ret and "recentActivityEvents" in ret:
            # return the updated information
            return ret["recentActivityEvents"]
        # or empty
        return {}



class GetRecentArticles(QueryParamsBase):
    def __init__(self,
                 eventRegistry: EventRegistry,
                 mandatorySourceLocation: bool = False,
                 articleLang: Union[str, List[str], None] = None,
                 returnInfo: ReturnInfo = ReturnInfo(),
                 **kwargs):
        """
        Return info about recently added articles
        @param eventRegistry: instance of class EventRegistry
        @param mandatorySourceLocation: if True then return only articles from sources for which we know geographic location
        @param articleLang: None, string or a list of strings, depending if we should return all articles, or articles in one or more languages
        @param returnInfo: what details should be included in the returned information
        """
        QueryParamsBase.__init__(self)

        self._er = eventRegistry
        self._setVal("recentActivityArticlesMandatorySourceLocation", mandatorySourceLocation)
        if articleLang is not None:
            self._setVal("recentActivityArticlesLang", articleLang)
        self.queryParams.update(kwargs)
        self._update(returnInfo.getParams("recentActivityArticles"))


    def _getPath(self):
        return "/api/v1/minuteStreamArticles"


    def getUpdates(self):
        """
        Get the latest new or updated events articles Event Registry.
        NOTE: call this method exactly once per minute - calling it more frequently will return the same results multiple times,
        calling it less frequently will miss on some results. Results are computed once a minute.
        """
        # execute the query
        ret = self._er.execQuery(self)

        if ret and "recentActivityArticles" in ret:
            # store the latest seen uris for each requested data type
            if "newestUri" in ret["recentActivityArticles"]:
                for key, val in ret["recentActivityArticles"]["newestUri"].items():
                    self.queryParams["recentActivityArticles" + key[0].upper() + key[1:] + "UpdatesAfterUri"] = val

            # return the latest articles
            return ret["recentActivityArticles"]["activity"]
        # or empty
        return []
