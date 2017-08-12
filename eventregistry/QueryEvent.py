import six
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.QueryArticle import QueryArticle, RequestArticleInfo


class QueryEvent(Query):
    """
    Class for obtaining available info for one or more events in the Event Registry
    """
    def __init__(self,
                 eventUriOrList,
                 requestedResult = None):
        """
        @param eventUriOrUriList: a single event uri or a list of event uris
        @param requestedResult: the information to return as the result of the query. By default return the details of the event
        """
        super(QueryEvent, self).__init__()
        self._setVal("action", "getEvent")
        self._setVal("eventUri", eventUriOrList)
        self.setRequestedResult(requestedResult or RequestEventInfo())


    def _getPath(self):
        return "/json/event"


    def addRequestedResult(self, requestEvent):
        """
        Add a result type that you would like to be returned.
        In case you are a subscribed customer you can ask for multiple result types in a single query (for free users, only a single result type can be required per call).
        Result types can be the classes that extend RequestEvent base class (see classes below).
        """
        assert isinstance(requestEvent, RequestEvent), "QueryEvent class can only accept result requests that are of type RequestEvent"
        self.resultTypeList = [item for item in self.resultTypeList if item.getResultType() != requestEvent.getResultType()]
        self.resultTypeList.append(requestEvent)


    def setRequestedResult(self, requestEvent):
        """
        Set the single result type that you would like to be returned. Any previously set result types will be overwritten.
        Result types can be the classes that extend RequestEvent base class (see classes below).
        """
        assert isinstance(requestEvent, RequestEvent), "QueryEvent class can only accept result requests that are of type RequestEvent"
        self.resultTypeList = [requestEvent]



class QueryEventArticlesIter(QueryEvent, six.Iterator):
    """
    Class for obtaining an iterator over all articles in the event
    """
    def __init__(self, eventUri):
        """@param eventUri: a single event for which we want to obtain the list of articles in it"""
        super(QueryEventArticlesIter, self).__init__(eventUri)


    def count(self, eventRegistry,
              lang = mainLangs):
        """
        return the number of articles that match the criteria
        @param eventRegistry: instance of EventRegistry class. used to obtain the necessary data
        @param lang: array or a single language in which to return the list of matching articles
        """
        self.setRequestedResult(RequestEventArticleUris(lang = lang))
        res = eventRegistry.execQuery(self)
        if "error" in res:
            print(res["error"])
        count = len(res.get(self.queryParams["eventUri"], {}).get("articleUris", {}).get("results", []))
        return count


    def execQuery(self, eventRegistry,
            lang = mainLangs,
            sortBy = "cosSim", sortByAsc = False,
            returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200)),
            articleBatchSize = 200,
            maxItems = -1):
        """
        @param eventRegistry: instance of EventRegistry class. used to obtain the necessary data
        @param lang: array or a single language in which to return the list of matching articles
        @param sortBy: order in which event articles are sorted. Options: none (no specific sorting), id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        @param articleBatchSize: number of articles to download at once (we are not downloading article by article) (at most 200)
        @param maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out
        """
        assert articleBatchSize <= 200, "You can not have a batch size > 200 items"
        self._er = eventRegistry
        self._lang = lang
        self._sortBy = sortBy
        self._sortByAsc = sortByAsc
        self._returnInfo = returnInfo
        self._articleBatchSize = articleBatchSize
        # if we want to return only a subset of items:
        self._maxItems = maxItems
        self._currItem = 0
        # download the list of article uris
        self._articleList = []
        self.setRequestedResult(RequestEventArticleUris(lang = self._lang, sortBy = self._sortBy, sortByAsc = self._sortByAsc))
        res = self._er.execQuery(self)
        if "error" in res:
            print(res["error"])
        self._uriList = res.get(self.queryParams["eventUri"], {}).get("articleUris", {}).get("results", [])
        return self


    def _getNextArticleBatch(self):
        """download next batch of events based on the event uris in the uri list"""
        self.clearRequestedResults()
        # if no uris, then we have nothing to download
        if len(self._uriList) == 0:
            return
        # get uris to download
        uris = self._uriList[:self._articleBatchSize]
        if self._er._verboseOutput:
            print("Downoading %d articles from event %s" % (len(uris), self.queryParams["eventUri"]))
        # remove used uris
        self._uriList = self._uriList[self._articleBatchSize:]
        q = QueryArticle(uris)
        q.setRequestedResult(RequestArticleInfo(self._returnInfo))
        res = self._er.execQuery(q)
        if "error" in res:
            print(res["error"])
        arts = [ res[key]["info"] for key in uris if key in res and "info" in res[key]]
        self._articleList.extend(arts)


    def __iter__(self):
        # clear any past info - iterator should start from beginning
        return self


    def __next__(self):
        """iterate over the available events"""
        self._currItem += 1
        # if we want to return only the first X items, then finish once reached
        if self._maxItems >= 0 and self._currItem > self._maxItems:
            raise StopIteration
        if len(self._articleList) == 0:
            self._getNextArticleBatch()
        if len(self._articleList) > 0:
            return self._articleList.pop(0)
        raise StopIteration



class RequestEvent:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestEventInfo(RequestEvent):
    def __init__(self, returnInfo = ReturnInfo()):
        """
        return details about an event
        """
        self.resultType = "info"
        self.__dict__.update(returnInfo.getParams("info"))



