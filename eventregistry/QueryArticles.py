import six, json
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.Query import *


class QueryArticles(Query):
    def __init__(self,
                 keywords = None,
                 conceptUri = None,
                 categoryUri = None,
                 sourceUri = None,
                 sourceLocationUri = None,
                 sourceGroupUri = None,
                 locationUri = None,
                 lang = None,
                 dateStart = None,
                 dateEnd = None,
                 dateMentionStart = None,
                 dateMentionEnd = None,
                 ignoreKeywords = None,
                 ignoreConceptUri = None,
                 ignoreCategoryUri = None,
                 ignoreSourceUri = None,
                 ignoreSourceLocationUri = None,
                 ignoreSourceGroupUri = None,
                 ignoreLocationUri = None,
                 ignoreLang = None,
                 keywordsLoc = "body",
                 ignoreKeywordsLoc = "body",
                 isDuplicateFilter = "keepAll",
                 hasDuplicateFilter = "keepAll",
                 eventFilter = "keepAll",
                 requestedResult = None):
        """
        Query class for searching for individual articles in the Event Registry.
        The resulting articles have to match all specified conditions. If a parameter value equals "" or [], then it is ignored.
        In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

        @param keywords: find articles that mention the specified keywords.
            A single keyword/phrase can be provided as a string, multiple keywords/phrases can be provided as a list of strings.
            Use QueryItems.AND() if *all* provided keywords/phrases should be mentioned, or QueryItems.OR() if *any* of the keywords/phrases should be mentioned.
            or QueryItems.OR() to specify a list of keywords where any of the keywords have to appear
        @param conceptUri: find articles where the concept with concept uri is mentioned.
            A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
            Use QueryItems.AND() if *all* provided concepts should be mentioned, or QueryItems.OR() if *any* of the concepts should be mentioned.
            To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
        @param categoryUri: find articles that are assigned into a particular category.
            A single category can be provided as a string, while multiple categories can be provided as a list in QueryItems.AND() or QueryItems.OR().
            A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
        @param sourceUri: find articles that were written by a news source sourceUri.
            If multiple sources should be considered use QueryItems.OR() to provide the list of sources.
            Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
        @param sourceLocationUri: find articles that were written by news sources located in the given geographic location.
            If multiple source locations are provided, then put them into a list inside QueryItems.OR()
            Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
        @param sourceGroupUri: find articles that were written by news sources that are assigned to the specified source group.
            If multiple source groups are provided, then put them into a list inside QueryItems.OR()
            Source group uri for a given name can be obtained using EventRegistry.getSourceGroupUri().
        @param locationUri: find articles that describe something that occured at a particular location.
            If value can be a string or a list of strings provided in QueryItems.OR().
            Location uri can either be a city or a country. Location uri for a given name can be obtained using EventRegistry.getLocationUri().
        @param lang: find articles that are written in the specified language.
            If more than one language is specified, resulting articles has to be written in *any* of the languages.
        @param dateStart: find articles that were written on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
        @param dateEnd: find articles that occured before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
        @param dateMentionStart: find articles that explicitly mention a date that is equal or greater than dateMentionStart.
        @param dateMentionEnd: find articles that explicitly mention a date that is lower or equal to dateMentionEnd.
        @param ignoreKeywords: ignore articles that mention all provided keywords
        @param ignoreConceptUri: ignore articles that mention all provided concepts
        @param ignoreCategoryUri: ignore articles that are assigned to a particular category
        @param ignoreSourceUri: ignore articles that have been written by *any* of the specified news sources
        @param ignoreSourceLocationUri: ignore articles that have been written by sources located at *any* of the specified locations
        @param ignoreSourceGroupUri: ignore articles that have been written by sources in *any* of the specified source groups
        @param ignoreLocationUri: ignore articles that occured in any of the provided locations. A location can be a city or a place
        @param ignoreLang: ignore articles that are written in *any* of the provided languages
        @param keywordsLoc: where should we look when searching using the keywords provided by "keywords" parameter. "body" (default), "title", or "body,title"
        @param ignoreKeywordsLoc: where should we look when data should be used when searching using the keywords provided by "ignoreKeywords" parameter. "body" (default), "title", or "body,title"
        @param isDuplicateFilter: some articles can be duplicates of other articles. What should be done with them. Possible values are:
                "skipDuplicates" (skip the resulting articles that are duplicates of other articles)
                "keepOnlyDuplicates" (return only the duplicate articles)
                "keepAll" (no filtering, default)
        @param hasDuplicateFilter: some articles are later copied by others. What should be done with such articles. Possible values are:
                "skipHasDuplicates" (skip the resulting articles that have been later copied by others)
                "keepOnlyHasDuplicates" (return only the articles that have been later copied by others)
                "keepAll" (no filtering, default)
        @param eventFilter: some articles describe a known event and some don't. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipArticlesWithoutEvent" (skip articles that are not describing any known event in ER)
                "keepOnlyArticlesWithoutEvent" (return only the articles that are not describing any known event in ER)
                "keepAll" (no filtering, default)
        @param requestedResult: the information to return as the result of the query. By default return the list of matching articles
        """
        super(QueryArticles, self).__init__()
        self._setVal("action", "getArticles")

        self._setQueryArrVal(keywords, "keyword", "keywordOper", "and")
        self._setQueryArrVal(conceptUri, "conceptUri", "conceptOper", "and")
        self._setQueryArrVal(categoryUri, "categoryUri", "categoryOper", "or")
        self._setQueryArrVal(sourceUri, "sourceUri", None, "or")
        self._setQueryArrVal(sourceLocationUri, "sourceLocationUri", None, "or")
        self._setQueryArrVal(sourceGroupUri, "sourceGroupUri", None, "or")
        self._setQueryArrVal(locationUri, "locationUri", None, "or")        # location such as "http://en.wikipedia.org/wiki/Ljubljana"

        self._setQueryArrVal(lang, "lang", None, "or")                      # a single lang or list (possible: eng, deu, spa, zho, slv)

        # starting date of the published articles (e.g. 2014-05-02)
        if dateStart != None:
            self._setDateVal("dateStart", dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if dateEnd != None:
            self._setDateVal("dateEnd", dateEnd)

        # first valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionStart != None:
            self._setDateVal("dateMentionStart", dateMentionStart)
        # last valid mentioned date detected in articles (e.g. 2014-05-02)
        if dateMentionEnd != None:
            self._setDateVal("dateMentionEnd", dateMentionEnd)

        # for the negative conditions, only the OR is a valid operator type
        self._setQueryArrVal(ignoreKeywords, "ignoreKeyword", None, "or")
        self._setQueryArrVal(ignoreConceptUri, "ignoreConceptUri", None, "or")
        self._setQueryArrVal(ignoreCategoryUri, "ignoreCategoryUri", None, "or")
        self._setQueryArrVal(ignoreSourceUri, "ignoreSourceUri", None, "or")
        self._setQueryArrVal(ignoreSourceLocationUri, "ignoreSourceLocationUri", None, "or")
        self._setQueryArrVal(ignoreSourceGroupUri, "ignoreSourceGroupUri", None, "or")
        self._setQueryArrVal(ignoreLocationUri, "ignoreLocationUri", None, "or")

        self._setQueryArrVal(ignoreLang, "ignoreLang", None, "or")

        self._setValIfNotDefault("keywordLoc", keywordsLoc, "body")
        self._setValIfNotDefault("ignoreKeywordLoc", ignoreKeywordsLoc, "body")

        self._setValIfNotDefault("isDuplicateFilter", isDuplicateFilter, "keepAll")
        self._setValIfNotDefault("hasDuplicateFilter", hasDuplicateFilter, "keepAll")
        self._setValIfNotDefault("eventFilter", eventFilter, "keepAll")

        # set the information that should be returned
        self.setRequestedResult(requestedResult or RequestArticlesInfo())


    def _getPath(self):
        return "/json/article"


    def addRequestedResult(self, requestArticles):
        """
        Add a result type that you would like to be returned.
        In case you are a subscribed customer you can ask for multiple result types in a single query (for free users, only a single result type can be required per call).
        Result types can be the classes that extend RequestArticles base class (see classes below).
        """
        assert isinstance(requestArticles, RequestArticles), "QueryArticles class can only accept result requests that are of type RequestArticles"
        self.resultTypeList = [item for item in self.resultTypeList if item.getResultType() != requestArticles.getResultType()]
        self.resultTypeList.append(requestArticles)


    def setRequestedResult(self, requestArticles):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestArticles base class (see classes below).
        """
        assert isinstance(requestArticles, RequestArticles), "QueryArticles class can only accept result requests that are of type RequestArticles"
        self.resultTypeList = [requestArticles]


    @staticmethod
    def initWithArticleUriList(uriList):
        """
        instead of making a query, provide a list of article URIs manually, and then produce the desired results on top of them
        """
        q = QueryArticles()
        assert isinstance(uriList, list), "uriList has to be a list of strings that represent article uris"
        q.queryParams = { "action": "getArticles", "articleUri": uriList }
        return q


    @staticmethod
    def initWithComplexQuery(query):
        """
        create a query using a complex article query
        """
        q = QueryArticles()
        # provided an instance of ComplexArticleQuery
        if isinstance(query, ComplexArticleQuery):
            q._setVal("query", json.dumps(query.getQuery()))
        # provided query as a string containing the json object
        elif isinstance(query, six.string_types):
            foo = json.loads(query)
            q._setVal("query", query)
        # provided query as a python dict
        elif isinstance(query, dict):
            q._setVal("query", json.dumps(query))
        else:
            assert False, "The instance of query parameter was not a ComplexArticleQuery, a string or a python dict"
        return q



class QueryArticlesIter(QueryArticles, six.Iterator):
    """
    class that simplifies and combines functionality from QueryArticles and RequestArticlesInfo. It provides an iterator
    over the list of articles that match the specified conditions
    """

    def count(self, eventRegistry):
        """
        return the number of articles that match the criteria
        """
        self.setRequestedResult(RequestArticlesUriList())
        res = eventRegistry.execQuery(self)
        if "error" in res:
            print(res["error"])
        count = res.get("uriList", {}).get("totalResults", 0)
        return count


    def execQuery(self, eventRegistry,
                  sortBy = "rel",
                  sortByAsc = False,
                  returnInfo = ReturnInfo(),
                  articleBatchSize = 100,
                  maxItems = -1,
                  **kwargs):
        """
        @param eventRegistry: instance of EventRegistry class. used to query new article list and uris
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        @param maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out
        """
        self._er = eventRegistry
        self._sortBy = sortBy
        self._sortByAsc = sortByAsc
        self._returnInfo = returnInfo
        self._articleBatchSize = 100    # always download 100 - best for the user since it uses his token and we want to download as much as possible in a single search
        self._uriPage = 0
        self._useArchive = None
        # if we want to return only a subset of items:
        self._maxItems = maxItems
        self._currItem = 0
        # list of cached articles that are yet to be returned by the iterator
        self._articleList = []
        self._uriWgtList = []
        # how many pages do we have for URIs. set once we call _getNextUriPage first
        self._allUriPages = None
        return self


    @staticmethod
    def initWithComplexQuery(query):
        q = QueryArticlesIter()
        # provided an instance of ComplexArticleQuery
        if isinstance(query, ComplexArticleQuery):
            q._setVal("query", json.dumps(query.getQuery()))
        # provided query as a string containing the json object
        elif isinstance(query, six.string_types):
            foo = json.loads(query)
            q._setVal("query", query)
        # provided query as a python dict
        elif isinstance(query, dict):
            q._setVal("query", json.dumps(query))
        else:
            assert False, "The instance of query parameter was not a ComplexArticleQuery, a string or a python dict"
        return q


    def _getNextUriPage(self):
        """download a simple list of article uris"""
        self._uriPage += 1
        self._uriWgtList = []
        if self._allUriPages != None and self._uriPage > self._allUriPages:
            return
        if self._er._verboseOutput:
            print("Downoading page %d of article uris" % (self._uriPage))
        self.setRequestedResult(RequestArticlesUriWgtList(page = self._uriPage, sortBy = self._sortBy, sortByAsc = self._sortByAsc))
        res = self._er.execQuery(self)
        # remember if the archive needed to be used to process the query - use the info later when asking for the articles in batches
        self._useArchive = self._er.getLastReqArchiveUse()
        if "error" in res:
            print(res["error"])
        self._uriWgtList = res.get("uriWgtList", {}).get("results", [])
        self._allUriPages = res.get("uriWgtList", {}).get("pages", 0)


    def _getNextArticleBatch(self):
        """download next batch of articles based on the article uris in the uri list"""
        # try to get more uris, if none
        if len(self._uriWgtList) == 0:
            self._getNextUriPage()
        # if still no uris, then we have nothing to download
        if len(self._uriWgtList) == 0:
            return
        # get uris to download
        uriWgts = self._uriWgtList[:self._articleBatchSize]
        # create a list of uris, without the weights
        uriToWgts = dict([val.split(":") for val in uriWgts])
        uris = [val.split(":")[0] for val in uriWgts]
        # remove used uris
        self._uriWgtList = self._uriWgtList[self._articleBatchSize:]
        if self._er._verboseOutput:
            print("Downoading %d articles..." % (len(uris)))

        q = QueryArticles.initWithArticleUriList(uris)
        q.setRequestedResult(RequestArticlesInfo(page = 1, count = self._articleBatchSize, sortBy = "none", returnInfo = self._returnInfo))
        # download articles and make sure that we set the same archive flag as it was returned when we were processing the uriList request
        res = self._er.execQuery(q, allowUseOfArchive = self._useArchive)
        if "error" in res:
            print("Error while obtaining a list of articles: " + res["error"])
        else:
            assert res.get("articles", {}).get("pages", 0) == 1
        results = res.get("articles", {}).get("results", [])
        for result in results:
            if "uri" in result:
                result["wgt"] = int(uriToWgts.get(result["uri"], "1"))
        self._articleList.extend(results)


    def __iter__(self):
        return self


    def __next__(self):
        """iterate over the available articles"""
        self._currItem += 1
        # if we want to return only the first X items, then finish once reached
        if self._maxItems >= 0 and self._currItem > self._maxItems:
            raise StopIteration
        if len(self._articleList) == 0:
            self._getNextArticleBatch()
        if len(self._articleList) > 0:
            return self._articleList.pop(0)
        raise StopIteration



class RequestArticles:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestArticlesInfo(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 20,
                 sortBy = "date", sortByAsc = False,
                 returnInfo = ReturnInfo()):
        """
        return article details for resulting articles
        @param page: page of the articles to return
        @param count: number of articles to return for the given page (at most 100)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 100, "at most 100 articles can be returned per call"
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))


    def setPage(self, page):
        """
        set the page of results to obtain
        """
        assert page >= 1, "page has to be >= 1"
        self.articlesPage = page



