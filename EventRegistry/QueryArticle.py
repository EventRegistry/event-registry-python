from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class QueryArticle(Query):
    """
    Class for obtaining available info for one or more articles in the Event Registry

    @param articleUriOrUriList: a single article uri or a list of article uris
    """
    def __init__(self,
                 articleUriOrUriList):
        super(QueryArticle, self).__init__()
        self._setVal("articleUri", articleUriOrUriList)
        self._setVal("action", "getArticle")

    def _getPath(self):
        return "/json/article"

    @staticmethod
    @deprecated
    def queryById(articleIdOrIdList):
        """
        obtain information about one or more articles by providing their Event Registry ids
        """
        q = QueryArticle([])
        q.queryParams["articleId"] = articleIdOrIdList
        return q

    @staticmethod
    def queryByUri(articleUriOrUriList):
        """
        obtain information about one or more articles by providing their article uris (newsfeed ids, such as "284017606")
        """
        q = QueryArticle([])
        q.queryParams["articleUri"] = articleUriOrUriList
        return q

    def addRequestedResult(self, requestArticle):
        """
        Add a result type that you would like to be returned.
        In one QueryArticle you can ask for multiple result types.
        Result types can be the classes that extend RequestArticle base class (see classes below).
        """
        assert isinstance(requestArticle, RequestArticle), "QueryArticle class can only accept result requests that are of type RequestArticle"
        self.resultTypeList.append(requestArticle)


class RequestArticle:
    def __init__(self):
        self.resultType = None


class RequestArticleInfo(RequestArticle):
    """
    return details about the article
    """
    def __init__(self, returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))


class RequestArticleSimilarArticles(RequestArticle):
    """
    return a list of similar articles based on the CCA
    """
    def __init__(self, page = 1,                            # page of the articles
                 count = 20,                                # number of articles to return
                 lang = ["eng"],                            # in which language(s) should be the similar articles
                 limitPerLang = -1,                         # max number of articles per language to return (-1 for no limit)
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        assert page >= 1, "page has to be >= 1"
        assert count <= 200
        self.resultType = "similarArticles"
        self.similarArticlesPage = page
        self.similarArticlesCount = count
        self.similarArticlesLang = lang
        self.similarArticlesLimitPerLang = limitPerLang
        self.__dict__.update(returnInfo.getParams("similarArticles"))


class RequestArticleDuplicatedArticles(RequestArticle):
    """
    return a list of duplicated articles of the current article
    """
    def __init__(self, page = 1,        # page of the articles
                 count = 20,            # number of articles to return
                 sortBy = "cosSim", sortByAsc = False,              # how are the articles sorted. Options: id, date, cosSim, fq, socialScore, facebookShares, twitterShares
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        assert page >= 1, "page has to be >= 1"
        self.resultType = "duplicatedArticles"
        self.duplicatedArticlesPage = page
        self.duplicatedArticlesCount = count
        self.duplicatedArticlesSortBy = sortBy
        self.duplicatedArticlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("duplicatedArticles"))


class RequestArticleOriginalArticle(RequestArticle):
    """
    return the article that is the original of the given article (the current article is a duplicate)
    """
    def __init__(self, returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = -1))):
        self.resultType = "originalArticle"
        self.__dict__.update(returnInfo.getParams("originalArticle"))




