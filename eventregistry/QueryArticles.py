import json
import datetime
from eventregistry.Base import QueryItems, QueryParamsBase, Query, QueryResultsIter, IterableQuery
from eventregistry.Exceptions import QueryError
from eventregistry.ReturnInfo import ReturnInfo
from eventregistry.Query import ComplexArticleQuery
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List, Literal

# the names exported by "from eventregistry import *"
__all__ = ["QueryArticles", "QueryArticlesIter", "RequestArticles", "RequestArticlesInfo", "RequestArticlesUriWgtList",
           "RequestArticlesTimeAggr", "RequestArticlesConceptAggr", "RequestArticlesCategoryAggr",
           "RequestArticlesSourceAggr", "RequestArticlesKeywordAggr", "RequestArticlesConceptGraph",
           "RequestArticlesConceptMatrix", "RequestArticlesConceptTrends", "RequestArticlesDateMentionAggr",
           "RequestArticlesLangAggr", "RequestArticlesSentimentAggr", "RequestArticlesAuthorAggr", "RequestArticlesLocAggr", "RequestArticlesSourceExAggr",
           "RequestArticlesRecentActivity"]


class QueryArticles(Query):
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

                isDuplicateFilter: str = "keepAll",
                hasDuplicateFilter: str = "keepAll",
                eventFilter: str = "keepAll",
                authorsFilter: str = "keepAll",
                videosFilter: str = "keepAll",
                linksFilter: str = "keepAll",
                startSourceRankPercentile: int = 0,
                endSourceRankPercentile: int = 100,
                minSentiment: float = -1,
                maxSentiment: float = 1,
                dataType: Union[str, List[str]] = "news",
                requestedResult: Union["RequestArticles", None] = None):
        """
        Query class for searching for individual articles in the Event Registry.
        The resulting articles have to match all specified conditions. If a parameter value equals "" or [], then it is ignored.
        In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

        Args:
            keywords: find articles that mention the specified keywords.
                A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
                or QueryItems.OR() to specify a list of keywords where any of the keywords have to appear
            conceptUri: find articles where the concept with concept uri is mentioned.
                A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
                Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
                To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
            categoryUri: find articles that are assigned into a particular category.
                A single category can be provided as a string, while multiple categories can be provided as a list in QueryItems.AND() or QueryItems.OR().
                A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
            sourceUri: find articles that were written by a news source sourceUri.
                If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
                Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
            sourceLocationUri: find articles that were written by news sources located in the given geographic location.
                If multiple source locations are provided, then put them into a list inside QueryItems.OR()
                Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
            sourceGroupUri: find articles that were written by news sources that are assigned to the specified source group.
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
            dateMentionStart: find articles that explicitly mention a date that is equal or greater than dateMentionStart.
            dateMentionEnd: find articles that explicitly mention a date that is lower or equal to dateMentionEnd.
            keywordsLoc: where should we look when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
            keywordSearchMode: what search mode to use when specifying keywords. Possible values are: simple, exact, phrase
            ignoreKeywords: ignore articles that mention all provided keywords
            ignoreConceptUri: ignore articles that mention all provided concepts
            ignoreCategoryUri: ignore articles that are assigned to a particular category
            ignoreSourceUri: ignore articles that have been written by *any* of the specified news sources
            ignoreSourceLocationUri: ignore articles that have been written by sources located at *any* of the specified locations
            ignoreSourceGroupUri: ignore articles that have been written by sources in *any* of the specified source groups
            ignoreAuthorUri: ignore articles that were written by *any* of the specified authors
            ignoreLocationUri: ignore articles that occurred in any of the provided locations. A location can be a city or a place
            ignoreLang: ignore articles that are written in *any* of the provided languages
            ignoreKeywordsLoc: where should we look when data should be used when searching using the keywords provided by "ignoreKeywords" parameter. "body" (default), "title", or "body,title"
            ignoreKeywordSearchMode: what search mode to use when specifying ignoreKeywords. Possible values are: simple, exact, phrase
            isDuplicateFilter: some articles can be duplicates of other articles. What should be done with them. Possible values are:
                "skipDuplicates" (skip the resulting articles that are duplicates of other articles)
                "keepOnlyDuplicates" (return only the duplicate articles)
                "keepAll" (no filtering, default)
            hasDuplicateFilter: some articles are later copied by others. What should be done with such articles. Possible values are:
                "skipHasDuplicates" (skip the resulting articles that have been later copied by others)
                "keepOnlyHasDuplicates" (return only the articles that have been later copied by others)
                "keepAll" (no filtering, default)
            eventFilter: some articles describe a known event and some don't. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipArticlesWithoutEvent" (skip articles that are not describing any known event in ER)
                "keepOnlyArticlesWithoutEvent" (return only the articles that are not describing any known event in ER)
                "keepAll" (no filtering, default)
            authorsFilter: for some articles we are able to extract who their author is and for some we cannot. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipIfHasAuthors" (skip articles for which we have identified who their author is)
                "keepOnlyIfHasAuthors" (return only the articles for which we have extracted their author)
                "keepAll" (no filtering, default)
            videosFilter: some articles contain a link to a video and some don't. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipIfHasVideos" (skip articles that don't contain any link to a video)
                "keepOnlyIfHasVideos" (return only the articles that contain a link to a video)
                "keepAll" (no filtering, default)
            linksFilter: some articles contain some links to other urls (potentially other articles) and some don't. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipIfHasLinks" (skip articles that contain one or more links to other urls)
                "keepOnlyIfHasLinks" (return only the articles that contain a link to other urls)
                "keepAll" (no filtering, default)
            startSourceRankPercentile: starting percentile of the sources to consider in the results (default: 0). Value should be in range 0-90 and divisible by 10.
            endSourceRankPercentile: ending percentile of the sources to consider in the results (default: 100). Value should be in range 10-100 and divisible by 10.
            minSentiment: minimum value of the sentiment, that the returned articles should have. Range [-1, 1]. Note: setting the value will remove all articles that don't have
                a computed value for the sentiment (all non-English articles)
            maxSentiment: maximum value of the sentiment, that the returned articles should have. Range [-1, 1]. Note: setting the value will remove all articles that don't have
                a computed value for the sentiment (all non-English articles)
            dataType: what data types should we search? "news" (news content, default), "pr" (press releases), or "blog".
                If you want to use multiple data types, put them in an array (e.g. ["news", "pr"])
            requestedResult: the information to return as the result of the query. By default return the list of matching articles
        """
        super().__init__()
        self._setVal("action", "getArticles")

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


        self._setValIfNotDefault("isDuplicateFilter", isDuplicateFilter, "keepAll")
        self._setValIfNotDefault("hasDuplicateFilter", hasDuplicateFilter, "keepAll")
        self._setValIfNotDefault("eventFilter", eventFilter, "keepAll")
        self._setValIfNotDefault("hasAuthorsFilter", authorsFilter, "keepAll")
        self._setValIfNotDefault("hasLinksFilter", linksFilter, "keepAll")
        self._setValIfNotDefault("hasVideosFilter", videosFilter, "keepAll")
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
        # if the user provided a custom value, then set the data type. Otherwise don't set it since the user could provide a complex query with data type values and we would
        self._setValIfNotDefault("dataType", dataType, "news")

        # set the information that should be returned
        self.setRequestedResult(requestedResult or RequestArticlesInfo())


    def _getPath(self):
        return "/api/v1/article"


    def setRequestedResult(self, requestArticles: "RequestArticles"):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestArticles base class (see classes below).
        """
        if not (isinstance(requestArticles, RequestArticles)):
            raise TypeError("QueryArticles class can only accept result requests that are of type RequestArticles")
        self.resultTypeList = [requestArticles]


    @staticmethod
    def initWithArticleUriList(uriList: Union[str, List[str]], returnInfo: Union[ReturnInfo, None] = None):
        """
        instead of making a query, provide a list of article URIs manually, and then produce the desired results on top of them
        """
        # we need to set the dataType parameter here, otherwise users cannot ask for blog or pr articles using this way
        q = QueryArticles(requestedResult=RequestArticlesInfo(returnInfo = returnInfo))
        if not (isinstance(uriList, str) or isinstance(uriList, list)):
            raise TypeError("uriList has to be a list of strings or a string that represent article uris")
        q.queryParams = { "action": "getArticles", "articleUri": uriList, "dataType": ["news", "blog", "pr"] }
        return q


    @staticmethod
    def initWithArticleUriWgtList(uriWgtList: Union[str, List[str]], returnInfo: Union[ReturnInfo, None] = None):
        """
        instead of making a query, provide a list of article URIs manually, and then produce the desired results on top of them
        """
        # we need to set the dataType parameter here, otherwise users cannot ask for blog or pr articles using this way
        q = QueryArticles(requestedResult=RequestArticlesInfo(returnInfo=returnInfo))
        if isinstance(uriWgtList, list):
            uriWgtList = ",".join(uriWgtList)
        if not (isinstance(uriWgtList, str)):
            raise TypeError("uriWgtList parameter did not contain a list or a string")
        q.queryParams = { "action": "getArticles", "articleUriWgtList": uriWgtList, "dataType": ["news", "blog", "pr"] }
        return q


    @staticmethod
    def initWithComplexQuery(query: Union[ComplexArticleQuery, str, dict]):
        """
        create a query using a complex article query
        """
        q = QueryArticles()
        # provided an instance of ComplexArticleQuery
        if isinstance(query, ComplexArticleQuery):
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
            raise TypeError("The instance of query parameter was not a ComplexArticleQuery, a string or a python dict")
        return q



class QueryArticlesIter(IterableQuery, QueryArticles):
    """
    class that simplifies and combines functionality from QueryArticles and RequestArticlesInfo. It provides an iterator
    over the list of articles that match the specified conditions
    """
    def count(self, eventRegistry: EventRegistry):
        """
        return the number of articles that match the criteria
        """
        # use a copy of the query so that calling count() does not change the requested results of the query
        res = eventRegistry.execQuery(self._copyWithRequest(RequestArticlesInfo()))
        if "error" in res:
            raise QueryError(str(res["error"]), statusCode = 200, responseText = str(res["error"]))
        return res.get("articles", {}).get("totalResults", 0)


    def execQuery(self, eventRegistry: EventRegistry,
                  sortBy: str = "rel",
                  sortByAsc: bool = False,
                  returnInfo: Union[ReturnInfo, None] = None,
                  maxItems: int = -1) -> QueryResultsIter:
        """
        Args:
            eventRegistry: instance of EventRegistry class. used to query new article list and uris
            sortBy: how are articles sorted. Options: date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out

        Returns:
            iterator over the articles that match the query. Each call returns a new, independent iterator and the query itself is not changed
        """
        batchSize = 100    # always download 100 - best for the user since it uses his token and we want to download as much as possible in a single search
        return self._setResultsIter(QueryResultsIter(eventRegistry, self,
            createRequest = lambda page: RequestArticlesInfo(page = page, count = batchSize, sortBy = sortBy, sortByAsc = sortByAsc, returnInfo = returnInfo),
            getResults = lambda res: res.get("articles", {}),
            maxItems = maxItems))


    @staticmethod
    def initWithComplexQuery(query: Union[ComplexArticleQuery, str, dict]):
        """
        Args:
            query: complex query as ComplexArticleQuery instance, string or a python dict
        """
        q = QueryArticlesIter()

        # provided an instance of ComplexArticleQuery
        if isinstance(query, ComplexArticleQuery):
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
            raise TypeError("The instance of query parameter was not a ComplexArticleQuery, a string or a python dict")
        return q


    @staticmethod
    def initWithArticleUriList(uriList: Union[str, List[str]]):  # type: ignore[override]  # the returnInfo is given to execQuery()
        """
        instead of making a query, provide a list of article URIs manually, and then iterate over these articles.
        What details about the articles to return is specified with the returnInfo parameter of execQuery()
        """
        # we need to set the dataType parameter here, otherwise users cannot ask for blog or pr articles using this way
        q = QueryArticlesIter()
        if not (isinstance(uriList, (list, str))):
            raise TypeError("uriList parameter did not contain a list or a string")
        q.queryParams = { "action": "getArticles", "articleUri": uriList, "dataType": ["news", "blog", "pr"] }
        return q



class RequestArticles:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestArticlesInfo(RequestArticles):
    def __init__(self,
                 page: int = 1,
                 count: int = 100,
                 sortBy: str = "date", sortByAsc: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return article details for resulting articles

        Args:
            page: page of the articles to return
            count: number of articles to return for the given page (at most 100)
            sortBy: how are articles sorted. Options: date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100):
            raise ValueError("at most 100 articles can be returned per call")
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("articles"))


    def setPage(self, page: int):
        """
        set the page of results to obtain
        """
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.articlesPage = page



class RequestArticlesUriWgtList(RequestArticles):
    def __init__(self,
                 page: int = 1,
                 count: int = 10000,
                 sortBy: str = "fq", sortByAsc: bool = False):
        """
        return a list of article uris together with the scores

        Args:
            page: page of the results (1, 2, ...)
            count: number of items to return in a single query (at most 50000)
            sortBy: how are articles sorted. Options: date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
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


    def setPage(self, page: int):
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        self.uriWgtListPage = page



