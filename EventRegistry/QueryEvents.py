from eventregistry.Base import *
from eventregistry.ReturnInfo import *


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
    @param ignoreKeywords: ignore events where articles about the event mention all provided keywords
    @param ignoreConceptUri: ignore events that are about all provided concepts
    @param ignoreLang: ignore events that are reported in any of the provided languages
    @param ignoreLocationUri: ignore events that occured in any of the provided locations. A location can be a city or a place
    @param ignoreSourceUri: ignore events that have have articles which have been written by all specified news sources
    @param categoryIncludeSub: when a category is specified using categoryUri, should also all subcategories be included?
    @param ignoreCategoryIncludeSub: when a category is specified using ignoreCategoryUri, should also all subcategories be included?
    @param conceptOper: Boolean operator to use in cases when multiple concepts are specified. Possible values are:
            "AND" if all concepts should be mentioned in the resulting events
            "OR" if any of the concept should be mentioned in the resulting events
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

        if requestedResult:
            self.addRequestedResult(requestedResult)

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
        self.resultTypeList.append(requestEvents)

    @staticmethod
    def initWithEventUriList(uriList):
        q = QueryEvents()
        q.setEventUriList(uriList)
        return q

class RequestEvents:
    def __init__(self):
        self.resultType = None


class RequestEventsInfo(RequestEvents):
    """
    return event details for resulting events
    """
    def __init__(self, page = 1,
                 count = 20,
                 sortBy = "rel", sortByAsc = False,    # how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), socialScore (amount of shares in social media)
                 returnInfo = ReturnInfo()):
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
    """
    return a simple list of event uris for resulting events
    """
    def __init__(self, page = 1,
                 count = 100000,
                 sortBy = "rel", sortByAsc = False):    # how should the resulting events be sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), socialScore (amount of shares in social media)
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
    """
    return time distribution of resulting events
    """
    def __init__(self):
        self.resultType = "timeAggr"


class RequestEventsKeywordAggr(RequestEvents):
    """
    return keyword aggregate (tag cloud) of resulting events
    """
    def __init__(self, lang = "eng"):
        self.resultType = "keywordAggr"
        self.keywordAggrLang = lang


class RequestEventsLocAggr(RequestEvents):
    """
    return aggreate of locations of resulting events
    """
    def __init__(self,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert eventsSampleSize <= 300000
        self.resultType = "locAggr"
        self.locAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("locAggr"))


class RequestEventsLocTimeAggr(RequestEvents):
    """
    return aggreate of locations and times of resulting events
    """
    def __init__(self,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert eventsSampleSize <= 300000
        self.resultType = "locTimeAggr"
        self.locTimeAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("locTimeAggr"))


class RequestEventsConceptAggr(RequestEvents):
    """
    get aggregated list of concepts - top concepts that appear in events
    """
    def __init__(self,
                 conceptCount = 20,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 200
        assert eventsSampleSize <= 3000000
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptAggr"))


class RequestEventsConceptGraph(RequestEvents):
    """
    return a graph of concepts - connect concepts that are frequently occuring in the same events
    """
    def __init__(self,
                 conceptCount = 25,
                 linkCount = 50,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 1000
        assert linkCount <= 2000
        assert eventsSampleSize <= 300000
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptGraph"))


class RequestEventsConceptMatrix(RequestEvents):
    """
    get a matrix of concepts and their dependencies. For individual concept pairs
    return how frequently they co-occur in the resulting events and
    how "surprising" this is, based on the frequency of individual concepts
    """
    def __init__(self,
                 conceptCount = 25,
                 measure = "pmi",
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 200
        assert eventsSampleSize <= 300000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))


class RequestEventsConceptTrends(RequestEvents):
    """
    return a list of top trending concepts and their daily trending info over time
    """
    def __init__(self,
                 conceptCount = 10,
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 50
        self.resultType = "conceptTrends"
        self.conceptTrendsConceptCount = conceptCount
        self.__dict__.update(returnInfo.getParams("conceptTrends"))


class RequestEventsSourceAggr(RequestEvents):
    """
    return top news sources that report about the events that match the search conditions
    """
    def __init__(self, sourceCount = 30,
                 eventsSampleSize = 100000,
                 returnInfo = ReturnInfo()):
        assert sourceCount <= 200
        assert eventsSampleSize <= 300000
        self.resultType = "sourceAggr"
        self.sourceAggrSourceCount = sourceCount
        self.sourceAggrSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("sourceAggr"))


class RequestEventsDateMentionAggr(RequestEvents):
    """
    return events and the dates that are mentioned in articles about these events
    """
    def __init__(self,
                 minDaysApart = 0,
                 minDateMentionCount = 5,
                 eventsSampleSize = 100000):
        assert eventsSampleSize <= 300000
        self.resultType = "dateMentionAggr"
        self.dateMentionAggrMinDaysApart = minDaysApart
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrSampleSize = eventsSampleSize


class RequestEventsEventClusters(RequestEvents):
    """
    return hierarchical clustering of events into smaller clusters
    2-means clustering is applied on each node in the tree
    """
    def __init__(self,
                 keywordCount = 30,
                 maxEventsToCluster = 10000,
                 returnInfo = ReturnInfo()):
        assert keywordCount <= 100
        assert maxEventsToCluster <= 10000
        self.resultType = "eventClusters"
        self.eventClustersKeywordCount = keywordCount
        self.eventClustersMaxEventsToCluster = maxEventsToCluster
        self.__dict__.update(returnInfo.getParams("eventClusters"))


class RequestEventsCategoryAggr(RequestEvents):
    """
    return distribution of events into dmoz categories
    """
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "categoryAggr"
        self.__dict__.update(returnInfo.getParams("categoryAggr"))


class RequestEventsRecentActivity(RequestEvents):
    """
    return a list of recently changed events that match search conditions
    """
    def __init__(self,
                 maxEventCount = 60,
                 maxMinsBack = 10 * 60,
                 lastEventActivityId = 0,
                 lang = "eng",
                 eventsWithLocationOnly = True,
                 eventsWithLangOnly = False,
                 minAvgCosSim = 0,
                 returnInfo = ReturnInfo()):
        assert maxEventCount <= 1000
        self.resultType = "recentActivity"
        self.eventsRecentActivityMaxEventCount = maxEventCount
        self.eventsRecentActivityMaxMinsBack = maxMinsBack
        self.eventsRecentActivityLastEventActivityId = lastEventActivityId
        self.eventsRecentActivityEventLang = lang                                   # the language in which title should be returned
        self.eventsRecentActivityEventsWithLocationOnly = eventsWithLocationOnly    # return only events for which we've recognized their location
        self.eventsRecentActivityEventsWithLangOnly = eventsWithLangOnly            # return only event that have a cluster at least in the lang language
        self.eventsRecentActivityMinAvgCosSim = minAvgCosSim                        # the minimum avg cos sim of the events to be returned (events with lower quality should not be included)
        self.__dict__.update(returnInfo.getParams("recentActivity"))


