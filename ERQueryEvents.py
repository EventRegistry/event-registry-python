from ERBase import *
from ERReturnInfo import *

# query class for searching for events in the event registry 
class QueryEvents(Query):
    def __init__(self,  **kwargs):
        super(QueryEvents, self).__init__();
        
        self._setVal("action", "getEvents");

        self._setValIfNotDefault("keywords", kwargs, "");          # e.g. "bla bla"
        self._setValIfNotDefault("conceptUri", kwargs, []);      # e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"]
        self._setValIfNotDefault("lang", kwargs, []);                  # eng, deu, spa, zho, slv, ...
        self._setValIfNotDefault("sourceUri", kwargs, []);    # ["www.bbc.co.uk"]
        self._setValIfNotDefault("locationUri", kwargs, []);    # ["http://en.wikipedia.org/wiki/Ljubljana"]
        self._setValIfNotDefault("categoryUri", kwargs, []);    # ["http://www.dmoz.org/Science/Astronomy"]
        self._setValIfNotDefault("categoryIncludeSub", kwargs, True);
        self._setValIfNotDefault("dateStart", kwargs, "");    # 2014-05-02
        self._setValIfNotDefault("dateEnd", kwargs, "");        # 2014-05-02
        if kwargs.has_key("minArticlesInEvent"):
            self._setVal("minArticlesInEvent", kwargs["minArticlesInEvent"]);
        if kwargs.has_key("maxArticlesInEvent"):
            self._setVal("maxArticlesInEvent", kwargs["maxArticlesInEvent"]);
        if kwargs.has_key("dateMentionStart"):
            self._setVal("dateMentionStart", kwargs["dateMentionStart"]);    # e.g. 2014-05-02
        if kwargs.has_key("dateMentionEnd"):
            self._setVal("dateMentionEnd", kwargs["dateMentionEnd"]);        # e.g. 2014-05-02

        self._setValIfNotDefault("ignoreKeywords", kwargs, "");
        self._setValIfNotDefault("ignoreConceptUri", kwargs, []);
        self._setValIfNotDefault("ignoreLang", kwargs, []);
        self._setValIfNotDefault("ignoreLocationUri", kwargs, []);
        self._setValIfNotDefault("ignoreSourceUri", kwargs, []);
        self._setValIfNotDefault("ignoreCategoryUri", kwargs, []);
        self._setValIfNotDefault("ignoreCategoryIncludeSub", kwargs, True);
        

    def _getPath(self):
        return "/json/event";

    def addConcept(self, conceptUri):
        self._addArrayVal("conceptUri", conceptUri);

    def addLocation(self, locationUri):
        self._addArrayVal("locationUri", locationUri);
        
    def addCategory(self, categoryUri):
        self._addArrayVal("categoryUri", categoryUri)

    def addNewsSource(self, newsSourceUri):
        self._addArrayVal("sourceUri", newsSourceUri)

    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams.pop("keywords", "") + " " + keyword;

    # set a custom list of event uris. the results will be then computed on this list - no query will be done
    def setEventUriList(self, uriList):
        self.queryParams = { "action": "getEvents", "eventUriList": ",".join(uriList) };

    def setDateLimit(self, startDate, endDate):
        self._setDateVal("dateStart", startDate);
        self._setDateVal("dateEnd", endDate);
                    
    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestEvents):
        if not isinstance(requestEvents, RequestEvents):
            raise AssertionError("QueryEvents class can only accept result requests that are of type RequestEvents");
        self.resultTypeList.append(requestEvents);



# #####################################
# #####################################
class RequestEvents:
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestEventsInfo(RequestEvents):
    def __init__(self, page = 0, count = 20, 
                 sortBy = "date", sortByAsc = False,    # date, rel, size, socialScore
                 returnInfo = ReturnInfo()):
        assert count <= 200
        self.resultType = "events"
        self.eventsPage = page
        self.eventsCount = count
        self.eventsSortBy = sortBy          # date, rel, size, socialScore
        self.eventsSortByAsc = sortByAsc
        self.__dict__.update(returnInfo.getParams("events"))

    def setPage(self, page):
        self.eventsPage = page

    def setCount(self, count):
        self.eventsCount = count