class RequestArticlesTimeAggr(RequestArticles):
    def __init__(self):
        """
        return time distribution of resulting articles
        """
        super().__init__()
        self.resultType = "timeAggr"



class RequestArticlesConceptAggr(RequestArticles):
    def __init__(self,
                 conceptCount: int = 25,
                 conceptCountPerType: Union[int, None] = None,
                 conceptScoring: str = "importance",
                 articlesSampleSize: int = 10000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get aggreate of concepts of resulting articles

        Args:
            conceptCount: number of top concepts to return (at most 500)
            conceptCountPerType: if you wish to limit the number of top concepts per type (person, org, loc, wiki) then set this to some number.
                If you want to get equal number of concepts for each type then set conceptCountPerType to conceptCount/4 (since there are 4 concept types)
            conceptScoring: how should the top concepts be computed. Possible values are
                "importance" (takes into account how frequently a concept is mentioned and how relevant it is in an article),
                "frequency" (ranks the concepts simply by how frequently the concept is mentioned in the results) and
                "uniqueness" (computes what are the top concepts that are frequently mentioned in the results of your search query but less frequently mentioned in the news in general)
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 20000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 500):
            raise ValueError("conceptCount should be at most 500")
        if not (articlesSampleSize <= 20000):
            raise ValueError("articlesSampleSize should be at most 20000")
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize
        self.conceptAggrScoring = conceptScoring
        if conceptCountPerType is not None:
            self.conceptAggrConceptCountPerType = conceptCountPerType
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptAggr"))



