import json
import datetime
from eventregistry.Query import ComplexMentionQuery
from eventregistry.Base import IterableQuery, Query, QueryItems, QueryParamsBase, QueryResultsIter
from eventregistry.Exceptions import QueryError
from eventregistry.ReturnInfo import ReturnInfo
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List

# the names exported by "from eventregistry import *"
__all__ = ["QueryMentions", "QueryMentionsIter", "RequestMentions", "RequestMentionsInfo", "RequestMentionsUriWgtList",
           "RequestMentionsTimeAggr", "RequestMentionsConceptAggr", "RequestMentionsCategoryAggr",
           "RequestMentionsSourceAggr", "RequestMentionsKeywordAggr", "RequestMentionsEventTypeAggr",
           "RequestMentionsRecentActivity"]


class QueryMentions(Query):
    def __init__(self,
                eventTypeUri: Union[str, QueryItems, None] = None,
                keywords: Union[str, QueryItems, None] = None,
                conceptUri: Union[str, QueryItems, None] = None,
                categoryUri: Union[str, QueryItems, None] = None,
                sourceUri: Union[str, QueryItems, None] = None,
                sourceLocationUri: Union[str, QueryItems, None] = None,
                sourceGroupUri: Union[str, QueryItems, None] = None,
                industryUri: Union[str, QueryItems, None] = None,
                sdgUri: Union[str, QueryItems, None] = None,
                sasbUri: Union[str, QueryItems, None] = None,
                esgUri: Union[str, QueryItems, None] = None,
                locationUri: Union[str, QueryItems, None] = None,
                lang: Union[str, QueryItems, None] = None,
                dateStart: Union[datetime.datetime, datetime.date, str, None] = None,
                dateEnd: Union[datetime.datetime, datetime.date, str, None] = None,

                ignoreEventTypeUri: Union[str, QueryItems, None] = None,
                ignoreKeywords: Union[str, QueryItems, None] = None,
                ignoreConceptUri: Union[str, QueryItems, None] = None,
                ignoreCategoryUri: Union[str, QueryItems, None] = None,
                ignoreSourceUri: Union[str, QueryItems, None] = None,
                ignoreSourceLocationUri: Union[str, QueryItems, None] = None,
                ignoreSourceGroupUri: Union[str, QueryItems, None] = None,
                ignoreIndustryUri: Union[str, QueryItems, None] = None,
                ignoreSdgUri: Union[str, QueryItems, None] = None,
                ignoreSasbUri: Union[str, QueryItems, None] = None,
                ignoreEsgUri: Union[str, QueryItems, None] = None,
                ignoreLocationUri: Union[str, QueryItems, None] = None,
                ignoreLang: Union[str, QueryItems, None] = None,

                showDuplicates: bool = False,
                startSourceRankPercentile: int = 0,
                endSourceRankPercentile: int = 100,
                minSentiment: float = -1,
                maxSentiment: float = 1,
                minSentenceIndex: Union[int, None] = None,
                maxSentenceIndex: Union[int, None] = None,
                requestedResult: Union["RequestMentions", None] = None):
        """
        Query class for searching for individual mentions in the Event Registry.
        The resulting mentions (objects, containing sentence, article information, mentioned entities, etc.) have to match all specified conditions.
        If a parameter value equals "" or [], then it is ignored.
        In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

        Args:
            eventTypeUri: find mentions that express a certain type of a relation.
                A single event type can be provided as a string, multiple event types can be provided as a list of strings.
                Since each mention can only have one event type, if multiple event types are provided, an *or* condition is used between them.
            keywords: find mentions that mention the specified keywords.
                A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
                or QueryItems.OR() to specify a list of keywords where any of the keywords have to appear
            conceptUri: find mentions where the concept with concept uri is mentioned.
                A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
                To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
            categoryUri: find mentions that are assigned into a particular category.
                A single category can be provided as a string, while multiple categories can be provided as a list in QueryItems.AND() or QueryItems.OR().
                A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
            sourceUri: find mentions that were written by a news source sourceUri.
                If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
                Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
            sourceLocationUri: find mentions that were written by news sources located in the given geographic location.
                If multiple source locations are provided, then put them into a list inside QueryItems.OR().
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            sourceGroupUri: find mentions that were written by news sources that are assigned to the specified source group.
                If multiple source groups are provided, then put them into a list inside QueryItems.OR().
                Source group uri for a given name can be obtained using EventRegistry.getSourceGroupUri().
            industryUri: find mentions that relate to companies in a certain industry.
                A single industry can be provided as a string, while multiple industries can be provided as a list in QueryItems.AND() or QueryItems.OR().
                Industry uri for a given industry name can be obtained using EventRegistry.suggestIndustries().
            sdgUri: find mentions that are about event types that are associated with a particular SDG.
                If multiple SDGs are provided, then put them into a list inside QueryItems.OR().
                SDG uri for a given SDG can be obtained using EventRegistry.getSdgUris().
            sasbUri: find mentions that are about event types that are associated with a particular SASB category.
                If multiple SASB categories are provided, then put them into a list inside QueryItems.OR().
                SASB uri for a given SASB category can be obtained using EventRegistry.getSasbUris().
            esgUri: find mentions that are about event types that are associated with a particular ESG category.
                If multiple ESGs are provided, then put them into a list inside QueryItems.OR().
                Possible values are "esg/environment", "esg/social", "esg/governance".
            locationUri: find mentions that describe something that occurred at a particular location.
                If value can be a string or a list of strings provided in QueryItems.OR().
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            lang: find mentions that are written in the specified language.
                If more than one language is specified, resulting mentions has to be written in *any* of the languages.
            dateStart: find mentions that were written on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateEnd: find mentions that occurred before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
            dateMentionStart: find mentions that explicitly mention a date that is equal or greater than dateMentionStart.
            dateMentionEnd: find mentions that explicitly mention a date that is lower or equal to dateMentionEnd.
            keywordsLoc: where should we look when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
            ignoreEventTypeUri: ignore mentions that belong to certain event types
            ignoreKeywords: ignore mentions that mention all provided keywords
            ignoreConceptUri: ignore mentions that mention all provided concepts
            ignoreCategoryUri: ignore mentions that are assigned to a particular category
            ignoreSourceUri: ignore mentions that have been written by *any* of the specified news sources
            ignoreSourceLocationUri: ignore mentions that have been written by sources located at *any* of the specified locations
            ignoreSourceGroupUri: ignore mentions that have been written by sources in *any* of the specified source groups
            ignoreIndustryUri: ignore mentions that refer to companies in any of the provided industries
            ignoreSdgUri: ignore mentions that are about event types that are associated with a particular SDG.
            ignoreSasbUri: ignore mentions that are about event types that are associated with a particular SASB category.
            ignoreEsgUri: ignore mentions that are about event types that are associated with a particular ESG.
            ignoreLocationUri: ignore mentions that occurred in any of the provided locations. A location can be a city or a place
            ignoreLang: ignore mentions that are written in *any* of the provided languages
            showDuplicates: should we show return duplicate mentions? (default: False)
            startSourceRankPercentile: starting percentile of the sources to consider in the results (default: 0). Value should be in range 0-90 and divisible by 10.
            endSourceRankPercentile: ending percentile of the sources to consider in the results (default: 100). Value should be in range 10-100 and divisible by 10.
            minSentiment: minimum value of the sentiment, that the returned mentions should have. Range [-1, 1]. Note: setting the value will remove all mentions that don't have
                a computed value for the sentiment (all non-English mentions)
            maxSentiment: maximum value of the sentiment, that the returned mentions should have. Range [-1, 1]. Note: setting the value will remove all mentions that don't have
                a computed value for the sentiment (all non-English mentions)
            minSentenceIndex: what should be the minimum index of the sentence in the article in order to be included in the results.
            maxSentenceIndex: what should be the maximum index of the sentence in the article in order to be included in the results.
            showDuplicates: include duplicate mentions in the results. By default, duplicates are removed.
            requestedResult: the information to return as the result of the query. By default return the list of matching mentions
        """
        super().__init__()
        self._setVal("action", "getMentions")

        self._setQueryArrVal(eventTypeUri, "eventTypeUri", None, "or")
        self._setQueryArrVal(keywords, "keyword", "keywordOper", "and")
        self._setQueryArrVal(conceptUri, "conceptUri", "conceptOper", "and")
        self._setQueryArrVal(categoryUri, "categoryUri", "categoryOper", "or")
        self._setQueryArrVal(sourceUri, "sourceUri", "sourceOper", "or")
        self._setQueryArrVal(sourceLocationUri, "sourceLocationUri", None, "or")
        self._setQueryArrVal(sourceGroupUri, "sourceGroupUri", "sourceGroupOper", "or")
        self._setQueryArrVal(industryUri, "industryUri", "industryOper", "or")
        self._setQueryArrVal(sdgUri, "sdgUri", None, "or")
        self._setQueryArrVal(sasbUri, "sasbUri", None, "or")
        self._setQueryArrVal(esgUri, "esgUri", None, "or")
        self._setQueryArrVal(locationUri, "locationUri", None, "or")        # location such as "http://en.wikipedia.org/wiki/Ljubljana"

        self._setQueryArrVal(lang, "lang", None, "or")                      # a single lang or list (possible: eng, deu, spa, zho, slv)

        # starting date of the published articles (e.g. 2014-05-02)
        if dateStart is not None:
            self._setDateVal("dateStart", dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if dateEnd is not None:
            self._setDateVal("dateEnd", dateEnd)


        # for the negative conditions, only the OR is a valid operator type
        self._setQueryArrVal(ignoreEventTypeUri, "ignoreEventTypeUri", None, "or")
        self._setQueryArrVal(ignoreKeywords, "ignoreKeyword", None, "or")
        self._setQueryArrVal(ignoreConceptUri, "ignoreConceptUri", None, "or")
        self._setQueryArrVal(ignoreCategoryUri, "ignoreCategoryUri", None, "or")
        self._setQueryArrVal(ignoreSourceUri, "ignoreSourceUri", None, "or")
        self._setQueryArrVal(ignoreSourceLocationUri, "ignoreSourceLocationUri", None, "or")
        self._setQueryArrVal(ignoreSourceGroupUri, "ignoreSourceGroupUri", None, "or")
        self._setQueryArrVal(ignoreIndustryUri, "ignoreIndustryUri", None, "or")
        self._setQueryArrVal(ignoreSdgUri, "ignoreSdgUri", None, "or")
        self._setQueryArrVal(ignoreSasbUri, "ignoreSasbUri", None, "or")
        self._setQueryArrVal(ignoreEsgUri, "ignoreEsgUri", None, "or")
        self._setQueryArrVal(ignoreLocationUri, "ignoreLocationUri", None, "or")

        self._setQueryArrVal(ignoreLang, "ignoreLang", None, "or")

        self._setValIfNotDefault("showDuplicates", showDuplicates, False)
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
            self._setVal("minSentiment", minSentiment)
        if maxSentiment != 1:
            if not (maxSentiment >= -1 and maxSentiment <= 1):
                raise ValueError("maxSentiment should be a value between -1 and 1")
            self._setVal("maxSentiment", maxSentiment)
        if minSentenceIndex is not None:
            if not (minSentenceIndex >= 0):
                raise ValueError("minSentenceIndex should be at least 0")
            self._setVal("minSentenceIndex", minSentenceIndex)
        if maxSentenceIndex is not None:
            if not (maxSentenceIndex >= 0):
                raise ValueError("maxSentenceIndex should be at least 0")
            self._setVal("maxSentenceIndex", maxSentenceIndex)

        # set the information that should be returned
        self.setRequestedResult(requestedResult or RequestMentionsInfo())


    def _getPath(self):
        return "/api/v1/eventType/mention"


    def setRequestedResult(self, requestMentions: "RequestMentions"):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestMentions base class (see classes below).
        """
        if not (isinstance(requestMentions, RequestMentions)):
            raise TypeError("QueryMentions class can only accept result requests that are of type RequestMentions")
        self.resultTypeList = [requestMentions]


    @staticmethod
    def initWithMentionUriList(uriList):
        """
        instead of making a query, provide a list of mention URIs manually, and then produce the desired results on top of them
        """
        q = QueryMentions()
        if not (isinstance(uriList, str) or isinstance(uriList, list)):
            raise TypeError("uriList has to be a list of strings or a string that represent mention uris")
        q.queryParams = { "action": "getMentions", "mentionUri": uriList }
        return q


    @staticmethod
    def initWithMentionUriWgtList(uriWgtList: Union[str, List[str]]):
        """
        instead of making a query, provide a list of mention URIs manually, and then produce the desired results on top of them
        """
        q = QueryMentions()
        if isinstance(uriWgtList, list):
            q.queryParams = { "action": "getMentions", "mentionUriWgtList": ",".join(uriWgtList) }
        elif isinstance(uriWgtList, str):
            q.queryParams = { "action": "getMentions", "mentionUriWgtList": uriWgtList }
        else:
            raise TypeError("uriWgtList parameter did not contain a list or a string")
        return q


    @staticmethod
    def initWithComplexQuery(query: Union[ComplexMentionQuery, str, dict]):
        """
        create a query using a complex mention query

        Args:
            query: complex query as ComplexMentionQuery instance, string or a python dict
        """
        q = QueryMentions()
        # provided an instance of ComplexMentionQuery
        if isinstance(query, ComplexMentionQuery):
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
            raise TypeError("The instance of query parameter was not a ComplexMentionQuery, a string or a python dict")
        return q



class QueryMentionsIter(IterableQuery, QueryMentions):
    """
    class that simplifies and combines functionality from QueryMentions and RequestMentionsInfo. It provides an iterator
    over the list of mentions that match the specified conditions
    """
    def count(self, eventRegistry: EventRegistry):
        """
        return the number of mentions that match the criteria
        """
        # use a copy of the query so that calling count() does not change the requested results of the query
        res = eventRegistry.execQuery(self._copyWithRequest(RequestMentionsInfo()))
        if "error" in res:
            raise QueryError(str(res["error"]), statusCode = 200, responseText = str(res["error"]))
        return res.get("mentions", {}).get("totalResults", 0)


    def execQuery(self, eventRegistry: EventRegistry,
                  sortBy: str = "rel",
                  sortByAsc: bool = False,
                  returnInfo: Union[ReturnInfo, None] = None,
                  maxItems: int = -1) -> QueryResultsIter:
        """
        Args:
            eventRegistry: instance of EventRegistry class. used to query new mention list and uris
            sortBy: how are mentions sorted. Options: date (publishing date), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out

        Returns:
            iterator over the mentions that match the query. Each call returns a new, independent iterator and the query itself is not changed
        """
        batchSize = 100    # always download 100 - best for the user since it uses his token and we want to download as much as possible in a single search
        return self._setResultsIter(QueryResultsIter(eventRegistry, self,
            createRequest = lambda page: RequestMentionsInfo(page = page, count = batchSize, sortBy = sortBy, sortByAsc = sortByAsc, returnInfo = returnInfo),
            getResults = lambda res: res.get("mentions", {}),
            maxItems = maxItems))


    @staticmethod
    def initWithComplexQuery(query: Union[ComplexMentionQuery, str, dict]):
        """
        Args:
            query: complex query as ComplexMentionQuery instance, string or a python dict
        """
        q = QueryMentionsIter()

        # provided an instance of ComplexMentionQuery
        if isinstance(query, ComplexMentionQuery):
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
            raise TypeError("The instance of query parameter was not a ComplexMentionQuery, a string or a python dict")
        return q


    @staticmethod
    def initWithMentionUriList(uriList: Union[str, List[str]]):
        """
        instead of making a query, provide a list of Mention URIs manually, and then produce the desired results on top of them
        """
        q = QueryMentionsIter()
        if not (isinstance(uriList, (list, str))):
            raise TypeError("uriList has to be a list of strings that represent mention uris")
        q.queryParams = { "action": "getMentions", "mentionUri": uriList }
        return q



class RequestMentions:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestMentionsInfo(RequestMentions):
    def __init__(self,
                 page: int = 1,
                 count: int = 100,
                 sortBy: str = "date", sortByAsc: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return mention details for resulting mentions

        Args:
            page: page of the mentions to return
            count: number of mentions to return for the given page (at most 100)
            sortBy: how are mentions sorted. Options: date (publishing date), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100):
            raise ValueError("at most 100 mentions can be returned per call")
        self.resultType = "mentions"
        self.mentionsPage = page
        self.mentionsCount = count
        self.mentionsSortBy = sortBy
        self.mentionsSortByAsc = sortByAsc
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("mentions"))


    def setPage(self, page):
        """
        set the page of results to obtain
        """
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.mentionsPage = page



class RequestMentionsUriWgtList(RequestMentions):
    def __init__(self,
                 page: int = 1,
                 count: int = 10000,
                 sortBy: str = "fq", sortByAsc: bool = False):
        """
        return a list of mention uris together with the scores

        Args:
            page: page of the results (1, 2, ...)
            count: number of items to return in a single query (at most 50000)
            sortBy: how are mentions sorted. Options: date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 50000):
            raise ValueError("count should be at most 50000")
        self.resultType = "uriWgtList"
        self.uriWgtListPage = page
        self.uriWgtListCount = count
        self.uriWgtListSortBy = sortBy
        self.uriWgtListSortByAsc = sortByAsc


    def setPage(self, page):
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.uriWgtListPage = page



