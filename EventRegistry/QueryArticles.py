
import six
from eventregistry.Base import *
from eventregistry.ReturnInfo import *


class QueryArticles(Query):
    def __init__(self,
                 keywords = "",
                 conceptUri = [],
                 sourceUri = [],
                 locationUri = [],
                 categoryUri = [],
                 lang = [],
                 dateStart = "",
                 dateEnd = "",
                 dateMentionStart = "",
                 dateMentionEnd = "",
                 ignoreKeywords = "",
                 ignoreConceptUri = [],
                 ignoreLocationUri = [],
                 ignoreSourceUri = [],
                 ignoreCategoryUri = [],
                 ignoreLang = [],
                 categoryIncludeSub = True,
                 conceptOper = "AND",
                 ignoreCategoryIncludeSub = True,
                 isDuplicateFilter = "keepAll",
                 hasDuplicateFilter = "keepAll",
                 eventFilter = "keepAll"):
        """
        Query class for searching for individual articles in the Event Registry.
        The resulting articles have to match all specified conditions. If a parameter value equals "" or [], then it is ignored.
        In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

        @param keywords: find articles that mention all the specified keywords.
            In case of multiple keywords, separate them with space. Example: "apple iphone".
        @param conceptUri: find articles where the concept with concept uri is mentioned.
            A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
            If multiple concept uris are provided, resulting articles have to mention *all* of them.
            To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
        @param sourceUri: find articles that were written by a news source sourceUri.
            If multiple sources are provided, resulting articles have to be written by *any* of the provided news sources.
            Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
        @param locationUri: find articles that describe an event that occured at a particular location.
            Location uri can either be a city or a country.
            If multiple locations are provided, resulting articles have to match *any* of the locations.
            Location uri for a given name can be obtained using EventRegistry.getLocationUri().
        @param categoryUri: find articles that are assigned into a particular category.
            If multiple categories are provided, resulting articles have to be assigned to *any* of the categories.
            A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
        @param lang: find articles that are written in the specified language.
            If more than one language is specified, resulting articles has to be written in *any* of the languages.
        @param dateStart: find articles that were written on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
        @param dateEnd: find articles that occured before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
        @param dateMentionStart: find articles that explicitly mention a date that is equal or greater than dateMentionStart.
        @param dateMentionEnd: find articles that explicitly mention a date that is lower or equal to dateMentionEnd.
        @param ignoreKeywords: ignore articles that mention all provided keywords
        @param ignoreConceptUri: ignore articles that mention all provided concepts
        @param ignoreLocationUri: ignore articles that occured in any of the provided locations. A location can be a city or a place
        @param ignoreSourceUri: ignore articles that have been written by *any* of the specified news sources
        @param ignoreLang: ignore articles that are written in *any* of the provided languages
        @param categoryIncludeSub: when a category is specified using categoryUri, should also all subcategories be included?
        @param ignoreCategoryIncludeSub: when a category is specified using ignoreCategoryUri, should also all subcategories be included?
        @param conceptOper: Boolean operator to use in cases when multiple concepts are specified. Possible values are:
                "AND" if all concepts should be mentioned in the resulting articles
                "OR" if any of the concept should be mentioned in the resulting articles
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
        """
        super(QueryArticles, self).__init__()
        self._setVal("action", "getArticles")

        self._setValIfNotDefault("keywords", keywords, "")          # e.g. "bla bla"
        self._setValIfNotDefault("conceptUri", conceptUri, [])      # a single concept uri or a list (e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"])
        self._setValIfNotDefault("sourceUri", sourceUri, [])        # a single source uri or a list (e.g. ["www.bbc.co.uk"])
        self._setValIfNotDefault("locationUri", locationUri, [])    # a single location uri or a list (e.g. ["http://en.wikipedia.org/wiki/Ljubljana"])
        self._setValIfNotDefault("categoryUri", categoryUri, [])    # a single category uri or a list (e.g. ["http://www.dmoz.org/Science/Astronomy"])
        self._setValIfNotDefault("categoryIncludeSub", categoryIncludeSub, True)    # also include the subcategories for the given categories
        self._setValIfNotDefault("lang", lang, [])                  # a single lang or list (possible: eng, deu, spa, zho, slv)

        # starting date of the published articles (e.g. 2014-05-02)
        if (dateStart != ""):
            self._setDateVal("dateStart", dateStart)
        # ending date of the published articles (e.g. 2014-05-02)
        if (dateEnd != ""):
            self._setDateVal("dateEnd", dateEnd)

        # first valid mentioned date detected in articles (e.g. 2014-05-02)
        if (dateMentionStart != ""):
            self._setDateVal("dateMentionStart", dateMentionStart)
        # last valid mentioned date detected in articles (e.g. 2014-05-02)
        if (dateMentionEnd != ""):
            self._setDateVal("dateMentionEnd", dateMentionEnd)

        self._setValIfNotDefault("ignoreKeywords", ignoreKeywords, "")
        self._setValIfNotDefault("ignoreConceptUri", ignoreConceptUri, [])
        self._setValIfNotDefault("ignoreLang", ignoreLang, [])
        self._setValIfNotDefault("ignoreLocationUri", ignoreLocationUri, [])
        self._setValIfNotDefault("ignoreSourceUri", ignoreSourceUri, [])
        self._setValIfNotDefault("ignoreCategoryUri", ignoreCategoryUri, [])
        self._setValIfNotDefault("ignoreCategoryIncludeSub", ignoreCategoryIncludeSub, True)
        self._setValIfNotDefault("conceptOper", conceptOper, "AND")

        self._setValIfNotDefault("isDuplicateFilter", isDuplicateFilter, "keepAll")
        self._setValIfNotDefault("hasDuplicateFilter", hasDuplicateFilter, "keepAll")
        self._setValIfNotDefault("eventFilter", eventFilter, "keepAll")


    def _getPath(self):
        return "/json/article"


    def addConcept(self, conceptUri):
        """add concept to the search"""
        self._addArrayVal("conceptUri", conceptUri)


    def addLocation(self, locationUri):
        """add a location to the search"""
        self._addArrayVal("locationUri", locationUri)


    def addCategory(self, categoryUri):
        """add a category to the search"""
        self._addArrayVal("categoryUri", categoryUri)


    def addNewsSource(self, newsSourceUri):
        """add a news source to the search"""
        self._addArrayVal("sourceUri", newsSourceUri)


    def addKeyword(self, keyword):
        """add a keyword or a phrase to the search"""
        self.queryParams["keywords"] = self.queryParams.pop("keywords", "") + " " + keyword


    def setDateLimit(self, startDate, endDate):
        """
        add a date restriction to the search
        @param startDate: instance of a string, date or datetime
        @param endDate: instance of a string, date or datetime
        """
        self._setDateVal("dateStart", startDate)
        self._setDateVal("dateEnd", endDate)


    def setDateMentionLimit(self, startDate, endDate):
        """
        require date mentiones to the search
        @param startDate: instance of a string, date or datetime
        @param endDate: instance of a string, date or datetime
        """
        self._setDateVal("dateMentionStart", startDate)
        self._setDateVal("dateMentionEnd", endDate)


    def addRequestedResult(self, requestArticles):
        """
        Add a result type that you would like to be returned.
        In one QueryArticles you can ask for multiple result types.
        Result types can be the classes that extend RequestArticles base class (see classes below).
        """
        assert isinstance(requestArticles, RequestArticles), "QueryArticles class can only accept result requests that are of type RequestArticles"
        self.resultTypeList.append(requestArticles)


    def setRequestedResult(self, requestArticles):
        """
        Set the single result type that you would like to be returned. If some other request type was previously set, it will be overwritten.
        Result types can be the classes that extend RequestArticles base class (see classes below).
        """
        assert isinstance(requestArticles, RequestArticles), "QueryArticles class can only accept result requests that are of type RequestArticles"
        self.resultTypeList = [requestArticles]


    @deprecated
    def setArticleIdList(self, idList):
        """set a custom list of article ids. the results will be then computed on this list - no query will be done"""
        self.queryParams = { "action": "getArticles", "articleIdList": ",".join([str(val) for val in idList])}


    def setArticleUriList(self, uriList):
        """set a custom list of article uris. the results will be then computed on this list - no query will be done"""
        self.queryParams = { "action": "getArticles", "articleUri": uriList }


    @staticmethod
    def initWithArticleUriList(uriList):
        q = QueryArticles()
        q.setArticleUriList(uriList)
        return q


    @staticmethod
    def initWithArticleIdList(idList):
        q = QueryArticles()
        q.setArticleIdList(idList)
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
        self.clearRequestedResults()
        self.addRequestedResult(RequestArticlesUriList())
        res = eventRegistry.execQuery(self)
        count = res.get("uriList", {}).get("totalResults", 0)
        return count


    def execQuery(self, eventRegistry,
                  sortBy = "rel",
                  sortByAsc = False,
                  returnInfo = ReturnInfo(),
                  articleBatchSize = 200):
        """
        @param eventRegistry: instance of EventRegistry class. used to query new article list and uris
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        @param articleBatchSize: number of articles to download at once (we are not downloading article by article) (at most 200)
        """
        assert articleBatchSize <= 200, "You can not have a batch size > 200 items"
        self._er = eventRegistry
        self._sortBy = sortBy
        self._sortByAsc = sortByAsc
        self._returnInfo = returnInfo
        self._articleBatchSize = articleBatchSize
        self._uriPage = 0
        # list of cached articles that are yet to be returned by the iterator
        self._articleList = []
        self._uriList = []
        # how many pages do we have for URIs. set once we call _getNextUriPage first
        self._allUriPages = None
        return self


    def _getNextUriPage(self):
        """download a simple list of article uris"""
        self._uriPage += 1
        self._uriList = []
        if self._allUriPages != None and self._uriPage > self._allUriPages:
            return
        if self._er._verboseOutput:
            print("Downoading page %d of article uris" % (self._uriPage))
        self.clearRequestedResults()
        self.addRequestedResult(RequestArticlesUriList(page = self._uriPage, sortBy = self._sortBy, sortByAsc = self._sortByAsc))
        res = self._er.execQuery(self)
        self._uriList = res.get("uriList", {}).get("results", [])
        self._allUriPages = res.get("uriList", {}).get("pages", 0)
        self._getNextArticleBatch()


    def _getNextArticleBatch(self):
        """download next batch of articles based on the article uris in the uri list"""
        self.clearRequestedResults()
        # try to get more uris, if none
        if len(self._uriList) == 0:
            self._getNextUriPage()
        # if still no uris, then we have nothing to download
        if len(self._uriList) == 0:
            return
        # get uris to download
        uris = self._uriList[:self._articleBatchSize]
        if self._er._verboseOutput:
            print("Downoading %d articles..." % (len(uris)))
        # remove used uris
        self._uriList = self._uriList[self._articleBatchSize:]
        self.setArticleUriList(uris)
        self.addRequestedResult(RequestArticlesInfo(page = 1, count = self._articleBatchSize, sortBy = "none", returnInfo = self._returnInfo))
        res = self._er.execQuery(self)
        self._articleList.extend(res.get("articles", {}).get("results", []))


    def __iter__(self):
        return self


    def __next__(self):
        """iterate over the available articles"""
        if len(self._articleList) == 0:
            self._getNextArticleBatch()
        if len(self._articleList) > 0:
            return self._articleList.pop(0)
        raise StopIteration