class RequestArticlesUriList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article uris
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 50000
        self.resultType = "uriList"
        self.uriListPage = page
        self.uriListCount = count
        self.uriListSortBy = sortBy
        self.uriListSortByAsc = sortByAsc


    def setPage(self, page):
        assert page >= 1, "page has to be >= 1"
        self.uriListPage = page



class RequestArticlesUriWgtList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article uris together with the scores
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 50000
        self.resultType = "uriWgtList"
        self.uriWgtListPage = page
        self.uriWgtListCount = count
        self.uriWgtListSortBy = sortBy
        self.uriWgtListSortByAsc = sortByAsc


    def setPage(self, page):
        assert page >= 1, "page has to be >= 1"
        self.uriWgtListPage = page



class RequestArticlesUrlList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article urls
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 50000
        self.resultType = "urlList"
        self.urlListPage = page
        self.urlListCount = count
        self.urlListSortBy = sortBy
        self.urlListSortByAsc = sortByAsc



class RequestArticlesTimeAggr(RequestArticles):
    def __init__(self):
        """
        return time distribution of resulting articles
        """
        self.resultType = "timeAggr"



class RequestArticlesConceptAggr(RequestArticles):
    def __init__(self,
                 conceptCount = 25,
                 articlesSampleSize = 10000,
                 returnInfo = ReturnInfo()):
        """
        get aggreate of concepts of resulting articles
        @param conceptCount: number of top concepts to return (at most 500)
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 20000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 500
        assert articlesSampleSize <= 20000
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("conceptAggr"))



class RequestArticlesCategoryAggr(RequestArticles):
    def __init__(self,
                 articlesSampleSize = 20000,
                 returnInfo = ReturnInfo()):
        """
        return aggreate of categories of resulting articles
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
        @param returnInfo: what details about the categories should be included in the returned information
        """
        assert articlesSampleSize <= 50000
        self.resultType = "categoryAggr"
        self.categoryAggrSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("categoryAggr"))



class RequestArticlesSourceAggr(RequestArticles):
    def __init__(self,
                 articlesSampleSize = 20000,
                 returnInfo = ReturnInfo()):
        """
        get aggreate of news sources of resulting articles
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 1000000)
        @param returnInfo: what details about the sources should be included in the returned information
        """
        assert articlesSampleSize <= 1000000
        self.resultType = "sourceAggr"
        self.sourceAggrSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("sourceAggr"))


class RequestArticlesKeywordAggr(RequestArticles):
    def __init__(self,
                 lang = "eng",
                 articlesSampleSize = 10000):
        """
        get top keywords in the resulting articles
        @param lang: articles in which language should be analyzed and processed
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
        """
        assert articlesSampleSize <= 50000
        self.resultType = "keywordAggr"
        self.keywordAggrLang = lang
        self.keywordAggrSampleSize = articlesSampleSize



class RequestArticlesConceptGraph(RequestArticles):
    def __init__(self,
                 conceptCount = 25,
                 linkCount = 50,
                 articlesSampleSize = 10000,
                 returnInfo = ReturnInfo()):
        """
        get concept graph of resulting articles. Identify concepts that frequently co-occur with other concepts
        @param conceptCount: how many concepts should be returned (at most 1000)
        @param linkCount: how many top links between the concepts should be returned (at most 2000)
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 1000
        assert linkCount <= 2000
        assert articlesSampleSize <= 50000
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("conceptGraph"))



