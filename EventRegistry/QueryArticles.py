from Base import *
from ReturnInfo import *

class QueryArticles(Query):
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
    @param dateMentionStart: find articles that explicitely mention a date that is equal or greater than dateMentionStart.
    @param dateMentionEnd: find articles that explicitely mention a date that is lower or equal to dateMentionEnd.
    @param ignoreKeywords: ignore articles that mention all provided keywords
    @param ignoreConceptUri: ignore articles that mention all provided concepts
    @param ignoreLocationUri: ignore articles that occured in any of the provided locations. A location can be a city or a place
    @param ignoreSourceUri: ignore articles that have been written by *any* of the specified news sources
    @param ignoreLang: ignore articles that are written in *any* of the provided languages
    @param categoryIncludeSub: when a category is specified using categoryUri, should also all subcategories be included?
    @param ignoreCategoryIncludeSub: when a category is specified using ignoreCategoryUri, should also all subcategories be included?
    """
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
                 ignoreCategoryIncludeSub = True):
        super(QueryArticles, self).__init__()
        self._setVal("action", "getArticles")

        self._setValIfNotDefault("keywords", keywords, "")          # e.g. "bla bla"
        self._setValIfNotDefault("conceptUri", conceptUri, [])      # a single concept uri or a list (e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"])
        self._setValIfNotDefault("sourceUri", sourceUri, [])        # a single source uri or a list (e.g. ["www.bbc.co.uk"])
        self._setValIfNotDefault("locationUri", locationUri, [])    # a single location uri or a list (e.g. ["http://en.wikipedia.org/wiki/Ljubljana"])
        self._setValIfNotDefault("categoryUri", categoryUri, [])    # a single category uri or a list (e.g. ["http://www.dmoz.org/Science/Astronomy"])
        self._setValIfNotDefault("categoryIncludeSub", categoryIncludeSub, True)    # also include the subcategories for the given categories
        self._setValIfNotDefault("lang", lang, [])                  # a single lang or list (possible: eng, deu, spa, zho, slv)

        self._setValIfNotDefault("dateStart", dateStart, "")        # starting date of the published articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateEnd", dateEnd, "")            # ending date of the published articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateMentionStart", dateMentionStart, "")  # first valid mentioned date detected in articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateMentionEnd", dateMentionEnd, "")      # last valid mentioned date detected in articles (e.g. 2014-05-02)

        self._setValIfNotDefault("ignoreKeywords", ignoreKeywords, "")
        self._setValIfNotDefault("ignoreConceptUri", ignoreConceptUri, [])
        self._setValIfNotDefault("ignoreLang", ignoreLang, [])
        self._setValIfNotDefault("ignoreLocationUri", ignoreLocationUri, [])
        self._setValIfNotDefault("ignoreSourceUri", ignoreSourceUri, [])
        self._setValIfNotDefault("ignoreCategoryUri", ignoreCategoryUri, [])
        self._setValIfNotDefault("ignoreCategoryIncludeSub", ignoreCategoryIncludeSub, True)
        
    def _getPath(self):
        return "/json/article"
    
    def addConcept(self, conceptUri):
        self._addArrayVal("conceptUri", conceptUri)

    def addLocation(self, locationUri):
        self._addArrayVal("locationUri", locationUri)

    def addCategory(self, categoryUri):
        self._addArrayVal("categoryUri", categoryUri)

    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams.pop("keywords", "") + " " + keyword

    def setDateLimit(self, startDate, endDate):
        self._setDateVal("dateStart", startDate)
        self._setDateVal("dateEnd", endDate)

    def setDateMentionLimit(self, startDate, endDate):
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

    def setArticleIdList(self, idList):
        """set a custom list of article ids. the results will be then computed on this list - no query will be done"""
        self.queryParams = { "action": "getArticles", "articleIdList": ",".join([str(val) for val in idList])}
    

class RequestArticles:
    def __init__(self):
        self.resultType = None

class RequestArticlesInfo(RequestArticles):
    """
    return articlel details for resulting articles
    """
    def __init__(self, page = 0, count = 20, 
                 sortBy = "date", sortByAsc = False,    # how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), fq (relevance to the query), socialScore (total shares on social media), facebookShares (fb shares), twitterShares (twitter shares)
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))
        
    def setPage(self, page):
        self.articlesPage = page

    def setCount(self, count):
        self.articlesCount = count
        
class RequestArticlesUriList(RequestArticles):
    """
    return a list of article uris
    """
    def __init__(self):
        self.resultType = "uriList"

class RequestArticlesIdList(RequestArticles):
    """
    return a list of article ids
    """
    def __init__(self):
        self.resultType = "articleIds"

class RequestArticlesTimeAggr(RequestArticles):
    """
    return time distribution of resulting articles
    """
    def __init__(self):
        self.resultType = "timeAggr"

class RequestArticlesCategoryAggr(RequestArticles):
    """
    return aggreate of categories of resulting articles
    """
    def __init__(self, articlesSampleSize = 20000,
                 returnInfo = ReturnInfo()):
        assert articlesSampleSize <= 50000
        self.resultType = "categoryAggr"
        self.categoryAggrSampleSize = articlesSampleSize
        self.__dict__.update(returnInfo.getParams("categoryAggr"))


class RequestArticlesConceptAggr(RequestArticles):
    """
    get aggreate of concepts of resulting articles
    """
    def __init__(self, conceptCount = 25, 
                 articlesSampleSize = 1000, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 500
        assert articlesSampleSize <= 10000
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize  
        self.__dict__.update(returnInfo.getParams("conceptAggr"))
        
class RequestArticlesSourceAggr(RequestArticles):
    """
    get aggreate of news sources of resulting articles
    """
    def __init__(self, 
                 returnInfo = ReturnInfo()):
        self.resultType = "sourceAggr"
        self.__dict__.update(returnInfo.getParams("sourceAggr"))

class RequestArticlesKeywordAggr(RequestArticles):
    """
    get aggreate of sources of resulting articles
    """
    def __init__(self, lang = "eng", articlesSampleSize = 500):
        assert articlesSampleSize <= 1000
        self.resultType = "keywordAggr"
        self.keywordAggrLang = articlesSampleSize
                
class RequestArticlesConceptMatrix(RequestArticles):
    """
    get aggreate of sources of resulting articles
    """
    def __init__(self, count = 25, 
                 measure = "pmi",    # measure options: pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
                 sampleSize = 500, 
                 returnInfo = ReturnInfo()):
        assert count <= 200
        assert sampleSize <= 10000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = count
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = sampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))
        
class RequestArticlesConceptGraph(RequestArticles):
    """
    get concept graph of resulting articles
    """
    def __init__(self, count = 25, 
                 linkCount = 50, 
                 sampleSize = 500, 
                 returnInfo = ReturnInfo()):
        assert count <= 1000
        assert linkCount <= 2000
        assert sampleSize <= 20000
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = count
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = sampleSize
        self.__dict__.update(returnInfo.getParams("conceptGraph"))
        
class RequestArticlesConceptTrends(RequestArticles):
    """
    get trending of concepts in the resulting articles
    """
    def __init__(self, count = 25,
                 returnInfo = ReturnInfo()):
        assert count <= 50
        self.resultType = "conceptTrends"
        self.conceptTrendsConceptCount = count
        self.__dict__.update(returnInfo.getParams("conceptTrends"))

class RequestArticlesDateMentionAggr(RequestArticles):
    """
    get mentioned dates in the articles
    """
    def __init__(self):
        self.resultType = "dateMentionAggr"

class RequestArticlesRecentActivity(RequestArticles):
    """
    get the list of articles that were added recently
    """
    def __init__(self,
                 maxArticleCount = 60,
                 maxMinsBack = 10 * 60,
                 lastArticleActivityId = 0,
                 articlesWithLocationOnly = True,
                 returnInfo = ReturnInfo()):
        assert maxArticleCount <= 1000
        self.resultType = "recentActivity"
        self.articleRecentActivityMaxArticleCount  = maxArticleCount
        self.articleRecentActivityMaxMinsBack = maxMinsBack
        self.articleRecentActivityLastArticleActivityId  = lastArticleActivityId
        self.articleRecentActivityArticlesWithLocationOnly  = articlesWithLocationOnly
        self.__dict__.update(returnInfo.getParams("recentActivity"))