class RequestArticlesCategoryAggr(RequestArticles):
    def __init__(self,
                 articlesSampleSize: int = 20000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return aggreate of categories of resulting articles

        Args:
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details about the categories should be included in the returned information
        """
        super().__init__()
        if not (articlesSampleSize <= 50000):
            raise ValueError("articlesSampleSize should be at most 50000")
        self.resultType = "categoryAggr"
        self.categoryAggrSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("categoryAggr"))



class RequestArticlesSourceAggr(RequestArticles):
    def __init__(self,
                 sourceCount: int = 50,
                 normalizeBySourceArts: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get aggreate of news sources of resulting articles

        Args:
            sourceCount: the number of top sources to return
            normalizeBySourceArts: some sources generate significantly more content than others which is why
                they can appear as top souce for a given query. If you want to normalize and sort the sources by the total number of
                articles that they have published set this to True. This will return as top sources those that potentially publish less
                content overall, but their published content is more about the searched query.
            returnInfo: what details about the sources should be included in the returned information
        """
        super().__init__()
        self.resultType = "sourceAggr"
        self.sourceAggrSourceCount = sourceCount
        self.sourceAggrNormalizeBySourceArts = normalizeBySourceArts
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("sourceAggr"))


class RequestArticlesKeywordAggr(RequestArticles):
    def __init__(self,
                 articlesSampleSize: int = 2000):
        """
        get top keywords in the resulting articles

        Args:
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 20000)
        """
        super().__init__()
        if not (articlesSampleSize <= 20000):
            raise ValueError("articlesSampleSize should be at most 20000")
        self.resultType = "keywordAggr"
        self.keywordAggrSampleSize = articlesSampleSize