class RequestEventArticles(RequestEvent):
    def __init__(self,
                 page = 1,
                 count = 20,
                 lang = mainLangs,
                 sortBy = "cosSim", sortByAsc = False,
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200))):
        """
        return articles about the event
        @param page: page of the articles to return (1, 2, ...)
        @param count: number of articles to return per page (at most 200)
        @param lang: a single lanugage or a list of languages in which to return the articles
        @param sortBy: order in which event articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 200, "at most 200 articles can be returned per call"
        self.resultType = "articles"
        self.articlesPage = page
        self.articlesCount = count
        self.articlesLang = lang
        self.articlesSortBy = sortBy
        self.articlesSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("articles"))



class RequestEventArticleUris(RequestEvent):
    def __init__(self,
                 lang = mainLangs,
                 sortBy = "cosSim", sortByAsc = False  # order in which event articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), socialScore (total shares in social media)
                 ):
        """
        return just a list of article uris
        @param lang: a single lanugage or a list of languages in which to return the articles
        @param sortBy: order in which event articles are sorted. Options: id (internal id), date (published date), cosSim (closeness to event centroid), sourceImportanceRank (importance of the news source, custom set), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares in social media)
        @param sortByAsc: should the articles be sorted in ascending order (True) or descending (False) based on sortBy value
        """
        self.articleUrisLang = lang
        self.articleUrisSortBy = sortBy
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"



class RequestEventKeywordAggr(RequestEvent):
    def __init__(self, lang = "eng"):        # the lang parameter should match one of the languages for which we have articles in the event.
        """
        return keyword aggregate (tag-cloud) from articles in the event
        @param lang: language for which to compute the keywords
        """
        self.resultType = "keywordAggr"
        self.keywordAggrLang = lang



class RequestEventSourceAggr(RequestEvent):
    def __init__(self):
        """
        get news source distribution of articles in the event
        """
        self.resultType = "sourceExAggr"



class RequestEventDateMentionAggr(RequestEvent):
    def __init__(self):
        """
        get dates that we found mentioned in the event articles and their frequencies
        """
        self.resultType = "dateMentionAggr"



class RequestEventArticleTrend(RequestEvent):
    def __init__(self,
                 lang = mainLangs,
                 page = 1, count = 200,
                 minArticleCosSim = -1,
                 returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 0))):
        """
        return trending information for the articles about the event
        @param lang: languages for which to compute the trends
        @param page: page of the articles for which to return information (1, 2, ...)
        @param count: number of articles returned per page (at most 200)
        @param minArticleCosSim: ignore articles that have cos similarity to centroid lower than the specified value (-1 for no limit)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 200, "at most 200 articles can be returned per call"
        self.resultType = "articleTrend"
        self.articleTrendLang = lang
        self.articleTrendPage = page
        self.articleTrendCount = count
        self.articleTrendMinArticleCosSim = minArticleCosSim
        self.__dict__.update(returnInfo.getParams("articleTrend"))



class RequestEventSimilarEvents(RequestEvent):
    def __init__(self,
                 count = 20,                    #
                 maxDayDiff = sys.maxsize,       # what is the maximum time difference between the similar events and this one
                 addArticleTrendInfo = False,   # add info how the articles in the similar events are distributed over time
                 aggrHours = 6,                 # if similarEventsAddArticleTrendInfo == True then this is the aggregating window
                 includeSelf = False,           # should the info about the event itself be included among the results
                 returnInfo = ReturnInfo()):
        """
        compute and return a list of similar events
        @param count: number of similar events to return (at most 200)
        @param maxDayDiff: find only those events that are at most maxDayDiff days apart from the tested event
        @param addArticleTrendInfo: for the returned events compute how they were trending (intensity of reporting) in different time periods
        @param aggrHours: time span that is used as a unit when computing the trending info
        @param includeSel: include also the tested event in the results (True or False)
        @param returnInfo: what details should be included in the returned information
        """
        assert count <= 200
        self.resultType = "similarEvents"
        self.similarEventsCount = count
        if maxDayDiff != sys.maxsize:
            self.similarEventsMaxDayDiff = maxDayDiff
        self.similarEventsAddArticleTrendInfo = addArticleTrendInfo
        self.similarEventsAggrHours = aggrHours
        self.similarEventsIncludeSelf = includeSelf
        self.__dict__.update(returnInfo.getParams("similarEvents"))



class RequestEventSimilarStories(RequestEvent):
    def __init__(self,
                 count = 20,                # number of similar stories to return
                 source = "concept",        # how to compute similarity. Options: concept, cca
                 lang = ["eng"],            # in which language should be the similar stories
                 maxDayDiff = sys.maxsize,   # what is the maximum time difference between the similar stories and this one
                 returnInfo = ReturnInfo()):
        """
        return a list of similar stories (clusters)
        @param count: number of similar stories to return (at most 200)
        @param source: show is the similarity with other stories computed. Using concepts ('concepts') or CCA ('cca').
        @param lang: in what language(s) should be the returned stories
        @param maxDayDiff: maximum difference in days between the returned stories and the tested event
        @param returnInfo: what details should be included in the returned information
        """
        assert count <= 200
        self.resultType = "similarStories"
        self.similarStoriesCount = count
        self.similarStoriesSource = source
        self.similarStoriesLang = lang
        if maxDayDiff != sys.maxsize:
            self.similarStoriesMaxDayDiff = maxDayDiff
        self.__dict__.update(returnInfo.getParams("similarStories"))
