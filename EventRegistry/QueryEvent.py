from Base import *
from ReturnInfo import *

class QueryEvent(Query):
    """
    Class for obtaining available info for one or more events in the Event Registry 

    @param eventUriOrUriList: a single event uri or a list of event uris
    """
    def __init__(self, eventUriOrList):
        super(QueryEvent, self).__init__()
        self._setVal("action", "getEvent")
        self._setVal("eventUri", eventUriOrList)
        
    def _getPath(self):
        return "/json/event"   

    def addRequestedResult(self, requestEvent):
        """
        Add a result type that you would like to be returned.
        In one QueryEvent you can ask for multiple result types.
        Result types can be the classes that extend RequestEvent base class (see classes below).
        """
        assert isinstance(requestEvent, RequestEvent), "QueryEvent class can only accept result requests that are of type RequestEvent"
        self.resultTypeList.append(requestEvent)
                   

class RequestEvent:
    def __init__(self):
        self.resultType = None
        
class RequestEventInfo(RequestEvent):
    """
    return details about an event
    """
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))

class RequestEventArticles(RequestEvent):
    """
    return articles about the event
    """
    def __init__(self, 
                 page = 0,              # page of the articles
                 count = 20,            # number of articles to return
                 lang = mainLangs,      # return articles in specified language(s)
                 sortBy = "cosSim", sortByAsc = False,              # order in which event articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))):
        assert count <= 200
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesLang = lang
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))
        
class RequestEventArticleUris(RequestEvent):
    """
    return a list of article uris
    """
    def __init__(self, 
                 lang = mainLangs, 
                 sortBy = "cosSim", sortByAsc = False  # order in which event articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), socialScore (total shares in social media), facebookShares (shares on fb), twitterShares (shares on twitter)
                 ):
        self.articleUrisLang = lang
        self.articleUrisSortBy = sortBy          
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"

class RequestEventKeywordAggr(RequestEvent):
    """
    return keyword aggregate (tag-cloud) from articles in the event
    """
    def __init__(self, eventSampleSize = 500):
        assert eventSampleSize <= 1000
        self.resultType = "keywordAggr"
        self.keywordAggrSampleSize = eventSampleSize
        
class RequestEventSourceAggr(RequestEvent):
    """
    get news source distribution of articles in the event
    """
    def __init__(self):
        self.resultType = "sourceAggr"

class RequestEventDateMentionAggr(RequestEvent):
    """
    get date that we found mentioned in the event articles
    """
    def __init__(self):
        self.resultType = "dateMentionAggr"
        
class RequestEventArticleTrend(RequestEvent):
    """
    return trending information for the articles about the event
    """
    def __init__(self, 
                 lang = mainLangs, 
                 minArticleCosSim = -1, 
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))):
        self.resultType = "articleTrend"
        self.articleTrendLang = lang
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update(returnInfo.getParams("articleTrend"))


class RequestEventSimilarEvents(RequestEvent):
    """
    return a list of similar events
    """
    def __init__(self, 
                 count = 20,                    # number of similar events to return
                 source = "concept",            # how to compute similarity. Options: concept cca
                 maxDayDiff = sys.maxint,       # what is the maximum time difference between the similar events and this one
                 addArticleTrendInfo = False,   # add info how the articles in the similar events are distributed over time
                 aggrHours = 6,                 # if similarEventsAddArticleTrendInfo == True then this is the aggregating window
                 includeSelf = False,           # should the info about the event itself be included among the results
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "similarEvents"
        self.similarEventsCount = count                 
        self.similarEventsSource = source               
        self.similarEventsMaxDayDiff = maxDayDiff       
        self.similarEventsAddArticleTrendInfo = addArticleTrendInfo     
        self.similarEventsAggrHours = aggrHours
        self.similarEventsIncludeSelf = includeSelf                     
        self.__dict__.update(returnInfo.getParams("similarEvents"))

class RequestEventSimilarStories(RequestEvent):
    """
    return a list of similar stories (clusters)
    """
    def __init__(self, 
                 count = 20,                # number of similar stories to return
                 source = "concept",        # how to compute similarity. Options: concept, cca
                 lang = ["eng"],            # in which language should be the similar stories
                 maxDayDiff = sys.maxint,   # what is the maximum time difference between the similar stories and this one
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "similarStories"
        self.similarStoriesCount = count                
        self.similarStoriesSource = source              
        self.similarStoriesLang = lang                   
        self.similarStoriesMaxDayDiff = maxDayDiff       
        self.__dict__.update(returnInfo.getParams("similarStories"))
