import json
import datetime
from eventregistry.Base import IterableQuery, Query, QueryItems, QueryParamsBase, QueryResultsIter
from eventregistry.Exceptions import QueryError
from eventregistry.ReturnInfo import ReturnInfo
from eventregistry.Query import ComplexEventQuery
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List, Literal

# the names exported by "from eventregistry import *"
__all__ = ["QueryEvents", "QueryEventsIter", "RequestEvents", "RequestEventsInfo", "RequestEventsUriWgtList",
           "RequestEventsTimeAggr", "RequestEventsKeywordAggr", "RequestEventsLocAggr", "RequestEventsLocTimeAggr",
           "RequestEventsConceptAggr", "RequestEventsConceptGraph", "RequestEventsConceptMatrix",
           "RequestEventsConceptTrends", "RequestEventsSourceAggr", "RequestEventsDateMentionAggr",
           "RequestEventsCategoryAggr", "RequestEventsSentimentAggr", "RequestEventsAuthorAggr",
           "RequestEventsRecentActivity", "RequestEventsBreakingEvents"]


class QueryEvents(Query):
    def __init__(self,
                 keywords: Union[str, QueryItems, None] = None,
                 conceptUri: Union[str, QueryItems, None] = None,
                 categoryUri: Union[str, QueryItems, None] = None,
                 sourceUri: Union[str, QueryItems, None] = None,
                 sourceLocationUri: Union[str, QueryItems, None] = None,
                 sourceGroupUri: Union[str, QueryItems, None] = None,
                 authorUri: Union[str, QueryItems, None] = None,
                 locationUri: Union[str, QueryItems, None] = None,
                 lang: Union[str, QueryItems, None] = None,
                 dateStart: Union[datetime.datetime, datetime.date, str, None] = None,
                 dateEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                 reportingDateStart: Union[datetime.datetime, datetime.date, str, None] = None,
                 reportingDateEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                 minSentiment: float = -1,
                 maxSentiment: float = 1,
                 minArticlesInEvent: Union[int, None] = None,
                 maxArticlesInEvent: Union[int, None] = None,
                 dateMentionStart: Union[datetime.datetime, datetime.date, str, None] = None,
                 dateMentionEnd: Union[datetime.datetime, datetime.date, str, None] = None,
                 keywordsLoc: str = "body",
                 keywordSearchMode: Literal["simple", "exact", "phrase"] = "phrase",

                 ignoreKeywords: Union[str, QueryItems, None] = None,
                 ignoreConceptUri: Union[str, QueryItems, None] = None,
                 ignoreCategoryUri: Union[str, QueryItems, None] = None,
                 ignoreSourceUri: Union[str, QueryItems, None] = None,
                 ignoreSourceLocationUri: Union[str, QueryItems, None] = None,
                 ignoreSourceGroupUri: Union[str, QueryItems, None] = None,
                 ignoreAuthorUri: Union[str, QueryItems, None] = None,
                 ignoreLocationUri: Union[str, QueryItems, None] = None,
                 ignoreLang: Union[str, QueryItems, None] = None,
                 ignoreKeywordsLoc: str = "body",
                 ignoreKeywordSearchMode: Literal["simple", "exact", "phrase"] = "phrase",

                 requestedResult: Union["RequestEvents", None] = None):
        """
        Query class for searching for events in the Event Registry.
        The resulting events have to match all specified conditions. If a parameter value equals "" or [], then it is ignored.
        In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

        Args:
            keywords: find events where articles mention all the specified keywords.
                A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
            conceptUri: find events where the concept with concept uri is important.
                A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
                To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
            categoryUri: find events that are assigned into a particular category.
                A single category uri can be provided as a string, multiple category uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided categories should be mentioned, or QueryItems.OR() if *any* of the categories should be mentioned.
                A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
            sourceUri: find events that contain one or more articles that have been written by a news source sourceUri.
                If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
                Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
            sourceLocationUri: find events that contain one or more articles that were written by news sources located in the given geographic location.
                If multiple source locations are provided, then put them into a list inside QueryItems.OR()
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            sourceGroupUri: find events that contain one or more articles that were written by news sources that are assigned to the specified source group.
                If multiple source groups are provided, then put them into a list inside QueryItems.OR()
                Source group uri for a given name can be obtained using EventRegistry.getSourceGroupUri().
            authorUri: find events that contain one or more articles that have been written by a specific author.
                If multiple authors should be considered use QueryItems.OR() or QueryItems.AND() to provide the list of authors.
                Author uri for a given author name can be obtained using EventRegistry.getAuthorUri().
            locationUri: find events that occurred at a particular location.
                If value can be a string or a list of strings provided in QueryItems.OR().
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            lang: find events for which we found articles in the specified language.
                If more than one language is specified, resulting events has to be reported in *any* of the languages.
            dateStart: find events that occurred on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateEnd: find events that occurred before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            reportingDateStart: find events where the average date of the articles about this event is on or after this date. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            reportingDateEnd: find events where the average date of the articles about this event is on or before this date. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            minSentiment: minimum value of the sentiment, that the returned events should have. Range [-1, 1]. Note: setting the value will remove all events that don't have
                a computed value for the sentiment (all events that are not reported in English language)
            maxSentiment: maximum value of the sentiment, that the returned events should have. Range [-1, 1]. Note: setting the value will remove all events that don't have
                a computed value for the sentiment (all events that are not reported in English language)
            minArticlesInEvent: find events that have been reported in at least minArticlesInEvent articles (regardless of language)
            maxArticlesInEvent: find events that have not been reported in more than maxArticlesInEvent articles (regardless of language)
            dateMentionStart: find events where articles explicitly mention a date that is equal or greater than dateMentionStart.
            dateMentionEnd: find events where articles explicitly mention a date that is lower or equal to dateMentionEnd.
            keywordsLoc: what data should be used when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
            keywordSearchMode: what search mode to use when specifying keywords. Possible values are: simple, exact, phrase
            ignoreKeywords: ignore events where articles about the event mention any of the provided keywords
            ignoreConceptUri: ignore events that are about any of the provided concepts
            ignoreCategoryUri: ignore events that are about any of the provided categories
            ignoreSourceUri: ignore events that have have articles which have been written by any of the specified news sources
            ignoreSourceLocationUri: ignore events that have articles which been written by sources located at *any* of the specified locations
            ignoreSourceGroupUri: ignore events that have articles which have been written by sources in *any* of the specified source groups
            ignoreAuthorUri: ignore articles that were written by *any* of the specified authors
            ignoreLocationUri: ignore events that occurred in any of the provided locations. A location can be a city or a place
            ignoreLang: ignore events that are reported in any of the provided languages
            ignoreKeywordsLoc: what data should be used when searching using the keywords provided by "ignoreKeywords" parameter. "body" (default), "title", or "body,title"
            ignoreKeywordSearchMode: what search mode to use when specifying ignoreKeywords. Possible values are: simple, exact, phrase
            requestedResult: the information to return as the result of the query. By default return the list of matching events
        """
        super().__init__()

        self._setVal("action", "getEvents")

        self._setQueryArrVal(keywords, "keyword", "keywordOper", "and")
        self._setQueryArrVal(conceptUri, "conceptUri", "conceptOper", "and")
        self._setQueryArrVal(categoryUri, "categoryUri", "categoryOper", "or")
        self._setQueryArrVal(sourceUri, "sourceUri", "sourceOper", "or")
        self._setQueryArrVal(sourceLocationUri, "sourceLocationUri", None, "or")
        self._setQueryArrVal(sourceGroupUri, "sourceGroupUri", "sourceGroupOper", "or")
        self._setQueryArrVal(authorUri, "authorUri", "authorOper", "or")
        self._setQueryArrVal(locationUri, "locationUri", None, "or")        # location such as "http://en.wikipedia.org/wiki/Ljubljana"

        self._setQueryArrVal(lang, "lang", None, "or")                      # a single lang or list (possible: eng, deu, spa, zho, slv)

        if dateStart is not None:
            self._setDateVal("dateStart", dateStart)        # e.g. 2014-05-02
        if dateEnd is not None:
            self._setDateVal("dateEnd", dateEnd)            # e.g. 2014-05-02
        if reportingDateStart is not None:
            self._setDateVal("reportingDateStart", reportingDateStart)        # e.g. 2014-05-02
        if reportingDateEnd is not None:
            self._setDateVal("reportingDateEnd", reportingDateEnd)            # e.g. 2014-05-02
        if minSentiment != -1:
            if not (minSentiment >= -1 and minSentiment <= 1):
                raise ValueError("minSentiment should be a value between -1 and 1")
            self._setVal("minSentiment", minSentiment)      # e.g. -0.5
        if maxSentiment != 1:
            if not (maxSentiment >= -1 and maxSentiment <= 1):
                raise ValueError("maxSentiment should be a value between -1 and 1")
            self._setVal("maxSentiment", maxSentiment)      # e.g. 0.5

        self._setValIfNotDefault("minArticlesInEvent", minArticlesInEvent, None)
        self._setValIfNotDefault("maxArticlesInEvent", maxArticlesInEvent, None)

        if dateMentionStart is not None:
            self._setDateVal("dateMentionStart", dateMentionStart)      # e.g. 2014-05-02
        if dateMentionEnd is not None:
            self._setDateVal("dateMentionEnd", dateMentionEnd)          # e.g. 2014-05-02

        self._setValIfNotDefault("keywordLoc", keywordsLoc, "body")
        self._setValIfNotDefault("keywordSearchMode", keywordSearchMode, "phrase")


        # for the negative conditions, only the OR is a valid operator type
        self._setQueryArrVal(ignoreKeywords, "ignoreKeyword", None, "or")
        self._setQueryArrVal(ignoreConceptUri, "ignoreConceptUri", None, "or")
        self._setQueryArrVal(ignoreCategoryUri, "ignoreCategoryUri", None, "or")
        self._setQueryArrVal(ignoreSourceUri, "ignoreSourceUri", None, "or")
        self._setQueryArrVal(ignoreSourceLocationUri, "ignoreSourceLocationUri", None, "or")
        self._setQueryArrVal(ignoreSourceGroupUri, "ignoreSourceGroupUri", None, "or")
        self._setQueryArrVal(ignoreAuthorUri, "ignoreAuthorUri", None, "or")
        self._setQueryArrVal(ignoreLocationUri, "ignoreLocationUri", None, "or")

        self._setQueryArrVal(ignoreLang, "ignoreLang", None, "or")

        self._setValIfNotDefault("ignoreKeywordLoc", ignoreKeywordsLoc, "body")
        self._setValIfNotDefault("ignoreKeywordSearchMode", ignoreKeywordSearchMode, "phrase")

        self.setRequestedResult(requestedResult or RequestEventsInfo())


    def _getPath(self):
        return "/api/v1/event"


    def setRequestedResult(self, requestEvents: "RequestEvents"):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestEvents base class (see classes below).
        """
        if not (isinstance(requestEvents, RequestEvents)):
            raise TypeError("QueryEvents class can only accept result requests that are of type RequestEvents")
        self.resultTypeList = [requestEvents]


    @staticmethod
    def initWithEventUriList(uriList):
        """
        Set a custom list of event uris. The results will be then computed on this list - no query will be done (all conditions will be ignored).
        """
        q = QueryEvents()
        if not (isinstance(uriList, (str, list))):
            raise TypeError("uriList has to be a list of strings or a string that represent event uris")
        if isinstance(uriList, list):
            uriList = ",".join(uriList)
        q.queryParams = { "action": "getEvents", "eventUriList": uriList }
        return q


    @staticmethod
    def initWithEventUriWgtList(uriWgtList):
        """
        Set a custom list of event uris. The results will be then computed on this list - no query will be done (all conditions will be ignored).
        """
        q = QueryEvents()
        if isinstance(uriWgtList, list):
            q.queryParams = { "action": "getEvents", "eventUriWgtList": ",".join(uriWgtList) }
        elif isinstance(uriWgtList, str):
            q.queryParams = { "action": "getEvents", "eventUriWgtList": uriWgtList }
        else:
            raise TypeError("uriWgtList parameter did not contain a list or a string")
        return q


    @staticmethod
    def initWithComplexQuery(query: Union[ComplexEventQuery, str, dict]):
        """
        create a query using a complex event query
        """
        q = QueryEvents()
        # provided an instance of ComplexEventQuery
        if isinstance(query, ComplexEventQuery):
            q._setVal("query", json.dumps(query.getQuery()))
        # provided query as a string containing the json object
        elif isinstance(query, str):
            try:
                json.loads(query)
            except ValueError:
                raise ValueError("Failed to parse the provided string content as a JSON object. Please check the content provided as a parameter to the initWithComplexQuery() method")
            q._setVal("query", query)
        # provided query as a python dict
        elif isinstance(query, dict):
            q._setVal("query", json.dumps(query))
        # unrecognized value provided
        else:
            raise TypeError("The instance of query parameter was not a ComplexEventQuery, a string or a python dict")
        return q



class QueryEventsIter(IterableQuery, QueryEvents):
    """
    class that simplifies and combines functionality from QueryEvents and RequestEventsInfo. It provides an iterator
    over the list of events that match the specified conditions
    """

    def count(self, eventRegistry: EventRegistry):
        """
        return the number of events that match the criteria
        """
        # use a copy of the query so that calling count() does not change the requested results of the query
        res = eventRegistry.execQuery(self._copyWithRequest(RequestEventsInfo()))
        if "error" in res:
            raise QueryError(str(res["error"]), statusCode = 200, responseText = str(res["error"]))
        return res.get("events", {}).get("totalResults", 0)


    def execQuery(self, eventRegistry: EventRegistry,
                  sortBy: str = "rel",
                  sortByAsc: bool = False,
                  returnInfo: Union[ReturnInfo, None] = None,
                  maxItems: int = -1) -> QueryResultsIter:
        """
        Args:
            eventRegistry: instance of EventRegistry class. used to query new event list and uris
            sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles),
                none (no specific sorting)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out

        Returns:
            iterator over the events that match the query. Each call returns a new, independent iterator and the query itself is not changed
        """
        batchSize = 50    # always download max - best for the user since it uses his token and we want to download as much as possible in a single search
        return self._setResultsIter(QueryResultsIter(eventRegistry, self,
            createRequest = lambda page: RequestEventsInfo(page = page, count = batchSize, sortBy = sortBy, sortByAsc = sortByAsc, returnInfo = returnInfo),
            getResults = lambda res: res.get("events", {}),
            maxItems = maxItems))


    @staticmethod
    def initWithComplexQuery(query):
        q = QueryEventsIter()
        # provided an instance of ComplexEventQuery
        if isinstance(query, ComplexEventQuery):
            q._setVal("query", json.dumps(query.getQuery()))
        # provided query as a string containing the json object
        elif isinstance(query, str):
            try:
                json.loads(query)
            except ValueError:
                raise ValueError("Failed to parse the provided string content as a JSON object. Please check the content provided as a parameter to the initWithComplexQuery() method")
            q._setVal("query", query)
        # provided query as a python dict
        elif isinstance(query, dict):
            q._setVal("query", json.dumps(query))
        else:
            raise TypeError("The instance of query parameter was not a ComplexEventQuery, a string or a python dict")
        return q



class RequestEvents:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestEventsInfo(RequestEvents):
    def __init__(self, page: int = 1,
                 count: int = 50,
                 sortBy: str = "rel", sortByAsc: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return event details for resulting events

        Args:
            page: page of the results to return (1, 2, ...)
            count: number of events to return per page (at most 50)
            sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles),
                none (no specific sorting)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 50):
            raise ValueError("at most 50 events can be returned per call")
        self.resultType = "events"
        self.eventsPage = page
        self.eventsCount = count
        self.eventsSortBy = sortBy
        self.eventsSortByAsc = sortByAsc
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("events"))


    def setPage(self, page: int):
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.eventsPage = page


    def setCount(self, count: int):
        self.eventsCount = count



class RequestEventsUriWgtList(RequestEvents):
    def __init__(self,
                 page: int = 1,
                 count: int = 50000,
                 sortBy: str = "rel", sortByAsc: bool = False):
        """
        return a simple list of event uris together with the scores for resulting events

        Args:
            page: page of the results (1, 2, ...)
            count: number of results to include per page (at most 100000)
            sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles),
                none (no specific sorting)
            sortByAsc: should the events be sorted in ascending order (True) or descending (False)
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100000):
            raise ValueError("count should be at most 100000")
        self.resultType = "uriWgtList"
        self.uriWgtListPage = page
        self.uriWgtListCount = count
        self.uriWgtListSortBy = sortBy
        self.uriWgtListSortByAsc = sortByAsc


    def setPage(self, page):
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.uriWgtListPage = page



