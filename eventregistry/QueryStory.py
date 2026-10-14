import datetime
import json
from eventregistry.Base import Query, QueryParamsBase, mainLangs
from eventregistry.ReturnInfo import ArticleInfoFlags, ReturnInfo
from typing import Union, List

# the names exported by "from eventregistry import *"
__all__ = ["QueryStory", "RequestStory", "RequestStoryInfo", "RequestStoryArticles", "RequestStoryArticleUris",
           "RequestStoryArticleTrend", "RequestStorySimilarStories"]


class QueryStory(Query):
    """
    Class for obtaining available info for one or more stories (clusters) in the Event Registry
    NOTE: Story in our terminology is a cluster of articles (and not a single article). An event is
    then something that consists of one or more stories (typically in different languages).

    Args:
        storyUriOrList: a single story uri or a list of story uris
    """
    def __init__(self, storyUriOrList: Union[str, List[str], None] = None):
        super().__init__()
        self._setVal("action", "getStory")
        if storyUriOrList is not None:
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
        if not (isinstance(requestStory, RequestStory)):
            raise TypeError("QueryStory class can only accept result requests that are of type RequestStory")
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
    def __init__(self, returnInfo: Union[ReturnInfo, None] = None):
        super().__init__()
        self.resultType = "info"
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("info"))



class RequestStoryArticles(RequestStory):
    """
    return articles about the story
    """
    def __init__(self,
                 page: int = 1,
                 count: int = 100,
                 sortBy: str = "cosSim", sortByAsc: bool = False,
                 returnInfo: Union[ReturnInfo, None] = None):
        """
        return articles in the story (cluster)

        Args:
            page: page of the articles to return (1, 2, ...)
            count: number of articles to return per page (at most 100)
            sortBy: order in which articles are sorted. Options: date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (page >= 1):
            raise ValueError("page has to be >= 1")
        if not (count <= 100):
            raise ValueError("count should be at most 100")
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))).getParams("articles"))



class RequestStoryArticleUris(RequestStory):
    """
    return a list of article uris
    """
    def __init__(self,
                 sortBy: str = "cosSim", sortByAsc: bool = False  # order in which story articles are sorted. Options: date (published date), cosSim (closeness to story centroid)
                 ):
        """
        return articles in the story (cluster)

        Args:
            sortBy: order in which articles are sorted. Options: date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        """
        super().__init__()
        self.articleUrisSortBy = sortBy
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"



class RequestStoryArticleTrend(RequestStory):
    """
    return trending information for the articles about the story
    """
    def __init__(self,
                 lang: Union[str, List[str], None] = None,
                 minArticleCosSim: float = -1,
                 returnInfo: Union[ReturnInfo, None] = None):
        super().__init__()
        self.resultType = "articleTrend"
        self.articleTrendLang = lang if lang is not None else mainLangs
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))).getParams("articleTrend"))



class RequestStorySimilarStories(RequestStory):
    def __init__(self,
                conceptInfoList: List[dict],
                count: int = 50,
                dateStart: Union[datetime.date, str, None] = None,
                dateEnd: Union[datetime.date, str, None] = None,
                lang: Union[str, List[str], None] = None,
                returnInfo: Union[ReturnInfo, None] = None):
        """
        compute and return a list of similar stories

        Args:
            conceptInfoList: list of concepts and their importance, e.g. [{ "uri": "http://en.wikipedia.org/wiki/Barack_Obama", "wgt": 100 }, ...]
            count: number of similar stories to return (at most 50)
            dateStart: what can be the oldest date of the similar stories
            dateEnd: what can be the newest date of the similar stories
            lang: in which language(s) should be the similar stories
            returnInfo: what details should be included in the returned information
        """
        super().__init__()
        if not (count <= 50):
            raise ValueError("count should be at most 50")
        if not (isinstance(conceptInfoList, list)):
            raise TypeError("conceptInfoList should be of type list")
        lang = lang if lang is not None else []
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
        self.__dict__.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("similarStories"))
