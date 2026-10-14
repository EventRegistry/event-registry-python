from eventregistry.Base import Query
from eventregistry.ReturnInfo import ArticleInfoFlags, ReturnInfo
from typing import List, Union

# the names exported by "from eventregistry import *"
__all__ = ["QueryArticle", "RequestArticle", "RequestArticleInfo", "RequestArticleSimilarArticles",
           "RequestArticleDuplicatedArticles", "RequestArticleOriginalArticle"]


class QueryArticle(Query):
    def __init__(self,
                 articleUriOrUriList: Union[str, List[str]],
                 requestedResult: Union["RequestArticle", None] = None):
        """
        Class for obtaining available info for one or more articles in the Event Registry

        Args:
            articleUriOrUriList: a single article uri or a list of article uris
            requestedResult: the information to return as the result of the query. By default return the information about the article
        """
        super().__init__()
        self._setVal("articleUri", articleUriOrUriList)
        self._setVal("action", "getArticle")
        self.setRequestedResult(requestedResult or RequestArticleInfo())


    def _getPath(self):
        return "/api/v1/article"


    @staticmethod
    def queryByUri(articleUriOrUriList: Union[str, List[str]]):
        """
        obtain information about one or more articles by providing their article uris (newsfeed ids, such as "284017606")

        Args:
            articleUriOrUriList: single article uri or a list of article uris to query
        """
        q = QueryArticle([])
        q.queryParams["articleUri"] = articleUriOrUriList
        return q


    def setRequestedResult(self, requestArticle: "RequestArticle"):
        """
        Set the single result type that you would like to be returned. If some other request type was previously set, it will be overwritten.
        Result types can be the classes that extend RequestArticle base class (see classes below).
        """
        if not (isinstance(requestArticle, RequestArticle)):
            raise TypeError("QueryArticle class can only accept result requests that are of type RequestArticle")
        self.resultTypeList = [requestArticle]



class RequestArticle:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestArticleInfo(RequestArticle):
    def __init__(self, returnInfo: Union[ReturnInfo, None] = None):
        """
        return details about the article

        Args:
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        self.resultType = "info"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))).getParams("info"))



class RequestArticleSimilarArticles(RequestArticle):
    def __init__(self,
                 page: int = 1,
                 count: int = 20,
                 lang: Union[str, List[str], None] = None,
                 limitPerLang: int = -1,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return a list of similar articles based on the CCA

        Args:
            page: page of the articles
            count: number of articles to return (at most 200)
            lang: in which language(s) should be the similar articles
            limitPerLang: max number of articles per language to return (-1 for no limit)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 200):
            raise ValueError("at most 200 articles can be returned per call")
        self.resultType = "similarArticles"
        self.similarArticlesPage = page
        self.similarArticlesCount = count
        self.similarArticlesLang = lang if lang is not None else ["eng"]
        self.similarArticlesLimitPerLang = limitPerLang
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))).getParams("similarArticles"))



class RequestArticleDuplicatedArticles(RequestArticle):
    def __init__(self,
                 page: int = 1,
                 count: int = 20,
                 sortBy: str = "cosSim", sortByAsc: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return a list of duplicated articles of the current article

        Args:
            page: page of the articles
            count: number of articles to return (at most 200)
            sortBy: how are the articles sorted. Options: date, cosSim, fq
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 200):
            raise ValueError("at most 200 articles can be returned per call")
        self.resultType = "duplicatedArticles"
        self.duplicatedArticlesPage = page
        self.duplicatedArticlesCount = count
        self.duplicatedArticlesSortBy = sortBy
        self.duplicatedArticlesSortByAsc = sortByAsc
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))).getParams("duplicatedArticles"))



class RequestArticleOriginalArticle(RequestArticle):
    def __init__(self,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return the article that is the original of the given article (the current article is a duplicate)

        Args:
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        self.resultType = "originalArticle"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))).getParams("originalArticle"))
