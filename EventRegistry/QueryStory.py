from eventregistry.Base import *
from eventregistry.ReturnInfo import *

class QueryStory(Query):
    """
    Class for obtaining available info for one or more stories (clusters) in the Event Registry
    NOTE: Story in our terminology is a cluster of articles (and not a single article). An event is
    then something that consists of one or more stories (typically in different languages).

    @param storyUriOrList: a single story uri or a list of story uris
    """
    def __init__(self, storyUriOrList = None):
        super(QueryStory, self).__init__()
        self._setVal("action", "getStory")
        if storyUriOrList != None:
            self.queryByUri(storyUriOrList)

    def _getPath(self):
        return "/json/story"

    def queryByUri(self, uriOrUriList):
        """search stories by their uri(s)"""
        self._setVal("storyUri", uriOrUriList)

    def queryById(self, idOrIdList):
        """specify stories by their id(s)"""
        self._setVal("storyId", idOrIdList)

    def addRequestedResult(self, requestStory):
        """
        Add a result type that you would like to be returned.
        In one QueryStory you can ask for multiple result types.
        Result types can be the classes that extend RequestStory base class (see classes below).
        """
        assert isinstance(requestStory, RequestStory), "QueryStory class can only accept result requests that are of type RequestStory"
        self.resultTypeList.append(requestStory)


class RequestStory:
    def __init__(self):
        self.resultType = None


class RequestStoryInfo(RequestStory):
    """
    return details about a story
    """
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))


class RequestStoryArticles(RequestStory):
    """
    return articles about the story
    """
    def __init__(self,
                 page = 1,              # page of the articles
                 count = 20,            # number of articles to return
                 lang = mainLangs,      # return articles in specified language(s)
                 sortBy = "cosSim", sortByAsc = False,              # order in which story articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to story centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))):
        assert page >= 1, "page has to be >= 1"
        assert count <= 200
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesLang = lang
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))


class RequestStoryArticleUris(RequestStory):
    """
    return a list of article uris
    """
    def __init__(self,
                 lang = mainLangs,
                 sortBy = "cosSim", sortByAsc = False  # order in which story articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to story centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 ):
        self.articleUrisLang = lang
        self.articleUrisSortBy = sortBy
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"


class RequestStoryArticleTrend(RequestStory):
    """
    return trending information for the articles about the story
    """
    def __init__(self,
                 lang = mainLangs,
                 minArticleCosSim = -1,
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))):
        self.resultType = "articleTrend"
        self.articleTrendLang = lang
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update(returnInfo.getParams("articleTrend"))


class RequestStorySimilarStories(RequestStory):
    """
    return a list of similar stories
    """
    def __init__(self,
                 count = 20,                    # number of similar stories to return
                 source = "concept",            # how to compute similarity. Options: concept cca
                 maxDayDiff = sys.maxsize,       # what is the maximum time difference between the similar stories and this one
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "similarStories"
        self.similarEventsCount = count
        self.similarEventsSource = source
        if maxDayDiff != sys.maxsize:
            self.similarEventsMaxDayDiff = maxDayDiff
        self.similarEventsAddArticleTrendInfo = addArticleTrendInfo
        self.__dict__.update(returnInfo.getParams("similarEvents"))
