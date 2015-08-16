from ERBase import *
from ERReturnInfo import *

# query class for searching for events in the event registry 
class QueryEvent(Query):
    def __init__(self, eventUriOrList, **kwargs):
        super(QueryEvent, self).__init__();
        self._setVal("action", "getEvent");
        self._setVal("eventUri", eventUriOrList);    # a single event uri or a list of event uris
        
    def _getPath(self):
        return "/json/event";   

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestEvent):
        if not isinstance(requestEvent, RequestEvent):
            raise AssertionError("QueryEvent class can only accept result requests that are of type RequestEvent");
        self.resultTypeList.append(requestEvent);
                   

# #####################################
# #####################################
class RequestEvent:
    def __init__(self):
        self.resultType = None;
        
# return a list of event details
class RequestEventInfo(RequestEvent):
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))

# return a list of articles
class RequestEventArticles(RequestEvent):
    def __init__(self, page = 0, count = 20, 
                 lang = mainLangs, 
                 sortBy = "cosSim", sortByAsc = False,              # id, date, cosSim, fq, socialScore, facebookShares, twitterShares
                 returnInfo = ReturnInfo(articleMaxBodyLen = 200)):
        assert count <= 200
        self.resultType = "articles"
        self.articlesPage = page                # page of the articles
        self.articlesCount = count              # number of articles to return
        self.articlesLang = lang                # return articles in specified language(s)
        self.articlesSortBy = sortBy            # how are the event articles sorted (date, id, cosSim, fq)
        self.articlesSortByAsc = sortByAsc      
        self.__dict__.update(returnInfo.getParams("articles"))
        
# return a list of article uris
class RequestEventArticleUris(RequestEvent):
    def __init__(self, 
                 lang = mainLangs, 
                 sortBy = "cosSim", sortByAsc = False):
        self.articleUrisLang = lang
        self.articleUrisSortBy = sortBy          # id, date, cosSim, fq, socialScore, facebookShares, twitterShares
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"

# get keyword aggregate of articles in the event
class RequestEventKeywordAggr(RequestEvent):
    def __init__(self, eventSampleSize = 500):
        assert eventSampleSize <= 1000
        self.resultType = "keywordAggr"
        self.keywordAggrSampleSize = eventSampleSize
        
# get source distribution of articles in the event
class RequestEventSourceAggr(RequestEvent):
    def __init__(self):
        self.resultType = "sourceAggr"

# get distribution of date mentions found in the event articles
class RequestEventDateMentionAggr(RequestEvent):
    def __init__(self):
        self.resultType = "dateMentionAggr"
        
# get trending information for the articles about the event
class RequestEventArticleTrend(RequestEvent):
    def __init__(self, 
                 lang = mainLangs, 
                 minArticleCosSim = -1, 
                 returnInfo = ReturnInfo(articleMaxBodyLen = 0)):
        self.resultType = "articleTrend"
        self.articleTrendLang = lang
        self.articleTrendMinArticleCosSim = minArticleCosSim;
        self.__dict__.update(returnInfo.getParams("articleTrend"))

# get information about similar events
class RequestEventSimilarEvents(RequestEvent):
    def __init__(self, 
                 count = 20,                    # number of similar events to return
                 source = "concept",            # how to compute similarity ("concept", "cca")
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

# get information about similar stories (clusters)
class RequestEventSimilarStories(RequestEvent):
    def __init__(self, 
                 count = 20,                # number of similar stories to return
                 source = "concept",        # concept, cca - how to compute similarity
                 lang = ["eng"],            # in which language should be the stories
                 maxDayDiff = sys.maxint,   # what is the maximum time difference between the similar stories and this one
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "similarStories"
        self.similarStoriesCount = count                
        self.similarStoriesSource = source              
        self.similarStoriesLang = lang                   
        self.similarStoriesMaxDayDiff = maxDayDiff       
        self.__dict__.update(returnInfo.getParams("similarStories"))