class RequestArticles:
    def __init__(self):
        self.resultType = None



class RequestArticlesInfo(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 20,
                 sortBy = "date", sortByAsc = False,
                 returnInfo = ReturnInfo()):
        """
        return article details for resulting articles
        @param page: page of the articles to return
        @param count: number of articles to return for the given page (at most 200)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 200
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


    def setCount(self, count):
        """
        set the number of articles to return per query
        """
        self.articlesCount = count



class RequestArticlesUriList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article uris
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 50000
        self.resultType = "uriList"
        self.uriListPage = page
        self.uriListCount = count
        self.uriListSortBy = sortBy
        self.uriListSortByAsc = sortByAsc



class RequestArticlesIdList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article ids
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False) according to the sortBy criteria
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 50000
        self.resultType = "idList"
        self.idListPage = page
        self.idListCount = count
        self.idListSortBy = sortBy
        self.idListSortByAsc = sortByAsc



class RequestArticlesUrlList(RequestArticles):
    def __init__(self,
                 page = 1,
                 count = 10000,
                 sortBy = "fq", sortByAsc = False):
        """
        return a list of article urls
        @param page: page of the results (1, 2, ...)
        @param count: number of items to return in a single query (at most 50000)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media)
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
                 maxMinsBack = 10 * 60,
                 lastActivityId = 0,
                 lang = None,
                 mandatorySourceLocation = False,
                 returnInfo = ReturnInfo()):
        """
        get the list of articles that were recently added to the Event Registry and match the selected criteria
        @param maxArticleCount: max articles to return (at most 500)
        @param: maxMinsBack: maximum number of minutes in the history to look at
        @param lastActivityId: id of the last activity (returned by previous call to the same method)
        @param lang: return only articles in the specified languages (None if no limits). accepts string or a list of strings
        @param mandatorySourceLocation: return only articles for which we know the source's geographic location
        @param returnInfo: what details should be included in the returned information
        """
        assert maxArticleCount <= 100
        self.resultType = "recentActivity"
        self.recentActivityArticlesMaxArticleCount  = maxArticleCount
        self.recentActivityArticlesMaxMinsBack = maxMinsBack
        self.recentActivityArticlesLastActivityId  = lastActivityId
        if lang != None:
            self.recentActivityArticlesLang = lang

        self.recentActivityArticlesMandatorySourceLocation = mandatorySourceLocation
        self.__dict__.update(returnInfo.getParams("recentActivityArticles"))