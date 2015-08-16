from ERBase import *
from ERReturnInfo import *

# class for finding all available info for one or more articles in the event registry 
class QueryArticle(Query):
    def __init__(self, articleUriOrUriList):
        super(QueryArticle, self).__init__();
        self._setVal("articleUri", articleUriOrUriList);      # a single article uri or a list of article uris
        self._setVal("action", "getArticle");

    def _getPath(self):
        return "/json/article";   
   
    @staticmethod
    def queryById(articleIdOrIdList):
        q = QueryArticle([])
        q.queryParams["articleId"] = articleIdOrIdList
        return q

    @staticmethod
    def queryByUrl(articleUrlOrUrlList):
        q = QueryArticle([])
        q.queryParams["articleUrl"] = articleUrlOrUrlList
        return q
    
    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestArticle):
        if not isinstance(requestArticle, RequestArticle):
            raise AssertionError("QueryArticle class can only accept result requests that are of type RequestArticle");
        self.resultTypeList.append(requestArticle);


# #####################################
# #####################################
class RequestArticle:
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestArticleInfo(RequestArticle):
    def __init__(self, returnInfo = ReturnInfo(articleMaxBodyLen = -1)):        
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))
        
# return a list of similar articles based on the CCA
class RequestArticleSimilarArticles(RequestArticle):
    def __init__(self, page = 0, count = 20, 
                 lang = ["eng"], 
                 limitPerLang = -1, 
                 sortBy = "cosSim", sortByAsc = False,      # id, date, cosSim, fq, socialScore, facebookShares, twitterShares
                 returnInfo = ReturnInfo(articleMaxBodyLen = -1)):
        assert count <= 200
        self.resultType = "similarArticles"
        self.similarArticlesPage = page                 # page of the articles
        self.similarArticlesCount = count               # number of articles to return
        self.similarArticlesLang = lang                 # in which language(s) should be the similar articles
        self.similarArticlesLimitPerLang = limitPerLang # max number of articles per language to return (-1 for no limit)
        self.similarArticlesSortBy = sortBy             # how are the event articles sorted (date, id, cosSim, fq)
        self.similarArticlesSortByAsc = sortByAsc      
        self.__dict__.update(returnInfo.getParams("similarArticles"))

# return a list of duplicated articles of the current article
class RequestArticleDuplicatedArticles(RequestArticle):
    def __init__(self, page = 0, count = 20, 
                 sortBy = "cosSim", sortByAsc = False, 
                 conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 returnInfo = ReturnInfo(articleMaxBodyLen = -1)):
        self.resultType = "duplicatedArticles"
        self.duplicatedArticlesPage = page                 # page of the articles
        self.duplicatedArticlesCount = count               # number of articles to return
        self.duplicatedArticlesSortBy = sortBy             # how are the event articles sorted (date, id)
        self.duplicatedArticlesSortByAsc = sortByAsc      
        self.__dict__.update(returnInfo.getParams("duplicatedArticles"))

# return the article that is the original of the given article (the current article is a duplicate)
class RequestArticleOriginalArticle(RequestArticle):
    def __init__(self, returnInfo = ReturnInfo(articleMaxBodyLen = -1)):
        self.resultType = "originalArticle"
        self.__dict__.update(returnInfo.getParams("originalArticle"))
        
        