class RequestArticlesConceptMatrix(RequestArticles):
    def __init__(self,
                 conceptCount = 25,
                 measure = "pmi",
                 articlesSampleSize = 10000,
                 returnInfo = ReturnInfo()):
        """
        get aggreate of concept co-occurences of resulting articles
        @param conceptCount: how many concepts should be returned (at most 200)
        @param measure: how should the interestingness between the selected pairs of concepts be computed. Options: pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
        @param returnInfo: what details should be included in the returned information
        """
        assert conceptCount <= 200
        assert articlesSampleSize <= 50000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))



class RequestArticlesConceptTrends(RequestArticles):
    def __init__(self,
                 count = 25,
                 articlesSampleSize = 10000,
                 returnInfo = ReturnInfo()):
        """
        get trending of concepts in the resulting articles
        @param count: number of concepts to return (at most 50)
        @param articlesSampleSize: on what sample of results should the aggregate be computed (at most 50000)
        @param returnInfo: what details should be included in the returned information
        """
        assert count <= 50
        assert articlesSampleSize <= 50000
        self.resultType = "conceptTrends"
        self.conceptTrendsConceptCount = count
        self.conceptTrendsSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("conceptTrends"))



class RequestArticlesDateMentionAggr(RequestArticles):
    """
    get mentioned dates in the articles
    """
    def __init__(self):
        self.resultType = "dateMentionAggr"



