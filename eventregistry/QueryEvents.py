import six, json
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.Query import *


class QueryEvents(Query):
    """
    Query class for searching for events in the Event Registry.
    The resulting events have to match all specified conditions. If a parameter value equals "" or [], then it is ignored.
    In order for query to be valid, it has to have at least one positive condition (condition that does not start with ignore*).

    @param keywords: find events where articles mention all the specified keywords.
        In case of multiple keywords, separate them with space. Example: "apple iphone".
    @param conceptUri: find events where the concept with concept uri is important.
        A single concept uri can be provided as a string, multiple concept uris can be provided as a list of strings.
        If multiple concept uris are provided, resulting events have to be about *all* of them.
        To obtain a concept uri using a concept label use EventRegistry.getConceptUri().
    @param sourceUri: find events that contain one or more articles that have been written by a news source sourceUri.
        If multiple sources are provided, resulting events have to be contain articles from *all* provided sources.
        Source uri for a given news source name can be obtained using EventRegistry.getNewsSourceUri().
    @param locationUri: find events that occured at a particular location. Location uri can either be a city or a country.
        If multiple locations are provided, resulting events have to match *any* of the locations.
        Location uri for a given name can be obtained using EventRegistry.getLocationUri().
    @param categoryUri: find events that are assigned into a particular category.
        If multiple categories are provided, resulting events have to be assigned to *any* of the categories.
        A category uri can be obtained from a category name using EventRegistry.getCategoryUri().
    @param lang: find events for which we found articles in the specified language.
        If more than one language is specified, resulting events has to be reported in *any* of the languages.
    @param dateStart: find events that occured on or after dateStart. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
    @param dateEnd: find events that occured before or on dateEnd. Date should be provided in YYYY-MM-DD format, datetime.time or datetime.datetime.
    @param minArticlesInEvent: find events that have been reported in at least minArticlesInEvent articles (regardless of language)
    @param maxArticlesInEvent: find events that have not been reported in more than maxArticlesInEvent articles (regardless of language)
    @param dateMentionStart: find events where articles explicitly mention a date that is equal or greater than dateMentionStart.
    @param dateMentionEnd: find events where articles explicitly mention a date that is lower or equal to dateMentionEnd.
    @param ignoreKeywords: ignore events where articles about the event mention any of the provided keywords
    @param ignoreConceptUri: ignore events that are about any of the provided concepts
    @param ignoreLang: ignore events that are reported in any of the provided languages
    @param ignoreLocationUri: ignore events that occured in any of the provided locations. A location can be a city or a place
    @param ignoreSourceUri: ignore events that have have articles which have been written by any of the specified news sources
    @param categoryIncludeSub: when a category is specified using categoryUri, should also all subcategories be included?
    @param ignoreCategoryIncludeSub: when a category is specified using ignoreCategoryUri, should also all subcategories be included?
    @param conceptOper: Boolean operator to use in cases when multiple concepts are specified. Possible values are:
            "AND" if all concepts should be mentioned in the resulting events
            "OR" if any of the concept should be mentioned in the resulting events
    @param requestedResult: the information to return as the result of the query. By default return the list of matching events
    """
    def __init__(self,
                 keywords = "",
                 conceptUri = [],
                 sourceUri = [],
                 locationUri = [],
                 categoryUri = [],
                 lang = [],
                 dateStart = "",
                 dateEnd = "",
                 minArticlesInEvent = 0,
                 maxArticlesInEvent = sys.maxsize,
                 dateMentionStart = "",
                 dateMentionEnd = "",
                 ignoreKeywords = "",
                 ignoreConceptUri = [],
                 ignoreLocationUri = [],
                 ignoreSourceUri = [],
                 ignoreCategoryUri = [],
                 ignoreLang = [],
                 categoryIncludeSub = True,
                 ignoreCategoryIncludeSub = True,
                 conceptOper = "AND",
                 requestedResult = None):
        super(QueryEvents, self).__init__()

        self._setVal("action", "getEvents")

        self._setValIfNotDefault("keywords", keywords, "")         # e.g. "bla bla"
        self._setValIfNotDefault("conceptUri", conceptUri, [])     # e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"]
        self._setValIfNotDefault("sourceUri", sourceUri, [])       # ["www.bbc.co.uk"]
        self._setValIfNotDefault("locationUri", locationUri, [])   # ["http://en.wikipedia.org/wiki/Ljubljana"]
        self._setValIfNotDefault("categoryUri", categoryUri, [])   # ["http://www.dmoz.org/Science/Astronomy"]
        self._setValIfNotDefault("lang", lang, [])                 # eng, deu, spa, zho, slv, ...
        if (dateStart != ""):
            self._setDateVal("dateStart", dateStart)   # 2014-05-02
        if (dateEnd != ""):
            self._setDateVal("dateEnd", dateEnd)       # 2014-05-02
        self._setValIfNotDefault("minArticlesInEvent", minArticlesInEvent, 0)
        self._setValIfNotDefault("maxArticlesInEvent", maxArticlesInEvent, sys.maxsize)
        if (dateMentionStart != ""):
            self._setDateVal("dateMentionStart", dateMentionStart)    # e.g. 2014-05-02
        if (dateMentionEnd != ""):
            self._setDateVal("dateMentionEnd", dateMentionEnd)        # e.g. 2014-05-02

        self._setValIfNotDefault("ignoreKeywords", ignoreKeywords, "")
        self._setValIfNotDefault("ignoreConceptUri", ignoreConceptUri, [])
        self._setValIfNotDefault("ignoreLocationUri", ignoreLocationUri, [])
        self._setValIfNotDefault("ignoreSourceUri", ignoreSourceUri, [])
        self._setValIfNotDefault("ignoreCategoryUri", ignoreCategoryUri, [])
        self._setValIfNotDefault("ignoreLang", ignoreLang, [])

        self._setValIfNotDefault("categoryIncludeSub", categoryIncludeSub, True)
        self._setValIfNotDefault("ignoreCategoryIncludeSub", ignoreCategoryIncludeSub, True)
        self._setValIfNotDefault("conceptOper", conceptOper, "AND")

        self.addRequestedResult(requestedResult or RequestEventsInfo())


    def _getPath(self):
        return "/json/event"


    def addConcept(self, conceptUri):
        self._addArrayVal("conceptUri", conceptUri)


    def addLocation(self, locationUri):
        self._addArrayVal("locationUri", locationUri)


    def addCategory(self, categoryUri):
        self._addArrayVal("categoryUri", categoryUri)


    def addNewsSource(self, newsSourceUri):
        self._addArrayVal("sourceUri", newsSourceUri)


    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams.pop("keywords", "") + " " + keyword


    def setEventUriList(self, uriList):
        """
        Set a custom list of event uris. The results will be then computed on this list - no query
        will be done (all conditions will be ignored).
        """
        assert isinstance(uriList, list), "uriList has to be a list of strings that represent event uris"
        self.queryParams = { "action": "getEvents", "eventUriList": ",".join(uriList) }


    def setDateLimit(self, startDate, endDate):
        self._setDateVal("dateStart", startDate)
        self._setDateVal("dateEnd", endDate)


    def addRequestedResult(self, requestEvents):
        """
        Add a result type that you would like to be returned.
        In one QueryEvents you can ask for multiple result types.
        Result types can be the classes that extend RequestEvents base class (see classes below).
        """
        assert isinstance(requestEvents, RequestEvents), "QueryEvents class can only accept result requests that are of type RequestEvents"
        self.resultTypeList = [item for item in self.resultTypeList if item.getResultType() != requestEvents.getResultType()]
        self.resultTypeList.append(requestEvents)


    def setRequestedResult(self, requestEvents):
        """
        Set the single result type that you would like to be returned. If some other request type was previously set, it will be overwritten.
        Result types can be the classes that extend RequestEvents base class (see classes below).
        """
        assert isinstance(requestEvents, RequestEvents), "QueryEvents class can only accept result requests that are of type RequestEvents"
        self.resultTypeList = [requestEvents]


    @staticmethod
    def initWithEventUriList(uriList):
        q = QueryEvents()
        q.setEventUriList(uriList)
        return q


    @staticmethod
    def initWithComplexQuery(query):
        q = QueryEvents()
        # provided an instance of ComplexEventQuery
        if isinstance(query, ComplexEventQuery):
            q._setVal("query", json.dumps(query.getQuery()))
        # provided query as a string containing the json object
        elif isinstance(query, six.string_types):
            foo = json.loads(query)
            q._setVal("query", query)
        # provided query as a python dict
        elif isinstance(query, dict):
            q._setVal("query", json.dumps(query))
        # unrecognized value provided
        else:
            assert False, "The instance of query parameter was not a ComplexEventQuery, a string or a python dict"
        return q