class RequestEventsTimeAggr(RequestEvents):
    def __init__(self):
        """
        return time distribution of resulting events
        """
        super().__init__()
        self.resultType = "timeAggr"



class RequestEventsKeywordAggr(RequestEvents):
    def __init__(self, lang: Union[str, None] = None):
        """
        return keyword aggregate (tag cloud) on words in articles in resulting events

        Args:
            lang: in which language to produce the list of top keywords. If None, then compute on all articles
        """
        super().__init__()
        self.resultType = "keywordAggr"
        if lang is not None:
            self.keywordAggrLang = lang



class RequestEventsLocAggr(RequestEvents):
    def __init__(self,
                 eventsSampleSize: int = 100000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return aggreate of locations of resulting events

        Args:
            eventsSampleSize: sample of events to use to compute the location aggregate (at most 100000)
            returnInfo: what details (about locations) should be included in the returned information
        """
        super().__init__()
        if not (eventsSampleSize <= 100000):
            raise ValueError("eventsSampleSize should be at most 100000")
        self.resultType = "locAggr"
        self.locAggrSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("locAggr"))



class RequestEventsLocTimeAggr(RequestEvents):

    def __init__(self,
                 eventsSampleSize: int = 100000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return aggreate of locations and times of resulting events

        Args:
            eventsSampleSize: sample of events to use to compute the location aggregate (at most 100000)
            returnInfo: what details (about locations) should be included in the returned information
        """
        super().__init__()
        if not (eventsSampleSize <= 100000):
            raise ValueError("eventsSampleSize should be at most 100000")
        self.resultType = "locTimeAggr"
        self.locTimeAggrSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("locTimeAggr"))