class RequestArticlesConceptGraph(RequestArticles):
    def __init__(self,
                 conceptCount: int = 25,
                 linkCount: int = 50,
                 articlesSampleSize: int = 10000,
                 skipQueryConcepts: bool = True,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get concept graph of resulting articles. Identify concepts that frequently co-occur with other concepts

        Args:
            conceptCount: how many concepts should be returned (at most 1000)
            linkCount: how many top links between the concepts should be returned (at most 2000)
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details about the concepts should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 1000):
            raise ValueError("conceptCount should be at most 1000")
        if not (linkCount <= 2000):
            raise ValueError("linkCount should be at most 2000")
        if not (articlesSampleSize <= 50000):
            raise ValueError("articlesSampleSize should be at most 50000")
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = articlesSampleSize
        self.conceptGraphSkipQueryConcepts = skipQueryConcepts
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptGraph"))



class RequestArticlesConceptMatrix(RequestArticles):
    def __init__(self,
                 conceptCount: int = 25,
                 measure: str = "pmi",
                 articlesSampleSize: int = 10000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get aggreate of concept co-occurences of resulting articles

        Args:
            conceptCount: how many concepts should be returned (at most 200)
            measure: how should the interestingness between the selected pairs of concepts be computed. Options: pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 200):
            raise ValueError("conceptCount should be at most 200")
        if not (articlesSampleSize <= 50000):
            raise ValueError("articlesSampleSize should be at most 50000")
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptMatrix"))



