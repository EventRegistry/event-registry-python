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


    def addRequestedResult(self, requestStory):
        """
        Add a result type that you would like to be returned.
        In one QueryStory you can ask for multiple result types.
        Result types can be the classes that extend RequestStory base class (see classes below).
        """
        assert isinstance(requestStory, RequestStory), "QueryStory class can only accept result requests that are of type RequestStory"
        self.resultTypeList = [item for item in self.resultTypeList if item.getResultType() != requestStory.getResultType()]
        self.resultTypeList.append(requestStory)


    def setRequestedResult(self, requestStory):
        """
        Set the single result type that you would like to be returned. If some other request type was previously set, it will be overwritten.
        Result types can be the classes that extend RequestStory base class (see classes below).
        """
        assert isinstance(requestStory, RequestStory), "QueryStory class can only accept result requests that are of type RequestStory"
        self.resultTypeList = [requestStory]



class RequestStory:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



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
                 page = 1,
                 count = 20,
                 sortBy = "cosSim", sortByAsc = False,
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))):
        """
        return articles in the story (cluster)
        @param page: page of the articles to return (1, 2, ...)
        @param count: number of articles to return per page (at most 200)
        @param sortBy: order in which articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
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



class RequestStoryArticleUris(RequestStory):
    """
    return a list of article uris
    """
    def __init__(self,
                 sortBy = "cosSim", sortByAsc = False  # order in which story articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to story centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 ):
        """
        return articles in the story (cluster)
        @param sortBy: order in which articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        """
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
