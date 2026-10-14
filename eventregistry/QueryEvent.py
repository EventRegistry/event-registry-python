import json
import datetime
from eventregistry.Base import IterableQuery, Query, QueryItems, QueryParamsBase, QueryResultsIter
from eventregistry.Exceptions import QueryError
from eventregistry.ReturnInfo import ArticleInfoFlags, ReturnInfo
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List, Literal

# the names exported by "from eventregistry import *"
__all__ = ["QueryEvent", "QueryEventArticlesIter", "RequestEvent", "RequestEventInfo", "RequestEventArticles",
           "RequestEventArticleUriWgts", "RequestEventKeywordAggr", "RequestEventSourceAggr",
           "RequestEventDateMentionAggr", "RequestEventArticleTrend", "RequestEventSimilarEvents"]


class QueryEvent(Query):
    """
    Class for obtaining available info for one or more events in the Event Registry
    """
    def __init__(self,
                 eventUriOrList: Union[str, List[str]],
                 requestedResult: Union["RequestEvent", None] = None):
        """
        Args:
            eventUriOrUriList: a single event uri or a list of event uris (max 50)
            requestedResult: the information to return as the result of the query. By default return the details of the event
        """
        super().__init__()
        self._setVal("action", "getEvent")
        self._setVal("eventUri", eventUriOrList)
        self.setRequestedResult(requestedResult or RequestEventInfo())


    def _getPath(self):
        return "/api/v1/event"


    def setRequestedResult(self, requestEvent: "RequestEvent"):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestEvent base class (see classes below).
        """
        if not (isinstance(requestEvent, RequestEvent)):
            raise TypeError("QueryEvent class can only accept result requests that are of type RequestEvent")
        self.resultTypeList = [requestEvent]



class QueryEventArticlesIter(IterableQuery, QueryEvent):
    """
    Class for obtaining an iterator over all articles in the event
    """
    def __init__(self, eventUri: str,
                lang: Union[str, QueryItems, None] = None,
                keywords: Union[str, QueryItems, None] = None,
                conceptUri: Union[str, QueryItems, None] = None,
                categoryUri: Union[str, QueryItems, None] = None,
                sourceUri: Union[str, QueryItems, None] = None,
                sourceLocationUri: Union[str, QueryItems, None] = None,
                sourceGroupUri: Union[str, QueryItems, None] = None,
                authorUri: Union[str, QueryItems, None] = None,
                locationUri: Union[str, QueryItems, None] = None,
                dateStart: Union[datetime.datetime, datetime.date, str, None] = None,
                dateEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                dateMentionStart: Union[datetime.datetime, datetime.date, str, None] = None,
                dateMentionEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                keywordsLoc: str = "body",
                keywordSearchMode: Literal["simple", "exact", "phrase"] = "phrase",

                startSourceRankPercentile: int = 0,
                endSourceRankPercentile: int = 100,
                minSentiment: float = -1,
                maxSentiment: float = 1):
        """
        Args:
            eventUri: a single event for which we want to obtain the list of articles in it
            lang: find articles that are written in the specified language.
                If more than one language is specified, resulting articles has to be written in *any* of the languages.
            keywords: limit the event articles to those that mention the specified keywords.
                A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
                or QueryItems.OR() to specify a list of keywords where any of the keywords have to appear
            conceptUri: limit the event articles to those where the concept with concept uri is mentioned.
                A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
                To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
            categoryUri: limit the event articles to those that are assigned into a particular category.
                A single category can be provided as a string, while multiple categories can be provided as a list in QueryItems.AND() or QueryItems.OR().
                A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
            sourceUri: limit the event articles to those that were written by a news source sourceUri.
                If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
                Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
            sourceLocationUri: limit the event articles to those that were written by news sources located in the given geographic location.
                If multiple source locations are provided, then put them into a list inside QueryItems.OR()
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            sourceGroupUri: limit the event articles to those that were written by news sources that are assigned to the specified source group.
                If multiple source groups are provided, then put them into a list inside QueryItems.OR()
                Source group uri for a given name can be obtained using EventRegistry.getSourceGroupUri().
            authorUri: find articles that were written by a specific author.
                If multiple authors should be considered use QueryItems.OR() to provide the list of authors.
                Author uri for a given author name can be obtained using EventRegistry.getAuthorUri().
            locationUri: find articles that describe something that occurred at a particular location.
                If value can be a string or a list of strings provided in QueryItems.OR().
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            dateStart: find articles that were written on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateEnd: find articles that occurred before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateMentionStart: limit the event articles to those that explicitly mention a date that is equal or greater than dateMentionStart.
            dateMentionEnd: limit the event articles to those that explicitly mention a date that is lower or equal to dateMentionEnd.
            keywordsLoc: where should we look when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
            keywordSearchMode: what search mode to use when specifying keywords. Possible values are: simple, exact, phrase
            startSourceRankPercentile: starting percentile of the sources to consider in the results (default: 0). Value should be in range 0-90 and divisible by 10.
            endSourceRankPercentile: ending percentile of the sources to consider in the results (default: 100). Value should be in range 10-100 and divisible by 10.
            minSentiment: minimum value of the sentiment, that the returned articles should have. Range [-1, 1]. Note: setting the value will remove all articles that don't have
                a computed value for the sentiment (all articles that are not reported in English language)
            maxSentiment: maximum value of the sentiment, that the returned articles should have. Range [-1, 1]. Note: setting the value will remove all articles that don't have
                a computed value for the sentiment (all articles that are not reported in English language)
        """
        super().__init__(eventUri)
        self._setQueryArrVal(keywords, "keyword", "keywordOper", "and")
        self._setQueryArrVal(conceptUri, "conceptUri", "conceptOper", "and")
        self._setQueryArrVal(categoryUri, "categoryUri", "categoryOper", "or")
        self._setQueryArrVal(sourceUri, "sourceUri", "sourceOper", "or")
        self._setQueryArrVal(sourceLocationUri, "sourceLocationUri", None, "or")
        self._setQueryArrVal(sourceGroupUri, "sourceGroupUri", "sourceGroupOper", "or")
        self._setQueryArrVal(authorUri, "authorUri", "authorOper", "or")
        self._setQueryArrVal(locationUri, "locationUri", None, "or")        # location such as "http://en.wikipedia.org/wiki/Ljubljana"

        self._setQueryArrVal(lang, "articlesLang", None, "or")                      # a single lang or list

        # starting date of the published articles (e.g. 2014-05-02)
        if dateStart is not None:
            self._setDateVal("dateStart", dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if dateEnd is not None:
            self._setDateVal("dateEnd", dateEnd)

        # first valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionStart is not None:
            self._setDateVal("dateMentionStart", dateMentionStart)
        # last valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionEnd is not None:
            self._setDateVal("dateMentionEnd", dateMentionEnd)

        self._setValIfNotDefault("keywordLoc", keywordsLoc, "body")
        self._setValIfNotDefault("keywordSearchMode", keywordSearchMode, "phrase")

        if not (startSourceRankPercentile >= 0 and startSourceRankPercentile % 10 == 0 and startSourceRankPercentile <= 100):
            raise ValueError("startSourceRankPercentile should be a multiple of 10 between 0 and 100")
        if not (endSourceRankPercentile >= 0 and endSourceRankPercentile % 10 == 0 and endSourceRankPercentile <= 100):
            raise ValueError("endSourceRankPercentile should be a multiple of 10 between 0 and 100")
        if not (startSourceRankPercentile < endSourceRankPercentile):
            raise ValueError("startSourceRankPercentile should be smaller than endSourceRankPercentile")
        if startSourceRankPercentile != 0:
            self._setVal("startSourceRankPercentile", startSourceRankPercentile)
        if endSourceRankPercentile != 100:
            self._setVal("endSourceRankPercentile", endSourceRankPercentile)
        if minSentiment != -1:
            if not (minSentiment >= -1 and minSentiment <= 1):
                raise ValueError("minSentiment should be a value between -1 and 1")
            self._setVal("minSentiment", minSentiment)      # e.g. -0.5
        if maxSentiment != 1:
            if not (maxSentiment >= -1 and maxSentiment <= 1):
                raise ValueError("maxSentiment should be a value between -1 and 1")
            self._setVal("maxSentiment", maxSentiment)      # e.g. 0.5


    def count(self, eventRegistry: EventRegistry):
        """
        return the number of articles that match the criteria

        Args:
            eventRegistry: instance of EventRegistry class. used to obtain the necessary data
        """
        # use a copy of the query so that calling count() does not change the requested results of the query.
        # the conditions are already in the query parameters, so the request only asks for the articles
        res = eventRegistry.execQuery(self._copyWithRequest(RequestEventArticles()))
        if "error" in res:
            raise QueryError(str(res["error"]), statusCode = 200, responseText = str(res["error"]))
        return res.get(self.queryParams["eventUri"], {}).get("articles", {}).get("totalResults", 0)


    def execQuery(self, eventRegistry: EventRegistry,
            sortBy: str = "cosSim", sortByAsc: bool = False,
            returnInfo: Union[ReturnInfo, None] = None,
            maxItems: int = -1) -> QueryResultsIter:
        """
        Args:
            eventRegistry: instance of EventRegistry class. used to obtain the necessary data
            sortBy: order in which event articles are sorted. Options: none (no specific sorting), date (published date), cosSim (closeness to event centroid), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out

        Returns:
            iterator over the articles of the event that match the conditions. Each call returns a new, independent iterator and the query itself is not changed
        """
        eventUri = self.queryParams["eventUri"]
        # the conditions (keywords, concepts, ...) are already in the query parameters. They must not be passed again
        # to RequestEventArticles, since it would encode them again and replace their operators with the default ones
        return self._setResultsIter(QueryResultsIter(eventRegistry, self,
            createRequest = lambda page: RequestEventArticles(page = page, sortBy = sortBy, sortByAsc = sortByAsc, returnInfo = returnInfo),
            getResults = lambda res: res.get(eventUri, {}).get("articles", {}),
            maxItems = maxItems))



class RequestEvent:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestEventInfo(RequestEvent):
    def __init__(self, returnInfo: Union[ReturnInfo, None] = None):
        """
        return details about an event
        """
        self.resultType = "info"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("info"))



class RequestEventArticles(RequestEvent, QueryParamsBase):
    def __init__(self,
                page = 1,
                count = 100,

                lang: Union[str, QueryItems, None] = None,
                keywords: Union[str, QueryItems, None] = None,
                conceptUri: Union[str, QueryItems, None] = None,
                categoryUri: Union[str, QueryItems, None] = None,
                sourceUri: Union[str, QueryItems, None] = None,
                sourceLocationUri: Union[str, QueryItems, None] = None,
                sourceGroupUri: Union[str, QueryItems, None] = None,
                authorUri: Union[str, QueryItems, None] = None,
                locationUri: Union[str, QueryItems, None] = None,
                dateStart: Union[datetime.datetime, datetime.date, str, None] = None,
                dateEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                dateMentionStart: Union[datetime.datetime, datetime.date, str, None] = None,
                dateMentionEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                keywordsLoc: str = "body",
                keywordSearchMode: Literal["simple", "exact", "phrase"] = "phrase",

                startSourceRankPercentile: int = 0,
                endSourceRankPercentile: int = 100,

                sortBy: str = "cosSim", sortByAsc: bool = False,
                returnInfo: Union[ReturnInfo, None] = None):
        """
        return articles about the event

        Args:
            page: page of the articles to return (1, 2, ...)
            count: number of articles to return per page (at most 100)
            keywords: limit the event articles to those that mention the specified keywords.
                A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
                or QueryItems.OR() to specify a list of keywords where any of the keywords have to appear
            conceptUri: limit the event articles to those where the concept with concept uri is mentioned.
                A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
                To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
            categoryUri: limit the event articles to those that are assigned into a particular category.
                A single category can be provided as a string, while multiple categories can be provided as a list in QueryItems.AND() or QueryItems.OR().
                A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
            sourceUri: limit the event articles to those that were written by a news source sourceUri.
                If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
                Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
            sourceLocationUri: limit the event articles to those that were written by news sources located in the given geographic location.
                If multiple source locations are provided, then put them into a list inside QueryItems.OR()
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            sourceGroupUri: limit the event articles to those that were written by news sources that are assigned to the specified source group.
                If multiple source groups are provided, then put them into a list inside QueryItems.OR()
                Source group uri for a given name can be obtained using EventRegistry.getSourceGroupUri().
            authorUri: find articles that were written by a specific author.
                If multiple authors should be considered use QueryItems.OR() to provide the list of authors.
                Author uri for a given author name can be obtained using EventRegistry.getAuthorUri().
            locationUri: find articles that describe something that occurred at a particular location.
                If value can be a string or a list of strings provided in QueryItems.OR().
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            lang: find articles that are written in the specified language.
                If more than one language is specified, resulting articles has to be written in *any* of the languages.
            dateStart: find articles that were written on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateEnd: find articles that occurred before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateMentionStart: limit the event articles to those that explicitly mention a date that is equal or greater than dateMentionStart.
            dateMentionEnd: limit the event articles to those that explicitly mention a date that is lower or equal to dateMentionEnd.
            keywordsLoc: where should we look when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
            keywordSearchMode: what search mode to use when specifying keywords. Possible values are: simple, exact, phrase
            startSourceRankPercentile: starting percentile of the sources to consider in the results (default: 0). Value should be in range 0-100 and divisible by 10.
            endSourceRankPercentile: ending percentile of the sources to consider in the results (default: 100). Value should be in range 0-100 and divisible by 10.
            sortBy: order in which event articles are sorted. Options: date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
            returnInfo: what details should be included in the returned information. Use None to get the default information.
        """
        RequestEvent.__init__(self)
        QueryParamsBase.__init__(self)
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100):
            raise ValueError("at most 100 articles can be returned per call")
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count

        self._setQueryArrVal(keywords, "keyword", "keywordOper", "and")
        self._setQueryArrVal(conceptUri, "conceptUri", "conceptOper", "and")
        self._setQueryArrVal(categoryUri, "categoryUri", "categoryOper", "or")
        self._setQueryArrVal(sourceUri, "sourceUri", "sourceOper", "or")
        self._setQueryArrVal(sourceLocationUri, "sourceLocationUri", None, "or")
        self._setQueryArrVal(sourceGroupUri, "sourceGroupUri", "sourceGroupOper", "or")
        self._setQueryArrVal(authorUri, "authorUri", "authorOper", "or")
        self._setQueryArrVal(locationUri, "locationUri", None, "or")        # location such as "http://en.wikipedia.org/wiki/Ljubljana"

        self._setQueryArrVal(lang, "lang", None, "or")                      # a single lang or list (possible: eng, deu, spa, zho, slv)

        # starting date of the published articles (e.g. 2014-05-02)
        if dateStart is not None:
            self._setDateVal("dateStart", dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if dateEnd is not None:
            self._setDateVal("dateEnd", dateEnd)

        # first valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionStart is not None:
            self._setDateVal("dateMentionStart", dateMentionStart)
        # last valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionEnd is not None:
            self._setDateVal("dateMentionEnd", dateMentionEnd)

        self._setValIfNotDefault("keywordLoc", keywordsLoc, "body")
        self._setValIfNotDefault("keywordSearchMode", keywordSearchMode, "phrase")

        if not (startSourceRankPercentile >= 0 and startSourceRankPercentile % 10 == 0 and startSourceRankPercentile <= 100):
            raise ValueError("startSourceRankPercentile should be a multiple of 10 between 0 and 100")
        if not (endSourceRankPercentile >= 0 and endSourceRankPercentile % 10 == 0 and endSourceRankPercentile <= 100):
            raise ValueError("endSourceRankPercentile should be a multiple of 10 between 0 and 100")
        if not (startSourceRankPercentile < endSourceRankPercentile):
            raise ValueError("startSourceRankPercentile should be smaller than endSourceRankPercentile")
        if startSourceRankPercentile != 0:
            self._setVal("startSourceRankPercentile", startSourceRankPercentile)
        if endSourceRankPercentile != 100:
            self._setVal("endSourceRankPercentile", endSourceRankPercentile)

        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        # the filtering params are stored in queryParams. update the params on the self and delete the queryParams object
        self.__dict__.update(self.queryParams)
        if returnInfo:
            self.__dict__.update(returnInfo.getParams("articles"))
        del self.queryParams



class RequestEventArticleUriWgts(RequestEvent):
    def __init__(self,
                 lang: Union[str, List[str], None] = None,
                 sortBy: str = "cosSim", sortByAsc: bool = False,
                 **kwds):
        """
        return just a list of article uris and their associated weights

        Args:
            lang: a single language or a list of languages in which to return the articles. Set None to return all articles
            sortBy: order in which event articles are sorted. Options: date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
            kwds: any other potential query parameters - can be any of the parameters used in RequestEventArticles() constructor
        """
        if lang is not None:
            self.articlesLang = lang
        self.uriWgtListSortBy = sortBy
        self.uriWgtListSortByAsc = sortByAsc
        self.resultType = "uriWgtList"
        self.__dict__.update(**kwds)



class RequestEventKeywordAggr(RequestEvent):
    def __init__(self, lang: Union[str, List[str], None] = None,
                **kwds):
        """
        return keyword aggregate (tag-cloud) from articles in the event

        Args:
            lang: if not `None` then the top keywords will only be computed from the articles in the specified language.
                The value should match one of the languages for which we have articles in the event.
            kwds: any other potential query parameters - can be any of the parameters used in RequestEventArticles() constructor
        """
        self.resultType = "keywordAggr"
        self.articlesLang = lang
        self.__dict__.update(**kwds)



class RequestEventSourceAggr(RequestEvent):
    def __init__(self):
        """
        get news source distribution of articles in the event
        """
        self.resultType = "sourceExAggr"



class RequestEventDateMentionAggr(RequestEvent):
    def __init__(self):
        """
        get dates that we found mentioned in the event articles and their frequencies
        """
        self.resultType = "dateMentionAggr"



class RequestEventArticleTrend(RequestEvent):
    def __init__(self,
                 lang: Union[str, None] = None,
                 page: int = 1, count: int = 100,
                 minArticleCosSim: int = -1,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return trending information for the articles about the event

        Args:
            lang: languages for which to compute the trends. If None, then compute trends for all articles
            page: page of the articles for which to return information (1, 2, ...)
            count: number of articles returned per page (at most 100)
            minArticleCosSim: ignore articles that have cos similarity to centroid lower than the specified value (-1 for no limit)
            returnInfo: what details should be included in the returned information
        """
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100):
            raise ValueError("at most 100 articles can be returned per call")
        self.resultType = "articleTrend"
        self.articlesLang = lang
        self.articleTrendPage = page
        self.articleTrendCount = count
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))).getParams("articleTrend"))