class RequestArticlesConceptTrends(RequestArticles):
    def __init__(self,
                 conceptUris: Union[str, List[str], None] = None,
                 conceptCount: int = 25,
                 articlesSampleSize: int = 10000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get trending of concepts in the resulting articles

        Args:
            conceptUris: list of concept URIs for which to return trending information. If None, then top concepts will be automatically computed
            conceptCount: if the concepts are not provided, what should be the number of automatically determined concepts to return (at most 50)
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (conceptCount <= 50):
            raise ValueError("conceptCount should be at most 50")
        if not (articlesSampleSize <= 50000):
            raise ValueError("articlesSampleSize should be at most 50000")
        self.resultType = "conceptTrends"
        if conceptUris is not None:
            self.conceptTrendsConceptUri = conceptUris
        self.conceptTrendsConceptCount = conceptCount
        self.conceptTrendsSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("conceptTrends"))



class RequestArticlesDateMentionAggr(RequestArticles):
    """
    get mentioned dates in the articles
    """
    def __init__(self):
        super().__init__()
        self.resultType = "dateMentionAggr"



class RequestArticlesLangAggr(RequestArticles):
    def __init__(self):
        """
        return the number of resulting articles in each language
        """
        super().__init__()
        self.resultType = "langAggr"



class RequestArticlesSentimentAggr(RequestArticles):
    def __init__(self):
        """
        return the distribution of the sentiment of the resulting articles (sentiment is computed only for the articles in English)
        """
        super().__init__()
        self.resultType = "sentimentAggr"



class RequestArticlesAuthorAggr(RequestArticles):
    def __init__(self,
                 authorCount: int = 50,
                 includePeople: bool = True,
                 includeAgencies: bool = True,
                 articlesSampleSize: int = 500000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the authors that wrote the most of the resulting articles

        Args:
            authorCount: the number of top authors to return
            includePeople: should the authors that are people be included
            includeAgencies: should the authors that are news agencies be included
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 1000000)
            returnInfo: what details about the authors should be included in the returned information
        """
        super().__init__()
        if not (articlesSampleSize <= 1000000):
            raise ValueError("articlesSampleSize should be at most 1000000")
        self.resultType = "authorAggr"
        self.authorAggrAuthorCount = authorCount
        self.authorAggrIncludePeople = includePeople
        self.authorAggrIncludeAgencies = includeAgencies
        self.authorAggrSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("authorAggr"))



class RequestArticlesLocAggr(RequestArticles):
    def __init__(self,
                 articlesSampleSize: int = 500000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the locations where the events described in the resulting articles happened, with the number of articles for each

        Args:
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 1000000)
            returnInfo: what details about the locations should be included in the returned information
        """
        super().__init__()
        if not (articlesSampleSize <= 1000000):
            raise ValueError("articlesSampleSize should be at most 1000000")
        self.resultType = "locAggr"
        self.locAggrSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("locAggr"))