class RequestMentionsTimeAggr(RequestMentions):
    def __init__(self):
        """
        return time distribution of resulting mentions
        """
        super().__init__()
        self.resultType = "timeAggr"



class RequestMentionsConceptAggr(RequestMentions):
    def __init__(self,
                 conceptCount: int = 25,
                 conceptCountPerType: Union[int, None] = None,
                 conceptScoring: str = "importance",
                 mentionsSampleSize: int = 10000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get aggreate of concepts of resulting mentions

        Args:
            conceptCount: number of top concepts to return (at most 500)
            conceptCountPerType: if you wish to limit the number of top concepts per type (person, org, loc, wiki) then set this to some number.
                If you want to get equal number of concepts for each type then set conceptCountPerType to conceptCount/4 (since there are 4 concept types)
            conceptScoring: how should the top concepts be computed. Possible values are
                "importance" (takes into account how frequently a concept is mentioned and how relevant it is in an mention),
                "frequency" (ranks the concepts simply by how frequently the concept is mentioned in the results) and
                "uniqueness" (computes what are the top concepts that are frequently mentioned in the results of your search query but less frequently mentioned in the news in general)
            mentionsSampleSize: on what sample of results should the aggregate be computed (at most 20000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 500):
            raise ValueError("conceptCount should be at most 500")
        if not (mentionsSampleSize <= 20000):
            raise ValueError("mentionsSampleSize should be at most 20000")
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = mentionsSampleSize
        self.conceptAggrScoring = conceptScoring
        if conceptCountPerType is not None:
            self.conceptAggrConceptCountPerType = conceptCountPerType
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptAggr"))



class RequestMentionsCategoryAggr(RequestMentions):
    def __init__(self,
                 mentionsSampleSize: int = 20000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return aggreate of categories of resulting mentions

        Args:
            mentionsSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details about the categories should be included in the returned information
        """
        super().__init__()
        if not (mentionsSampleSize <= 50000):
            raise ValueError("mentionsSampleSize should be at most 50000")
        self.resultType = "categoryAggr"
        self.categoryAggrSampleSize = mentionsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("categoryAggr"))



class RequestMentionsSourceAggr(RequestMentions):
    def __init__(self,
                 sourceCount: int = 50,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get aggreate of news sources of resulting mentions

        Args:
            sourceCount: the number of top sources to return
            returnInfo: what details about the sources should be included in the returned information
        """
        super().__init__()
        self.resultType = "sourceAggr"
        self.sourceAggrSourceCount = sourceCount
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("sourceAggr"))


class RequestMentionsKeywordAggr(RequestMentions):
    def __init__(self,
                 mentionsSampleSize: int = 2000):
        """
        get top keywords in the resulting mentions

        Args:
            mentionsSampleSize: on what sample of results should the aggregate be computed (at most 20000)
        """
        super().__init__()
        if not (mentionsSampleSize <= 20000):
            raise ValueError("mentionsSampleSize should be at most 20000")
        self.resultType = "keywordAggr"
        self.keywordAggrSampleSize = mentionsSampleSize



class RequestMentionsEventTypeAggr(RequestMentions):
    def __init__(self,
                 mentionsSampleSize: int = 100000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return the event types of the resulting mentions, with the number of mentions of each event type

        Args:
            mentionsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
            returnInfo: what details about the event types should be included in the returned information
        """
        super().__init__()
        if not (mentionsSampleSize <= 300000):
            raise ValueError("mentionsSampleSize should be at most 300000")
        self.resultType = "eventTypeAggr"
        self.eventTypeAggrSampleSize = mentionsSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("eventTypeAggr"))



class RequestMentionsRecentActivity(RequestMentions):
    def __init__(self,
                 maxMentionCount: int = 100,
                 updatesAfterUri: Union[str, None] = None,
                 updatesAfterTm: Union[datetime.datetime, str, None] = None,
                 updatesAfterMinsAgo: Union[int, None] = None,
                 updatesUntilTm: Union[datetime.datetime, str, None] = None,
                 updatesUntilMinsAgo: Union[int, None] = None,
                 mandatorySourceLocation: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the list of mentions that were recently added to the Event Registry and match the selected criteria

        Args:
            maxMentionCount: the maximum number of mentions to return in the call (the number can be even higher than 100 but in case more mentions
                are returned, the call will also use more tokens)
            updatesAfterTm: the time after which the mentions were added (returned by previous call to the same method)
            updatesAfterMinsAgo: how many minutes into the past should we check (set either this or updatesAfterTm property, but not both)
            updatesUntilTm: what is the latest time when the mentions were added (in case you don't want the most recent mentions)
            updatesUntilMinsAgo: how many minutes ago was the latest time when the mentions were added
            mandatorySourceLocation: return only mentions for which we know the source's geographic location
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (maxMentionCount <= 2000):
            raise ValueError("maxMentionCount should be at most 2000")
        if not (updatesAfterTm is None or updatesAfterMinsAgo is None):
            raise ValueError("You should specify either updatesAfterTm or updatesAfterMinsAgo parameter, but not both")
        if not (updatesUntilTm is None or updatesUntilMinsAgo is None):
            raise ValueError("You should specify either updatesUntilTm or updatesUntilMinsAgo parameter, but not both")
        self.resultType = "recentActivityMentions"
        self.recentActivityMentionsMaxMentionCount = maxMentionCount
        if updatesAfterTm is not None:
            self.recentActivityMentionsUpdatesAfterTm = QueryParamsBase.encodeDateTime(updatesAfterTm)
        if updatesAfterMinsAgo is not None:
            self.recentActivityMentionsUpdatesAfterMinsAgo = updatesAfterMinsAgo
        if updatesUntilTm is not None:
            self.recentActivityMentionsUpdatesUntilTm = QueryParamsBase.encodeDateTime(updatesUntilTm)
        if updatesUntilMinsAgo is not None:
            self.recentActivityMentionsUpdatesUntilMinsAgo = updatesUntilMinsAgo

        # set the stopping uris, if provided
        if updatesAfterUri is not None:
            self.recentActivityMentionsUpdatesAfterUri = updatesAfterUri

        self.recentActivityMentionsMandatorySourceLocation = mandatorySourceLocation
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("recentActivityMentions"))