class RequestEventsConceptAggr(RequestEvents):
    def __init__(self,
                 conceptCount: int = 20,
                 eventsSampleSize: int = 100000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        compute which concept are the most frequently occuring in the list of resulting events

        Args:
            conceptCount: number of top concepts to return (at most 200)
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 1000000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 200):
            raise ValueError("conceptCount should be at most 200")
        if not (eventsSampleSize <= 1000000):
            raise ValueError("eventsSampleSize should be at most 1000000")
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptAggr"))



class RequestEventsConceptGraph(RequestEvents):
    def __init__(self,
                 conceptCount: int = 50,
                 linkCount: int = 150,
                 eventsSampleSize: int = 50000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        compute which concept pairs frequently co-occur together in the resulting events

        Args:
            conceptCount: number of top concepts to return (at most 1,000)
            linkCount: number of links between the concepts to return (at most 2,000)
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 100000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 1000):
            raise ValueError("conceptCount should be at most 1000")
        if not (linkCount <= 2000):
            raise ValueError("linkCount should be at most 2000")
        if not (eventsSampleSize <= 300000):
            raise ValueError("eventsSampleSize should be at most 300000")
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptGraph"))



class RequestEventsConceptMatrix(RequestEvents):
    def __init__(self,
                 conceptCount: int = 25,
                 measure: str = "pmi",
                 eventsSampleSize: int = 100000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get a matrix of concepts and their dependencies. For individual concept pairs
        return how frequently they co-occur in the resulting events and
        how "surprising" this is, based on the frequency of individual concepts

        Args:
            conceptCount: number of top concepts to return (at most 200)
            measure: how should the interestingness between the selected pairs of concepts be computed. Options: pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 200):
            raise ValueError("conceptCount should be at most 200")
        if not (eventsSampleSize <= 300000):
            raise ValueError("eventsSampleSize should be at most 300000")
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptMatrix"))



