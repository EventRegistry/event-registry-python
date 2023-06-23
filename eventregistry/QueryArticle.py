from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from typing import List, Union

class QueryArticle(Query):
    def __init__(self,
                 articleUriOrUriList: Union[str, List[str]],
                 requestedResult: Union["RequestArticle", None] = None):
        """
        Class for obtaining available info for one or more articles in the Event Registry
        @param articleUriOrUriList: a single article uri or a list of article uris
        @param requestedResult: the information to return as the result of the query. By default return the information about the article
        """
        super(QueryArticle, self).__init__()
        self._setVal("articleUri", articleUriOrUriList)
        self._setVal("action", "getArticle")
        self.setRequestedResult(requestedResult or RequestArticleInfo())


    def _getPath(self):
        return "/api/v1/article"


    @staticmethod
    def queryByUri(articleUriOrUriList: Union[str, List[str]]):
        """
        obtain information about one or more articles by providing their article uris (newsfeed ids, such as "284017606")
        @param articleUriOrUriList: single article uri or a list of article uris to query
        """
        q = QueryArticle([])
        q.queryParams["articleUri"] = articleUriOrUriList
        return q


    def setRequestedResult(self, requestArticle: "RequestArticle"):
        """
        Set the single result type that you would like to be returned. If some other request type was previously set, it will be overwritten.
        Result types can be the classes that extend RequestArticle base class (see classes below).
        """
        assert isinstance(requestArticle, RequestArticle), "QueryArticle class can only accept result requests that are of type RequestArticle"
        self.resultTypeList = [requestArticle]



class RequestArticle:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestArticleInfo(RequestArticle):
    def __init__(self, returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        """
        return details about the article
        @param returnInfo: what details should be included in the returned information
        """
        super(RequestArticle, self).__init__()
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))



class RequestArticleSimilarArticles(RequestArticle):
    def __init__(self,
                 page: int = 1,
                 count: int = 20,
                 lang: Union[str, List[str]] = ["eng"],
                 limitPerLang: int = -1,
                 returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        """
        return a list of similar articles based on the CCA
        @param page: page of the articles
        @param count: number of articles to return (at most 200)
        @param lang: in which language(s) should be the similar articles
        @param limitPerLang: max number of articles per language to return (-1 for no limit)
        @param returnInfo: what details should be included in the returned information
        """
        super(RequestArticle, self).__init__()
        assert page >= 1, "page has to be >= 1"
        assert count <= 200, "at most 200 articles can be returned per call"
        self.resultType = "similarArticles"
        self.similarArticlesPage = page
        self.similarArticlesCount = count
        self.similarArticlesLang = lang
        self.similarArticlesLimitPerLang = limitPerLang
        self.__dict__.update(returnInfo.getParams("similarArticles"))



class RequestArticleDuplicatedArticles(RequestArticle):
    def __init__(self,
                 page: int = 1,
                 count: int = 20,
                 sortBy: str = "cosSim", sortByAsc: bool = False,
                 returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        """
        return a list of duplicated articles of the current article
        @param page: page of the articles
        @param count: number of articles to return (at most 200)
        @param sortBy: how are the articles sorted. Options: id, date, cosSim, fq, socialScore, facebookShares, twitterShares
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        super(RequestArticle, self).__init__()
        assert page >= 1, "page has to be >= 1"
        assert count <= 200, "at most 200 articles can be returned per call"
        self.resultType = "duplicatedArticles"
        self.duplicatedArticlesPage = page
        self.duplicatedArticlesCount = count
        self.duplicatedArticlesSortBy = sortBy
        self.duplicatedArticlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("duplicatedArticles"))



class RequestArticleOriginalArticle(RequestArticle):
    def __init__(self,
                 returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        """
        return the article that is the original of the given article (the current article is a duplicate)
        @param returnInfo: what details should be included in the returned information
        """
        super(RequestArticle, self).__init__()
        self.resultType = "originalArticle"
        self.__dict__.update(returnInfo.getParams("originalArticle"))