class QueryEventsIter(QueryEvents, six.Iterator):
    """
    class that simplifies and combines functionality from QueryEvents and RequestEventsInfo. It provides an iterator
    over the list of events that match the specified conditions
    """

    def count(self, eventRegistry):
        """
        return the number of events that match the criteria
        """
        self.setRequestedResult(RequestEventsUriList())
        res = eventRegistry.execQuery(self)
        if "error" in res:
            print(res["error"])
        count = res.get("uriList", {}).get("totalResults", 0)
        return count


    def execQuery(self, eventRegistry,
                  sortBy = "rel",
                  sortByAsc = False,
                  returnInfo = ReturnInfo(),
                  eventBatchSize = 200,
                  maxItems = -1):
        """
        @param eventRegistry: instance of EventRegistry class. used to query new event list and uris
        @param sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), socialScore (amount of shares in social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param eventBatchSize: number of events to download at once (we are not downloading event by event)
        @param maxItems: maximum number of items to be returned. Used to stop iteration sooner than results run out
        """
        assert eventBatchSize <= 200, "You can not have a batch size > 200 items"
        self._er = eventRegistry
        self._sortBy = sortBy
        self._sortByAsc = sortByAsc
        self._returnInfo = returnInfo
        self._eventBatchSize = eventBatchSize
        self._uriPage = 0
        # if we want to return only a subset of items:
        self._maxItems = maxItems
        self._currItem = 0
        # list of cached events that are yet to be returned by the iterator
        self._eventList = []
        self._uriList = []
        # how many pages do we have for URIs. set once we call _getNextUriPage first
        self._allUriPages = None
        return self


    @staticmethod
    def initWithComplexQuery(query):
        assert isinstance(query, ComplexEventQuery), "The instance of query parameter should be of instance ComplexEventQuery"
        q = QueryEventsIter()
        q._setVal("query", json.dumps(query.getQuery()))
        return q


    def _getNextUriPage(self):
        """download a simple list of event uris"""
        self._uriPage += 1
        self._uriList = []
        if self._allUriPages != None and self._uriPage > self._allUriPages:
            return
        if self._er._verboseOutput:
            print("Downoading page %d of event uris" % (self._uriPage))
        self.setRequestedResult(RequestEventsUriList(page = self._uriPage, sortBy = self._sortBy, sortByAsc = self._sortByAsc))
        res = self._er.execQuery(self)
        if "error" in res:
            print(res["error"])
        self._uriList = res.get("uriList", {}).get("results", [])
        self._allUriPages = res.get("uriList", {}).get("pages", 0)
        self._getNextEventBatch()


    def _getNextEventBatch(self):
        """download next batch of events based on the event uris in the uri list"""
        self.clearRequestedResults()
        # try to get more uris, if none
        if len(self._uriList) == 0:
            self._getNextUriPage()
        # if still no uris, then we have nothing to download
        if len(self._uriList) == 0:
            return
        # get uris to download
        uris = self._uriList[:self._eventBatchSize]
        # remove used uris
        self._uriList = self._uriList[self._eventBatchSize:]
        if self._er._verboseOutput:
            print("Downoading %d events..." % (len(uris)))
        q = QueryEvents.initWithEventUriList(uris)
        q.setRequestedResult(RequestEventsInfo(page = 1, count = self._eventBatchSize, sortBy = "none", returnInfo = self._returnInfo))
        res = self._er.execQuery(q)
        if "error" in res:
            print("Error while obtaining a list of events: " + res["error"])
        else:
            assert res.get("events", {}).get("pages", 0) == 1
        self._eventList.extend(res.get("events", {}).get("results", []))


    def __iter__(self):
        return self


    def __next__(self):
        """iterate over the available events"""
        self._currItem += 1
        # if we want to return only the first X items, then finish once reached
        if self._maxItems >= 0 and self._currItem > self._maxItems:
            raise StopIteration
        if len(self._eventList) == 0:
            self._getNextEventBatch()
        if len(self._eventList) > 0:
            return self._eventList.pop(0)
        raise StopIteration