class RequestEventSimilarEvents(RequestEvent):
    def __init__(self,
                conceptInfoList: List[dict],
                count: int = 50,                    # number of similar events to return
                dateStart: Union[datetime.datetime, datetime.date, str, None] = None,              # what can be the oldest date of the similar events
                dateEnd: Union[datetime.datetime, datetime.date, str, None] = None,                # what can be the newest date of the similar events
                addArticleTrendInfo: bool = False,   # add info how the articles in the similar events are distributed over time
                aggrHours: int = 6,                 # if similarEventsAddArticleTrendInfo == True then this is the aggregating window
                returnInfo: Union[ReturnInfo, None] = None):
        """
        compute and return a list of similar events

        Args:
            conceptInfoList: array of concepts and their importance, e.g. [{ "uri": "http://en.wikipedia.org/wiki/Barack_Obama", "wgt": 100 }, ...]
            count: number of similar events to return (at most 50)
            dateStart: what can be the oldest date of the similar events
            dateEnd: what can be the newest date of the similar events
            addArticleTrendInfo: for the returned events compute how they were trending (intensity of reporting) in different time periods
            aggrHours: time span that is used as a unit when computing the trending info
            returnInfo: what details should be included in the returned information
        """
        if not (count <= 50):
            raise ValueError("count should be at most 50")
        if not (isinstance(conceptInfoList, list)):
            raise TypeError("conceptInfoList should be of type list")
        self.action = "getSimilarEvents"
        self.concepts = json.dumps(conceptInfoList)
        self.eventsCount = count
        if dateStart is not None:
            self.dateStart = QueryParamsBase.encodeDate(dateStart)
        if dateEnd is not None:
            self.dateEnd = QueryParamsBase.encodeDate(dateEnd)
        self.similarEventsAddArticleTrendInfo = addArticleTrendInfo
        self.similarEventsAggrHours = aggrHours
        # setting resultType since we have to, but it's actually ignored on the backend
        self.resultType = "similarEvents"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams(""))