class RequestArticlesSourceExAggr(RequestArticles):
    def __init__(self,
                 sourceCount: int = 50,
                 timeWindow: Literal["total", "month", "day", "hour"] = "day",
                 articlesSampleSize: int = 20000,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the top news sources of the resulting articles, together with the number of their articles over time

        Args:
            sourceCount: the number of top sources to return
            timeWindow: the size of the time interval for which the article counts of each source are computed: total, month, day or hour
            articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
            returnInfo: what details about the sources should be included in the returned information
        """
        super().__init__()
        if not (articlesSampleSize <= 50000):
            raise ValueError("articlesSampleSize should be at most 50000")
        self.resultType = "sourceExAggr"
        self.sourceExAggrSourceCount = sourceCount
        self.sourceExAggrTimeWindow = timeWindow
        self.sourceExAggrSampleSize = articlesSampleSize
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("sourceExAggr"))



class RequestArticlesRecentActivity(RequestArticles):
    def __init__(self,
                 maxArticleCount: int = 100,
                 updatesAfterNewsUri: Union[str, None] = None,
                 updatesafterBlogUri: Union[str, None] = None,
                 updatesAfterPrUri: Union[str, None] = None,
                 updatesAfterTm: Union[datetime.datetime, str, None] = None,
                 updatesAfterMinsAgo: Union[int, None] = None,
                 updatesUntilTm: Union[datetime.datetime, str, None] = None,
                 updatesUntilMinsAgo: Union[int, None] = None,
                 mandatorySourceLocation: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        get the list of articles that were recently added to the Event Registry and match the selected criteria

        Args:
            maxArticleCount: the maximum number of articles to return in the call (the number can be even higher than 100 but in case more articles
                are returned, the call will also use more tokens)
            updatesAfterTm: the time after which the articles were added (returned by previous call to the same method)
            updatesAfterMinsAgo: how many minutes into the past should we check (set either this or updatesAfterTm property, but not both)
            updatesUntilTm: what is the latest time when the articles were added (in case you don't want the most recent articles)
            updatesUntilMinsAgo: how many minutes ago was the latest time when the articles were added
            mandatorySourceLocation: return only articles for which we know the source's geographic location
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (maxArticleCount <= 2000):
            raise ValueError("maxArticleCount should be at most 2000")
        if not (updatesAfterTm is None or updatesAfterMinsAgo is None):
            raise ValueError("You should specify either updatesAfterTm or updatesAfterMinsAgo parameter, but not both")
        if not (updatesUntilTm is None or updatesUntilMinsAgo is None):
            raise ValueError("You should specify either updatesUntilTm or updatesUntilMinsAgo parameter, but not both")
        self.resultType = "recentActivityArticles"
        self.recentActivityArticlesMaxArticleCount = maxArticleCount
        if updatesAfterTm is not None:
            self.recentActivityArticlesUpdatesAfterTm = QueryParamsBase.encodeDateTime(updatesAfterTm)
        if updatesAfterMinsAgo is not None:
            self.recentActivityArticlesUpdatesAfterMinsAgo = updatesAfterMinsAgo
        if updatesUntilTm is not None:
            self.recentActivityArticlesUpdatesUntilTm = QueryParamsBase.encodeDateTime(updatesUntilTm)
        if updatesUntilMinsAgo is not None:
            self.recentActivityArticlesUpdatesUntilMinsAgo = updatesUntilMinsAgo

        # set the stopping uris, if provided
        if updatesAfterNewsUri is not None:
            self.recentActivityArticlesNewsUpdatesAfterUri = updatesAfterNewsUri
        if updatesafterBlogUri is not None:
            self.recentActivityArticlesBlogUpdatesAfterUri = updatesafterBlogUri
        if updatesAfterPrUri is not None:
            self.recentActivityArticlesPrUpdatesAfterUri = updatesAfterPrUri

        self.recentActivityArticlesMandatorySourceLocation = mandatorySourceLocation
        if returnInfo is not None:
            self.__dict__.update(returnInfo.getParams("recentActivityArticles"))
