from ERBase import *
from ERReturnInfo import *

# query class for searching for articles in the event registry 
class QueryArticles(Query):
    def __init__(self,  **kwargs):
        super(QueryArticles, self).__init__();
        self._setVal("action", "getArticles");

        self._setValIfNotDefault("keywords", kwargs, "");           # e.g. "bla bla"
        self._setValIfNotDefault("conceptUri", kwargs, []);         # a single concept uri or a list (e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"])
        self._setValIfNotDefault("lang", kwargs, []);               # a single lang or list (possible: eng, deu, spa, zho, slv)
        self._setValIfNotDefault("publisherUri", kwargs, []);       # a single source uri or a list (e.g. ["www.bbc.co.uk"])
        self._setValIfNotDefault("locationUri", kwargs, []);        # a single location uri or a list (e.g. ["http://en.wikipedia.org/wiki/Ljubljana"])
        self._setValIfNotDefault("categoryUri", kwargs, []);        # a single category uri or a list (e.g. ["http://www.dmoz.org/Science/Astronomy"])
        self._setValIfNotDefault("categoryIncludeSub", kwargs, True);       # also include the subcategories for the given categories
        self._setValIfNotDefault("dateStart", kwargs, "");                  # starting date of the published articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateEnd", kwargs, "");                    # ending date of the published articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateMentionStart", kwargs, "");   # first valid mentioned date detected in articles (e.g. 2014-05-02)
        self._setValIfNotDefault("dateMentionEnd", kwargs, "");     # last valid mentioned date detected in articles (e.g. 2014-05-02)

        self._setValIfNotDefault("ignoreKeywords", kwargs, "");
        self._setValIfNotDefault("ignoreConceptUri", kwargs, []);
        self._setValIfNotDefault("ignoreLang", kwargs, []);
        self._setValIfNotDefault("ignoreLocationUri", kwargs, []);
        self._setValIfNotDefault("ignorePublisherUri", kwargs, []);
        self._setValIfNotDefault("ignoreCategoryUri", kwargs, []);
        self._setValIfNotDefault("ignoreCategoryIncludeSub", kwargs, True);
        
    def _getPath(self):
        return "/json/article";
    
    def addConcept(self, conceptUri):
        self._addArrayVal("conceptUri", conceptUri);

    def addLocation(self, locationUri):
        self._addArrayVal("locationUri", locationUri);

    def addCategory(self, categoryUri):
        self._addArrayVal("categoryUri", categoryUri)

    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams.pop("keywords", "") + " " + keyword;

    def setDateLimit(self, startDate, endDate):
        self._setDateVal("dateStart", startDate);
        self._setDateVal("dateEnd", endDate);

    def setDateMentionLimit(self, startDate, endDate):
        self._setDateVal("dateMentionStart", startDate);
        self._setDateVal("dateMentionEnd", endDate);          

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestArticles):
        if not isinstance(requestArticles, RequestArticles):
            raise AssertionError("QueryArticles class can only accept result requests that are of type RequestArticles");
        self.resultTypeList.append(requestArticles);

    # set a custom list of article ids. the results will be then computed on this list - no query will be done
    def setArticleIdList(self, idList):
        self.queryParams = { "action": "getArticles", "articleIdList": ",".join([str(val) for val in idList])};
    

# #####################################
# #####################################
class RequestArticles:
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestArticlesInfo(RequestArticles):
    # possible sorting values: date, id, cosSim, fq
    def __init__(self, page = 0, count = 20, 
                 sortBy = "date", sortByAsc = False,    # id, date, cosSim, fq, socialScore, facebookShares, twitterShares
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy        # date, id, cosSim, fq
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))
        
    def setPage(self, page):
        self.articlesPage = page

    def setCount(self, count):
        self.articlesCount = count
        
# return a list of article uris
class RequestArticlesUriList(RequestArticles):
    def __init__(self):
        self.resultType = "uriList"

# return a list of article ids
class RequestArticlesIdList(RequestArticles):
    def __init__(self):
        self.resultType = "articleIds"

# get time distribution of resulting articles
class RequestArticlesTimeAggr(RequestArticles):
    def __init__(self):
        self.resultType = "timeAggr"

# get aggreate of categories of resulting articles
class RequestArticlesCategoryAggr(RequestArticles):
    def __init__(self, articlesSampleSize = 20000):
        assert articlesSampleSize <= 50000
        self.resultType = "categoryAggr"
        self.categoryAggrSampleSize = articlesSampleSize
        
# get aggreate of concepts of resulting articles
class RequestArticlesConceptAggr(RequestArticles):
    def __init__(self, conceptCount = 25, 
                 articlesSampleSize = 1000, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 500
        assert articlesSampleSize <= 10000
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize  
        self.__dict__.update(returnInfo.getParams("conceptAggr"))
        

# get aggreate of sources of resulting articles
class RequestArticlesSourceAggr(RequestArticles):
    def __init__(self, 
                 returnInfo = ReturnInfo()):
        self.resultType = "sourceAggr"
        self.__dict__.update(returnInfo.getParams("sourceAggr"))

# get aggreate of sources of resulting articles
class RequestArticlesKeywordAggr(RequestArticles):
    def __init__(self, lang = "eng", articlesSampleSize = 500):
        assert articlesSampleSize <= 1000
        self.resultType = "keywordAggr"
        self.keywordAggrLang = articlesSampleSize
                
# get aggreate of sources of resulting articles
class RequestArticlesConceptMatrix(RequestArticles):
    def __init__(self, count = 25, 
                 measure = "pmi", 
                 sampleSize = 500, 
                 returnInfo = ReturnInfo()):
        assert count <= 200
        assert sampleSize <= 10000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = count
        self.conceptMatrixMeasure = measure             # pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
        self.conceptMatrixSampleSize = sampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))
        
# get concept graph of resulting articles
class RequestArticlesConceptGraph(RequestArticles):
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
        
# get trending of concepts in the resulting articles
class RequestArticlesConceptTrends(RequestArticles):
    def __init__(self, count = 25,
                 returnInfo = ReturnInfo()):
        assert count <= 50
        self.resultType = "conceptTrends"
        self.trendingConceptsConceptCount = count
        self.__dict__.update(returnInfo.getParams("conceptTrends"))

# get mentioned dates in the articles
class RequestArticlesDateMentionAggr(RequestArticles):
    def __init__(self):
        self.resultType = "dateMentionAggr"

# get the list of articles that were added recently
class RequestArticlesRecentActivity(RequestArticles):
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
