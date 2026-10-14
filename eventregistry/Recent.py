"""
provides classes for getting new/updated events and articles
"""

import datetime
from typing import Union, List, Literal

from eventregistry.Base import QueryItems, QueryParamsBase
from eventregistry.ReturnInfo import ReturnInfo
from eventregistry.EventRegistry import EventRegistry
from eventregistry.QueryArticles import QueryArticles
from eventregistry.QueryEvents import QueryEvents

# the names exported by "from eventregistry import *"
__all__ = ["GetRecentEvents", "GetRecentArticles"]


class GetRecentEvents(QueryParamsBase):
    def __init__(self,
                 eventRegistry: EventRegistry,
                 mandatoryLang: Union[str, List[str], None] = None,
                 mandatoryLocation: bool = True,
                 returnInfo: Union[ReturnInfo, None] = None,
                 maxEventCount: Union[int, None] = None,
                 updatesAfterMinsAgo: Union[int, None] = None,
                 updatesAfterTm: Union[datetime.datetime, str, None] = None,
                 keywords: Union[str, QueryItems, None] = None,
                 conceptUri: Union[str, QueryItems, None] = None,
                 categoryUri: Union[str, QueryItems, None] = None,
                 sourceUri: Union[str, QueryItems, None] = None,
                 sourceLocationUri: Union[str, QueryItems, None] = None,
                 sourceGroupUri: Union[str, QueryItems, None] = None,
                 authorUri: Union[str, QueryItems, None] = None,
                 locationUri: Union[str, QueryItems, None] = None,
                 lang: Union[str, QueryItems, None] = None,
                 keywordsLoc: str = "body",
                 minArticlesInEvent: Union[int, None] = None,
                 maxArticlesInEvent: Union[int, None] = None,
                 **kwargs):
        """
        Return info about recently added/modified events

        Args:
            eventRegistry: instance of class EventRegistry
            mandatoryLang: set a lang or array of langs if you wish to only get events covered at least by the specified language
            mandatoryLocation: if set to True then return only events that have a known geographic location
            returnInfo: what details should be included in the returned information
            maxEventCount: the maximum number of events to return in a call
            updatesAfterMinsAgo: return the events added or updated in the last specified number of minutes (instead of since the last minute)
            updatesAfterTm: return the events added or updated after the given time (a datetime or a string in the 'YYYY-MM-DDTHH:MM:SS' format, in UTC)
            keywords: return only the events where articles mention the keywords. A string or QueryItems.AND() / QueryItems.OR()
            conceptUri: return only the events about the concept(s). A string or QueryItems.AND() / QueryItems.OR()
            categoryUri: return only the events in the category/categories. A string or QueryItems.AND() / QueryItems.OR()
            sourceUri: return only the events reported by the news source(s). A string or QueryItems.OR()
            sourceLocationUri: return only the events reported by the news sources from the location(s). A string or QueryItems.OR()
            sourceGroupUri: return only the events reported by the news sources in the source group(s). A string or QueryItems.OR()
            authorUri: return only the events with articles written by the author(s). A string or QueryItems.OR()
            locationUri: return only the events that happened at the location(s). A string or QueryItems.OR()
            lang: return only the events reported in the language(s). A string or QueryItems.OR()
            keywordsLoc: where should we look when searching using the keywords: "body" (default), "title", or "body,title"
            minArticlesInEvent: return only the events with at least this many articles
            maxArticlesInEvent: return only the events with at most this many articles
            kwargs: other parameters that should be sent with the request
        """
        QueryParamsBase.__init__(self)

        self._er = eventRegistry
        # the conditions are encoded in the same way as in QueryEvents (validation, operators)
        conditions = QueryEvents(keywords = keywords, conceptUri = conceptUri, categoryUri = categoryUri, sourceUri = sourceUri,
            sourceLocationUri = sourceLocationUri, sourceGroupUri = sourceGroupUri, authorUri = authorUri, locationUri = locationUri,
            lang = lang, keywordsLoc = keywordsLoc, minArticlesInEvent = minArticlesInEvent, maxArticlesInEvent = maxArticlesInEvent)
        self.queryParams.update({name: val for name, val in conditions.queryParams.items() if name != "action"})

        self._setVal("recentActivityEventsMandatoryLocation", mandatoryLocation)
        # return only events that have at least a story in the specified language
        if mandatoryLang is not None:
            self._setVal("recentActivityEventsMandatoryLang", mandatoryLang)
        if maxEventCount is not None:
            self._setVal("recentActivityEventsMaxEventCount", maxEventCount)
        if updatesAfterMinsAgo is not None:
            self._setVal("recentActivityEventsUpdatesAfterMinsAgo", updatesAfterMinsAgo)
        if updatesAfterTm is not None:
            self._setVal("recentActivityEventsUpdatesAfterTm", self.encodeDateTime(updatesAfterTm))
        self.queryParams.update(kwargs)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("recentActivityEvents"))


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
                 returnInfo: Union[ReturnInfo, None] = None,
                 maxArticleCount: Union[int, None] = None,
                 updatesAfterMinsAgo: Union[int, None] = None,
                 updatesAfterTm: Union[datetime.datetime, str, None] = None,
                 keywords: Union[str, QueryItems, None] = None,
                 conceptUri: Union[str, QueryItems, None] = None,
                 categoryUri: Union[str, QueryItems, None] = None,
                 sourceUri: Union[str, QueryItems, None] = None,
                 sourceLocationUri: Union[str, QueryItems, None] = None,
                 sourceGroupUri: Union[str, QueryItems, None] = None,
                 authorUri: Union[str, QueryItems, None] = None,
                 locationUri: Union[str, QueryItems, None] = None,
                 lang: Union[str, QueryItems, None] = None,
                 keywordsLoc: str = "body",
                 dataType: Union[str, List[str]] = "news",
                 isDuplicateFilter: Literal["skipDuplicates", "keepOnlyDuplicates", "keepAll"] = "keepAll",
                 eventFilter: Literal["skipArticlesWithoutEvent", "keepOnlyArticlesWithoutEvent", "keepAll"] = "keepAll",
                 startSourceRankPercentile: int = 0,
                 endSourceRankPercentile: int = 100,
                 minSentiment: float = -1,
                 maxSentiment: float = 1,
                 **kwargs):
        """
        Return info about recently added articles

        Args:
            eventRegistry: instance of class EventRegistry
            mandatorySourceLocation: if True then return only articles from sources for which we know geographic location
            articleLang: None, string or a list of strings, depending if we should return all articles, or articles in one or more languages
            returnInfo: what details should be included in the returned information
            maxArticleCount: the maximum number of articles to return in a call
            updatesAfterMinsAgo: return the articles added in the last specified number of minutes (instead of since the previous call)
            updatesAfterTm: return the articles added after the given time (a datetime or a string in the 'YYYY-MM-DDTHH:MM:SS' format, in UTC)
            keywords: return only the articles that mention the keywords. A string or QueryItems.AND() / QueryItems.OR()
            conceptUri: return only the articles that mention the concept(s). A string or QueryItems.AND() / QueryItems.OR()
            categoryUri: return only the articles in the category/categories. A string or QueryItems.AND() / QueryItems.OR()
            sourceUri: return only the articles from the news source(s). A string or QueryItems.OR()
            sourceLocationUri: return only the articles from the news sources from the location(s). A string or QueryItems.OR()
            sourceGroupUri: return only the articles from the news sources in the source group(s). A string or QueryItems.OR()
            authorUri: return only the articles written by the author(s). A string or QueryItems.OR()
            locationUri: return only the articles about something that happened at the location(s). A string or QueryItems.OR()
            lang: return only the articles in the language(s). A string or QueryItems.OR()
            keywordsLoc: where should we look when searching using the keywords: "body" (default), "title", or "body,title"
            dataType: what data types should we return: "news" (default), "pr", "blog" or a list of them
            isDuplicateFilter: "skipDuplicates" (skip the articles that are duplicates of other articles), "keepOnlyDuplicates" or "keepAll" (default)
            eventFilter: "skipArticlesWithoutEvent", "keepOnlyArticlesWithoutEvent" or "keepAll" (default)
            startSourceRankPercentile: starting percentile of the sources to consider in the results (default: 0). Value should be in range 0-90 and divisible by 10
            endSourceRankPercentile: ending percentile of the sources to consider in the results (default: 100). Value should be in range 10-100 and divisible by 10
            minSentiment: minimum value of the sentiment that the returned articles should have. Range [-1, 1]
            maxSentiment: maximum value of the sentiment that the returned articles should have. Range [-1, 1]
            kwargs: other parameters that should be sent with the request
        """
        QueryParamsBase.__init__(self)

        self._er = eventRegistry
        # the conditions are encoded in the same way as in QueryArticles (validation, operators)
        conditions = QueryArticles(keywords = keywords, conceptUri = conceptUri, categoryUri = categoryUri, sourceUri = sourceUri,
            sourceLocationUri = sourceLocationUri, sourceGroupUri = sourceGroupUri, authorUri = authorUri, locationUri = locationUri,
            lang = lang, keywordsLoc = keywordsLoc, dataType = dataType, isDuplicateFilter = isDuplicateFilter, eventFilter = eventFilter,
            startSourceRankPercentile = startSourceRankPercentile, endSourceRankPercentile = endSourceRankPercentile,
            minSentiment = minSentiment, maxSentiment = maxSentiment)
        self.queryParams.update({name: val for name, val in conditions.queryParams.items() if name != "action"})

        self._setVal("recentActivityArticlesMandatorySourceLocation", mandatorySourceLocation)
        if articleLang is not None:
            self._setVal("recentActivityArticlesLang", articleLang)
        if maxArticleCount is not None:
            self._setVal("recentActivityArticlesMaxArticleCount", maxArticleCount)
        if updatesAfterMinsAgo is not None:
            self._setVal("recentActivityArticlesUpdatesAfterMinsAgo", updatesAfterMinsAgo)
        if updatesAfterTm is not None:
            self._setVal("recentActivityArticlesUpdatesAfterTm", self.encodeDateTime(updatesAfterTm))
        self.queryParams.update(kwargs)
        self._update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("recentActivityArticles"))


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
            return ret["recentActivityArticles"].get("activity", [])
        # or empty
        return []