class RequestEvents:
    def __init__(self):
        self.resultType = None


    def getResultType(self):
        return self.resultType



class RequestEventsInfo(RequestEvents):
    def __init__(self, page = 1,
                 count = 20,
                 sortBy = "rel", sortByAsc = False,
                 returnInfo = ReturnInfo()):
        """
        return event details for resulting events
        @param page: page of the results to return (1, 2, ...)
        @param count: number of results to return per page (at most 200)
        @param sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), socialScore (amount of shares in social media)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 200
        self.resultType = "events"
        self.eventsPage = page
        self.eventsCount = count
        self.eventsSortBy = sortBy
        self.eventsSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("events"))


    def setPage(self, page):
        assert page >= 1, "page has to be >= 1"
        self.eventsPage = page


    def setCount(self, count):
        self.eventsCount = count



class RequestEventsUriList(RequestEvents):
    def __init__(self,
                 page = 1,
                 count = 100000,
                 sortBy = "rel", sortByAsc = False):
        """
        return a simple list of event uris for resulting events
        @param page: page of the results (1, 2, ...)
        @param count: number of results to include per page (at most 300000)
        @param sortBy: how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), socialScore (amount of shares in social media)
        @param sortByAsc: should the events be sorted in ascending order (True) or descending (False)
        """
        assert page >= 1, "page has to be >= 1"
        assert count <= 300000
        self.resultType = "uriList"
        self.uriListPage = page
        self.uriListCount = count
        self.uriListSortBy = sortBy
        self.uriListSortByAsc = sortByAsc

    def setPage(self, page):
        assert page >= 1, "page has to be >= 1"
        self.uriListPage = page

    def setCount(self, count):
        self.uriListCount = count


class RequestEventsTimeAggr(RequestEvents):
    def __init__(self):
        """
        return time distribution of resulting events
        """
        self.resultType = "timeAggr"


class RequestEventsKeywordAggr(RequestEvents):
    def __init__(self, lang = "eng"):
        """
        return keyword aggregate (tag cloud) on words in articles in resulting events
        @param lang: in which language to produce the list of top keywords
        """
        self.resultType = "keywordAggr"
        self.keywordAggrLang = lang


class RequestEventsLocAggr(RequestEvents):
    def __init__(self,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        return aggreate of locations of resulting events
        @param eventsSampleSize: sample of events to use to compute the location aggregate (at most 300000)
        @param returnInfo: what details (about locations) should be included in the returned information
        """
        assert eventsSampleSize <= 300000
        self.resultType = "locAggr"
        self.locAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("locAggr"))