class RequestEventsConceptTrends(RequestEvents):
    def __init__(self,
                 conceptUris: Union[str, List[str], None] = None,
                 conceptCount: int = 10,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return a list of top trending concepts and their daily trending info over time

        Args:
            conceptUris: list of concept URIs for which to return trending information. If None, then top concepts will be automatically computed
            count: if the concepts are not provided, what should be the number of automatically determined concepts to return (at most 50)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 50):
            raise ValueError("conceptCount should be at most 50")
        self.resultType = "conceptTrends"
        if conceptUris is not None:
            self.conceptTrendsConceptUri = conceptUris
        self.conceptTrendsConceptCount = conceptCount
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptTrends"))



class RequestEventsSourceAggr(RequestEvents):
    def __init__(self,
                 sourceCount: int = 30,
                 eventsSampleSize: int = 50000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return top news sources that report about the events that match the search conditions

        Args:
            sourceCount: number of top sources to return (at most 200)
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
            returnInfo: what details about the sources should be included in the returned information
        """
        super().__init__()
        if not (sourceCount <= 200):
            raise ValueError("sourceCount should be at most 200")
        if not (eventsSampleSize <= 100000):
            raise ValueError("eventsSampleSize should be at most 100000")
        self.resultType = "sourceAggr"
        self.sourceAggrSourceCount = sourceCount
        self.sourceAggrSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("sourceAggr"))



class RequestEventsDateMentionAggr(RequestEvents):
    def __init__(self,
                 minDaysApart: int = 0,
                 minDateMentionCount: int = 5,
                 eventsSampleSize: int = 100000):
        """
        return events and the dates that are mentioned in articles about these events

        Args:
            minDaysApart: ignore events that don't have a date that is more than this number of days apart from the tested event
            minDateMentionCount: report only dates that are mentioned at least this number of times
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
        """
        super().__init__()
        if not (eventsSampleSize <= 300000):
            raise ValueError("eventsSampleSize should be at most 300000")
        self.resultType = "dateMentionAggr"
        self.dateMentionAggrMinDaysApart = minDaysApart
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrSampleSize = eventsSampleSize



class RequestEventsCategoryAggr(RequestEvents):
    def __init__(self,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return distribution of events into dmoz categories

        Args:
            returnInfo: what details about the categories should be included in the returned information
        """
        super().__init__()
        self.resultType = "categoryAggr"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("categoryAggr"))



