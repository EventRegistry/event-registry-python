from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List


class QueryStory(Query):
    """
    Class for obtaining available info for one or more stories (clusters) in the Event Registry
    NOTE: Story in our terminology is a cluster of articles (and not a single article). An event is
    then something that consists of one or more stories (typically in different languages).

    @param storyUriOrList: a single story uri or a list of story uris
    """
    def __init__(self, storyUriOrList: Union[str, List[str], None] = None):
        super(QueryStory, self).__init__()
        self._setVal("action", "getStory")
        if storyUriOrList != None:
            self.queryByUri(storyUriOrList)


    def _getPath(self):
        return "/api/v1/story"


    def queryByUri(self, uriOrUriList: Union[str, List[str]]):
        """search stories by their uri(s)"""
        self._setVal("storyUri", uriOrUriList)


    def setRequestedResult(self, requestStory: "RequestStory"):
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
    def __init__(self, returnInfo: ReturnInfo = ReturnInfo()):
        super(RequestStory, self).__init__()
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))



class RequestStoryArticles(RequestStory):
    """
    return articles about the story
    """
    def __init__(self,
                 page: int = 1,
                 count: int = 100,
                 sortBy: str = "cosSim", sortByAsc: bool = False,
                 returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))):
        """
        return articles in the story (cluster)
        @param page: page of the articles to return (1, 2, ...)
        @param count: number of articles to return per page (at most 100)
        @param sortBy: order in which articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        @param returnInfo: what details should be included in the returned information
        """
        super(RequestStory, self).__init__()
        assert page >= 1, "page has to be >= 1"
        assert count <= 100
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
                 sortBy: str = "cosSim", sortByAsc: bool = False  # order in which story articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to story centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 ):
        """
        return articles in the story (cluster)
        @param sortBy: order in which articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        """
        super(RequestStory, self).__init__()
        self.articleUrisSortBy = sortBy
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"



class RequestStoryArticleTrend(RequestStory):
    """
    return trending information for the articles about the story
    """
    def __init__(self,
                 lang: Union[str, List[str]] = mainLangs,
                 minArticleCosSim: float = -1,
                 returnInfo: ReturnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))):
        super(RequestStory, self).__init__()
        self.resultType = "articleTrend"
        self.articleTrendLang = lang
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update(returnInfo.getParams("articleTrend"))



class RequestStorySimilarStories(RequestStory):
    """
        compute and return a list of similar stories
        @param conceptInfoList: array of concepts and their importance, e.g. [{ "uri": "http://en.wikipedia.org/wiki/Barack_Obama", "wgt": 100 }, ...]
        @param count: number of similar stories to return (at most 50)
        @param dateStart: what can be the oldest date of the similar stories
        @param dateEnd: what can be the newest date of the similar stories
        @param addArticleTrendInfo: for the returned stories compute how they were trending (intensity of reporting) in different time periods
        @param aggrHours: time span that is used as a unit when computing the trending info
        @param returnInfo: what details should be included in the returned information
        """
    def __init__(self,
                conceptInfoList: Union[str, List[str]],
                count: int = 50,                                          # number of similar stories to return
                dateStart: Union[datetime.date, str, None] = None,        # what can be the oldest date of the similar stories
                dateEnd: Union[datetime.date, str, None] = None,          # what can be the newest date of the similar stories
                lang: Union[str, List[str]] = [],
                returnInfo: ReturnInfo = ReturnInfo()):
        super(RequestStory, self).__init__()
        assert count <= 50
        assert isinstance(conceptInfoList, list)
        self.action = "getSimilarStories"
        self.concepts = json.dumps(conceptInfoList)
        self.storiesCount = count
        if dateStart is not None:
            self.dateStart = QueryParamsBase.encodeDate(dateStart)
        if dateEnd is not None:
            self.dateEnd = QueryParamsBase.encodeDate(dateEnd)
        if len(lang) > 0:
            self.lang = lang
        # setting resultType since we have to, but it's actually ignored on the backend
        self.resultType = "similarStories"
        self.__dict__.update(returnInfo.getParams("similarStories"))