# return a list of event uris
class RequestEventsUriList(RequestEvents):
    def __init__(self):
        self.resultType = "uriList"

        # get time distribution of resulting events
class RequestEventsTimeAggr(RequestEvents):
    def __init__(self):
        self.resultType = "timeAggr"

# get keyword aggregate of resulting events
class RequestEventsKeywordAggr(RequestEvents):
    def __init__(self, lang = "eng"):
        self.resultType = "keywordAggr"
        self.keywordAggrLang = lang;

# get aggreate of locations of resulting events
class RequestEventsLocAggr(RequestEvents):
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "locAggr"
        self.__dict__.update(returnInfo.getParams("locAggr"))

# get aggreate of locations and times of resulting events
class RequestEventsLocTimeAggr(RequestEvents):
    def __init__(self, returnInfo = ReturnInfo()):
        self.resultType = "locTimeAggr"
        self.__dict__.update(returnInfo.getParams("locTimeAggr"))

# list of top news sources that report about events that are among the results
class RequestEventsTopSourceAggr(RequestEvents):
    def __init__(self, 
                 topSourceCount = 20, 
                 returnInfo = ReturnInfo()):
        assert topSourceCount <= 200
        self.resultType = "topSourceAggr"
        self.topSourceAggrTopSourceCount = topSourceCount
        self.__dict__.update(returnInfo.getParams("topSourceAggr"))

# get aggregated list of concepts - top concepts that appear in events 
class RequestEventsConceptAggr(RequestEvents):
    def __init__(self, 
                 conceptCount = 20, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 200
        self.resultType = "conceptAggr"
        self.conceptAggrConceptCount = conceptCount
        self.__dict__.update(returnInfo.getParams("conceptAggr"))

# get a graph of concepts - connect concepts that are frequently in the same events
class RequestEventsConceptGraph(RequestEvents):
    def __init__(self, 
                 conceptCount = 25, 
                 linkCount = 50, 
                 eventsSampleSize = 500, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 1000
        assert linkCount <= 2000
        assert eventsSampleSize <= 20000
        self.resultType = "conceptGraph"
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptGraph"))

# get a matrix of concepts and their dependencies
class RequestEventsConceptMatrix(RequestEvents):
    def __init__(self, 
                 conceptCount = 25, 
                 measure = "pmi", 
                 eventsSampleSize = 500, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 200
        assert eventsSampleSize <= 10000
        self.resultType = "conceptMatrix"
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.__dict__.update(returnInfo.getParams("conceptMatrix"))

# get a list of top trending concepts and their daily trends over time
class RequestEventsConceptTrends(RequestEvents):
    def __init__(self, 
                 conceptCount = 10, 
                 returnInfo = ReturnInfo()):
        assert conceptCount <= 50
        self.resultType = "conceptTrends"
        self.conceptTrendsConceptCount = conceptCount
        self.__dict__.update(returnInfo.getParams("conceptTrends"))

# get events and the dates they mention
class RequestEventsDateMentionAggr(RequestEvents):
    def __init__(self, 
                 minDaysApart = 0, 
                 minDateMentionCount = 5):
        self.resultType = "dateMentionAggr"
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrMinDaysApart = minDaysApart

# get hierarchical clustering of events into smaller clusters.
class RequestEventsEventClusters(RequestEvents):
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

# get distribution of events into dmoz categories
class RequestEventsCategoryAggr(RequestEvents):
    def __init__(self):
        self.resultType = "categoryAggr"

# get list of recently changed events
class RequestEventsRecentActivity(RequestEvents):
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
        