class RequestEventsLocTimeAggr(RequestEvents):

    def __init__(self,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        return aggreate of locations and times of resulting events
        @param eventsSampleSize: sample of events to use to compute the location aggregate (at most 300000)
        @param returnInfo: what details (about locations) should be included in the returned information
        """
        assert eventsSampleSize <= 300000
        self.resultType = "locTimeAggr"
        self.locTimeAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("locTimeAggr"))


class RequestEventsConceptAggr(RequestEvents):
    def __init__(self,
                 conceptCount = 20,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        compute which concept are the most frequently occuring in the list of resulting events
        @param conceptCount: number of top concepts to return (at most 200)
        @param eventsSampleSize: on what sample of results should the aggregate be computed (at most 3000000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 200
        assert eventsSampleSize <= 3000000
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptAggr"))


class RequestEventsConceptGraph(RequestEvents):
    def __init__(self,
                 conceptCount = 25,
                 linkCount = 50,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        compute which concept pairs frequently co-occur together in the resulting events
        @param conceptCount: number of top concepts to return (at most 1000)
        @param linkCount: number of links between the concepts to return (at most 2000)
        @param eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 1000
        assert linkCount <= 2000
        assert eventsSampleSize <= 300000
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptGraph"))


class RequestEventsConceptMatrix(RequestEvents):
    def __init__(self,
                 conceptCount = 25,
                 measure = "pmi",
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        get a matrix of concepts and their dependencies. For individual concept pairs
        return how frequently they co-occur in the resulting events and
        how "surprising" this is, based on the frequency of individual concepts
        @param conceptCount: number of top concepts to return (at most 200)
        @param measure: how should the interestingness between the selected pairs of concepts be computed. Options: pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
        @param eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 200
        assert eventsSampleSize <= 300000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))


class RequestEventsConceptTrends(RequestEvents):
    def __init__(self,
                 conceptCount = 10,
                 returnInfo = ReturnInfo()):
        """
        return a list of top trending concepts and their daily trending info over time
        @param conceptCount: number of top concepts to return (at most 50)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert conceptCount <= 50
        self.resultType = "conceptTrends"
        self.conceptTrendsConceptCount = conceptCount
        self.__dict__.update(returnInfo.getParams("conceptTrends"))


class RequestEventsSourceAggr(RequestEvents):
    def __init__(self,
                 sourceCount = 30,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        """
        return top news sources that report about the events that match the search conditions
        @param sourceCount: number of top sources to return (at most 200)
        @param eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
        @param returnInfo: what details about the sources should be included in the returned information
        """
        assert sourceCount <= 200
        assert eventsSampleSize <= 300000
        self.resultType = "sourceAggr"
        self.sourceAggrSourceCount = sourceCount
        self.sourceAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("sourceAggr"))


class RequestEventsDateMentionAggr(RequestEvents):
    def __init__(self,
                 minDaysApart = 0,
                 minDateMentionCount = 5,
                 eventsSampleSize = 100000):
        """
        return events and the dates that are mentioned in articles about these events
        @param minDaysApart: ignore events that don't have a date that is more than this number of days apart from the tested event
        @param minDateMentionCount: report only dates that are mentioned at least this number of times
        @param eventsSampleSize: on what sample of results should the aggregate be computed (at most 300000)
        """
        assert eventsSampleSize <= 300000
        self.resultType = "dateMentionAggr"
        self.dateMentionAggrMinDaysApart = minDaysApart
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrSampleSize = eventsSampleSize


class RequestEventsEventClusters(RequestEvents):
    def __init__(self,
                 keywordCount = 30,
                 maxEventsToCluster = 10000,
                 returnInfo = ReturnInfo()):
        """
        return hierarchical clustering of events into smaller clusters. 2-means clustering is applied on each node in the tree
        @param keywordCount: number of keywords to report in each of the clusters (at most !00)
        @param maxEventsToCluster: try to cluster at most this number of events (at most 10000)
        @param returnInfo: what details about the concepts should be included in the returned information
        """
        assert keywordCount <= 100
        assert maxEventsToCluster <= 10000
        self.resultType = "eventClusters"
        self.eventClustersKeywordCount = keywordCount
        self.eventClustersMaxEventsToCluster = maxEventsToCluster
        self.__dict__.update(returnInfo.getParams("eventClusters"))


class RequestEventsCategoryAggr(RequestEvents):
    def __init__(self,
                 returnInfo = ReturnInfo()):
        """
        return distribution of events into dmoz categories
        @param returnInfo: what details about the categories should be included in the returned information
        """
        self.resultType = "categoryAggr"
        self.__dict__.update(returnInfo.getParams("categoryAggr"))


class RequestEventsRecentActivity(RequestEvents):
    def __init__(self,
                 maxEventCount = 60,
                 maxMinsBack = 10 * 60,
                 lastActivityId = 0,
                 mandatoryLocation = True,
                 lang = None,
                 minAvgCosSim = 0,
                 returnInfo = ReturnInfo()):
        """
        return a list of recently changed events that match search conditions
        @param maxEventCount: max events to return (at most 500)
        @param: maxMinsBack: maximum number of minutes in the history to look at
        @param lastActivityId: id of the last activity (returned by previous call to the same method)
        @param mandatoryLocation: return only events that have a geographic location assigned to them
        @param lang: limit the results to events that are described in the selected language (None if not filtered by any language)
        @param minAvgCosSim: the minimum avg cos sim of the events to be returned (events with lower quality should not be included)
        @param returnInfo: what details should be included in the returned information
        """
        assert maxEventCount <= 1000
        self.resultType = "recentActivity"
        self.recentActivityEventsMaxEventCount = maxEventCount
        self.recentActivityEventsMaxMinsBack = maxMinsBack
        self.recentActivityEventsLastActivityId = lastActivityId
        self.recentActivityEventsMandatoryLocation = mandatoryLocation
        if lang != None:
            self.recentActivityEventsLang = lang
        self.eventsRecentActivityMinAvgCosSim = minAvgCosSim
        self.__dict__.update(returnInfo.getParams("recentActivityEvents"))