class RequestEventsSentimentAggr(RequestEvents):
    def __init__(self):
        """
        return the distribution of the sentiment of the resulting events
        """
        super().__init__()
        self.resultType = "sentimentAggr"



class RequestEventsAuthorAggr(RequestEvents):
    def __init__(self,
                 authorCount: int = 50,
                 includePeople: bool = True,
                 includeAgencies: bool = True,
                 eventsSampleSize: int = 50000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the authors that wrote the most articles about the resulting events

        Args:
            authorCount: the number of top authors to return
            includePeople: should the authors that are people be included
            includeAgencies: should the authors that are news agencies be included
            eventsSampleSize: on what sample of results should the aggregate be computed (at most 100000)
            returnInfo: what details about the authors should be included in the returned information
        """
        super().__init__()
        if not (eventsSampleSize <= 100000):
            raise ValueError("eventsSampleSize should be at most 100000")
        self.resultType = "authorAggr"
        self.authorAggrAuthorCount = authorCount
        self.authorAggrIncludePeople = includePeople
        self.authorAggrIncludeAgencies = includeAgencies
        self.authorAggrSampleSize = eventsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("authorAggr"))



class RequestEventsRecentActivity(RequestEvents):
    def __init__(self,
                 maxEventCount: int = 50,
                 updatesAfterTm: Union[datetime.datetime, str, None] = None,
                 updatesAfterMinsAgo: Union[int, None] = None,
                 mandatoryLocation: Union[bool, None] = True,
                 minAvgCosSim: float = 0,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return a list of recently changed events that match search conditions

        Args:
            maxEventCount: max events to return (at most 200)
            updatesAfterTm: the time after which the events were added/updated (returned by previous call to the same method)
            updatesAfterMinsAgo: how many minutes into the past should we check (set either this or updatesAfterTm property, but not both)
            mandatoryLocation: return only events that have a geographic location assigned to them
            minAvgCosSim: the minimum avg cos sim of the events to be returned (events with lower quality should not be included)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (maxEventCount <= 2000):
            raise ValueError("maxEventCount should be at most 2000")
        if not (updatesAfterTm is None or updatesAfterMinsAgo is None):
            raise ValueError("You should specify either updatesAfterTm or updatesAfterMinsAgo parameter, but not both")
        self.resultType = "recentActivityEvents"
        self.recentActivityEventsMaxEventCount = maxEventCount
        self.recentActivityEventsMandatoryLocation = mandatoryLocation
        if updatesAfterTm is not None:
            self.recentActivityEventsUpdatesAfterTm = QueryParamsBase.encodeDateTime(updatesAfterTm)
        if updatesAfterMinsAgo is not None:
            self.recentActivityEventsUpdatesAfterMinsAgo = updatesAfterMinsAgo
        self.recentActivityEventsMinAvgCosSim = minAvgCosSim
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("recentActivityEvents"))


class RequestEventsBreakingEvents(RequestEvents):
    def __init__(self,
                 page: int = 1,
                 count: int = 50,
                 minBreakingScore: float = 0.2,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return a list of events that are currently breaking

        Args:
            page: page of the results to return (starting from 1)
            count: max events to return (at most 50)
            minBreakingScore: the minimum score of "breakingness" of the events to be returned
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page should be at least 1")
        if not (count <= 50):
            raise ValueError("count should be at most 50")
        self.resultType = "breakingEvents"
        self.breakingEventsPage = page
        self.breakingEventsCount = count
        self.breakingEventsMinBreakingScore = minBreakingScore
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("breakingEvents"))