class RequestArticlesRecentActivity(RequestArticles):
    def __init__(self,
                 maxArticleCount = 60,
                 updatesAfterTm = None,
                 updatesAfterMinsAgo = None,
                 lang = None,
                 mandatorySourceLocation = False,
                 returnInfo = ReturnInfo()):
        """
        get the list of articles that were recently added to the Event Registry and match the selected criteria
        @param maxArticleCount: max articles to return (at most 500)
        @param updatesAfterTm: the time after which the articles were added (returned by previous call to the same method)
        @param updatesAfterMinsAgo: how many minutes into the past should we check (set either this or updatesAfterTm property, but not both)
        @param lang: return only articles in the specified languages (None if no limits). accepts string or a list of strings
        @param mandatorySourceLocation: return only articles for which we know the source's geographic location
        @param returnInfo: what details should be included in the returned information
        """
        assert maxArticleCount <= 1000
        assert updatesAfterTm == None or updatesAfterMinsAgo == None, "You should specify either updatesAfterTm or updatesAfterMinsAgo parameter, but not both"
        self.resultType = "recentActivity"
        self.recentActivityArticlesMaxArticleCount  = maxArticleCount
        if updatesAfterTm != None:
            self.recentActivityArticlesUpdatesAfterTm = QueryParamsBase.encodeDateTime(updatesAfterTm)
        if updatesAfterMinsAgo != None:
            self.recentActivityEventsUpdatesAfterMinsAgo = updatesAfterMinsAgo
        if lang != None:
            self.recentActivityArticlesLang = lang
        self.recentActivityArticlesMandatorySourceLocation = mandatorySourceLocation
        self.__dict__.update(returnInfo.getParams("recentActivityArticles"))