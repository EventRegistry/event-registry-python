"""
classes responsible for obtaining results from the Event Registry
"""
import os, sys, urllib2, urllib, json, datetime;

class Query(object):
    def __init__(self):
        self.queryParams = {};
        self.resultTypeList = [];

    def _encode(self):
        self._updateQueryParamsWithResultTypes();
        return urllib.urlencode(self.queryParams, True);

    def _updateQueryParamsWithResultTypes(self):
        if len(self.resultTypeList) == 0:
            raise ValueError("The query does not have any result type specified. No sense in performing such a query");
        for request in self.resultTypeList:
            self.queryParams.update(request.__dict__);
        self.queryParams["resultType"] = [request.__dict__["resultType"] for request in self.resultTypeList];


# query class for searching for events in the event registry 
class QueryEvents(Query):
    def __init__(self,  **kwargs):
        super(QueryEvents, self).__init__();
        
        self.queryParams["action"] = "getEvents";

        self.queryParams["keywords"] = kwargs.pop("keywords", "");          # e.g. "bla bla"
        self.queryParams["conceptUri"] = kwargs.pop("conceptUri", []);      # e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"]
        self.queryParams["lang"] = kwargs.pop("lang", []);                  # eng, deu, spa, zho, slv
        self.queryParams["publisherUri"] = kwargs.pop("publisherUri", []);    # ["www.bbc.co.uk"]
        self.queryParams["locationUri"] = kwargs.pop("locationUri", []);    # ["http://en.wikipedia.org/wiki/Ljubljana"]
        self.queryParams["categoryUri"] = kwargs.pop("categoryUri", []);    # ["http://www.dmoz.org/Science/Astronomy"]
        self.queryParams["categoryIncludeSub"] = kwargs.pop("categoryIncludeSub", True);
        self.queryParams["dateStart"] = kwargs.pop("dateStart", "");    # 2014-05-02
        self.queryParams["dateEnd"] = kwargs.pop("dateEnd", "");        # 2014-05-02
        if kwargs.has_key("minArticlesInEvent"):
            self.queryParams["minArticlesInEvent"] = kwargs["minArticlesInEvent"];
        if kwargs.has_key("maxArticlesInEvent"):
            self.queryParams["maxArticlesInEvent"] = kwargs["maxArticlesInEvent"];
        if kwargs.has_key("dateMentionStart"):
            self.queryParams["dateMentionStart"] = kwargs["dateMentionStart"];  # 2014-05-02
        if kwargs.has_key("dateMentionEnd"):
            self.queryParams["dateMentionEnd"] = kwargs["dateMentionEnd"];      # 2014-05-02

        self.queryParams["ignoreKeywords"] = kwargs.pop("ignoreKeywords", "");
        self.queryParams["ignoreConceptUri"] = kwargs.pop("ignoreConceptUri", []);
        self.queryParams["ignoreLang"] = kwargs.pop("ignoreLang", []);
        self.queryParams["ignoreLocationUri"] = kwargs.pop("ignoreLocationUri", []);
        self.queryParams["ignorePublisherUri"] = kwargs.pop("ignorePublisherUri", []);
        self.queryParams["ignoreCategoryUri"] = kwargs.pop("ignoreCategoryUri", []);
        self.queryParams["ignoreCategoryIncludeSub"] = kwargs.pop("ignoreCategoryIncludeSub", True);

        self.queryParams["eventUriList"] = kwargs.pop("eventUriList", "");      # e.g. "1,3,54,65,234"  - Note: if eventUriList is specified, other conditions are ignored!
        

    def _getPath(self):
        return "/json/event";

    def addConcept(self, conceptUri):
        self.queryParams["conceptUri"].append(conceptUri);

    def addLocation(self, locationUri):
        self.queryParams["locationUri"].append(locationUri);
        
    def addCategory(self, categoryUri):
        self.queryParams["categoryUri"].append(categoryUri)

    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams["keywords"] + " " + keyword;

    # set a custom list of event uris. the results will be then computed on this list - no query will be done
    def setEventUriList(self, uriList):
        self.queryParams = { "eventUriList": uriList };

    def setDateLimit(self, startDate, endDate):
        if isinstance(startDate, datetime.date):
            self.queryParams["dateStart"] = startDate.isoformat()
        elif isinstance(startDate, datetime.datetime):
            self.queryParams["dateStart"] = startDate.date().isoformat()
        elif self.queryParams.has_key("dateStart"):
            del self.queryParams["dateStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateEnd"] = endDate.date().isoformat()
        elif self.queryParams.has_key("dateEnd"):
            del self.queryParams["dateEnd"]

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestEvent):
        if not isinstance(requestEvent, RequestEvent):
            raise AssertionError("QueryEvents class can only accept result requests that are of type RequestEvent");
        self.resultTypeList.append(requestEvent);


# query class for searching for articles in the event registry 
class QueryArticles(Query):
    def __init__(self,  **kwargs):
        super(QueryArticles, self).__init__();
        self.queryParams["action"] = "getArticles";
        self.queryParams["keywords"] = kwargs.pop("keywords", "");          # e.g. "bla bla"
        self.queryParams["conceptUri"] = kwargs.pop("conceptUri", []);      # e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"]
        self.queryParams["lang"] = kwargs.pop("lang", []);                  # eng, deu, spa, zho, slv
        self.queryParams["publisherUri"] = kwargs.pop("publisherUri", []);    # ["www.bbc.co.uk"]
        self.queryParams["locationUri"] = kwargs.pop("locationUri", []);    # ["http://en.wikipedia.org/wiki/Ljubljana"]
        self.queryParams["categoryUri"] = kwargs.pop("categoryUri", []);    # ["http://www.dmoz.org/Science/Astronomy"]
        self.queryParams["categoryIncludeSub"] = kwargs.pop("categoryIncludeSub", True);
        self.queryParams["dateStart"] = kwargs.pop("dateStart", "");    # 2014-05-02
        self.queryParams["dateEnd"] = kwargs.pop("dateEnd", "");        # 2014-05-02
        self.queryParams["dateMentionStart"] = kwargs.pop("dateMentionStart", "");  # 2014-05-02
        self.queryParams["dateMentionEnd"] = kwargs.pop("dateMentionEnd", "");      # 2014-05-02

        self.queryParams["ignoreKeywords"] = kwargs.pop("ignoreKeywords", "");
        self.queryParams["ignoreConceptUri"] = kwargs.pop("ignoreConceptUri", []);
        self.queryParams["ignoreLang"] = kwargs.pop("ignoreLang", []);
        self.queryParams["ignoreLocationUri"] = kwargs.pop("ignoreLocationUri", []);
        self.queryParams["ignorePublisherUri"] = kwargs.pop("ignorePublisherUri", []);
        self.queryParams["ignoreCategoryUri"] = kwargs.pop("ignoreCategoryUri", []);
        self.queryParams["ignoreCategoryIncludeSub"] = kwargs.pop("ignoreCategoryIncludeSub", True);
        
    def _getPath(self):
        return "/json/article";
    
    def addConcept(self, conceptUri):
        self.queryParams["conceptUri"].append(conceptUri);

    def addLocation(self, locationUri):
        self.queryParams["locationUri"].append(locationUri);

    def addCategory(self, categoryUri):
        self.queryParams["categoryUri"].append(categoryUri)

    def addKeyword(self, keyword):
        self.queryParams["keywords"] = self.queryParams["keywords"] + " " + keyword;

    # set a custom list of event uris. the results will be then computed on this list - no query will be done
    def setEventUriList(self, uriList):
        self.queryParams = { "eventUriList": uriList };

    def setDateLimit(self, startDate, endDate):
        if isinstance(startDate, datetime.date):
            self.queryParams["dateStart"] = startDate.isoformat()
        elif isinstance(startDate, datetime.datetime):
            self.queryParams["dateStart"] = startDate.date().isoformat()
        elif self.queryParams.has_key("dateStart"):
            del self.queryParams["dateStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateEnd"] = endDate.date().isoformat()
        elif self.queryParams.has_key("dateEnd"):
            del self.queryParams["dateEnd"]

    def setDateMentionLimit(self, startDate, endDate):
        if isinstance(startDate, datetime.date):
            self.queryParams["dateMentionStart"] = startDate.isoformat()
        elif isinstance(startDate, datetime.datetime):
            self.queryParams["dateMentionStart"] = startDate.date().isoformat()
        elif self.queryParams.has_key("dateMentionStart"):
            del self.queryParams["dateMentionStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateMentionEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateMentionEnd"] = endDate.date().isoformat()
        elif self.queryParams.has_key("dateMentionEnd"):
            del self.queryParams["dateMentionEnd"]

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestArticle):
        if not isinstance(requestArticle, RequestArticle):
            raise AssertionError("QueryArticles class can only accept result requests that are of type RequestArticle");
        self.resultTypeList.append(requestArticle);

# #####################################
# #####################################
class RequestEvent(object):
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestEventInfo(RequestEvent):
    def __init__(self, page = 0, count = 20, sortBy = "date", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], includeArticleCounts = True, includeConcepts = True, includeMultiLingInfo = True, includeCategories = True, includeLocation = True, includeStories = False, includeImages = True):
        self.eventsPage = page
        self.eventsCount = count
        self.eventsSortBy = sortBy
        self.eventsSortByAsc = sortByAsc
        self.eventsConceptLang = conceptLang
        self.eventsConceptTypes = conceptTypes
        self.eventsIncludeArticleCounts = includeArticleCounts
        self.eventsIncludeConcepts = includeConcepts
        self.eventsIncludeMultiLingInfo = includeMultiLingInfo
        self.eventsIncludeCategories = includeCategories
        self.eventsIncludeLocation = includeLocation
        self.eventsIncludeStories = includeStories
        self.eventsIncludeImages = includeImages
        self.resultType = "events"

# return a list of event uris
class RequestEventUriList(RequestEvent):
    def __init__(self):
        self.resultType = "uriList"

# get time distribution of resulting events
class RequestEventTimeAggr(RequestEvent):
    def __init__(self):
        self.resultType = "timeAggr"

# get aggreate of locations of resulting events
class RequestEventLocAggr(RequestEvent):
    def __init__(self, conceptLangs = ["eng"]):
        self.locAggrConceptLang = conceptLangs
        self.resultType = "locAggr"

# get aggreate of locations and times of resulting events
class RequestEventLocTimeAggr(RequestEvent):
    def __init__(self, conceptLangs = ["eng"]):
        self.locTimeAggrConceptLang = conceptLangs
        self.resultType = "locTimeAggr"

# list of top publishers that report about events that are among the results
class RequestEventTopPublisherAggr(RequestEvent):
    def __init__(self, topPublisherCount = 20, includePublisherDetails = True):
        self.topPublisherAggrTopPublisherCount = topPublisherCount
        self.topPublisherAggrIncludePublisherDetails = includePublisherDetails
        self.resultType = "topPublisherAggr"

# get aggregated list of concepts - top concepts that appear in events 
class RequestEventConceptAggr(RequestEvent):
    def __init__(self, conceptCount = 20, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"]):
        self.conceptAggrConceptType = conceptTypes
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrConceptLang = conceptLangs
        self.resultType = "conceptAggr"

# get a graph of concepts - connect concepts that are frequently in the same events
class RequestEventConceptGraph(RequestEvent):
    def __init__(self, conceptCount = 20, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"], linkCount = 50, eventsSampleSize = 500):
        self.conceptGraphConceptType = conceptTypes
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphConceptLang = conceptLangs
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.resultType = "conceptGraph"

# get a matrix of concepts and their dependencies
class RequestEventConceptMatrix(RequestEvent):
    def __init__(self, conceptCount = 20, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"], measure = "pmi", eventsSampleSize = 500):
        self.conceptMatrixConceptType = conceptTypes
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixConceptLang = conceptLangs
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.resultType = "conceptMatrix"

# get a list of top trending concepts and their daily trends over time
class RequestEventTrendingConcepts(RequestEvent):
    def __init__(self, conceptCount = 20, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"]):
        self.trendingConceptsConceptType = conceptTypes
        self.trendingConceptsConceptCount = conceptCount
        self.trendingConceptsConceptLang = conceptLangs
        self.resultType = "trendingConcepts"

# get events and the dates they mention
class RequestEventDateMentionAggr(RequestEvent):
    def __init__(self, minDaysApart = 0, minDateMentionCount = 5):
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrMinDaysApart = minDaysApart
        self.resultType = "dateMentionAggr"

# get hierarchical clustering of events into smaller clusters.
class RequestEventEventClusters(RequestEvent):
    def __init__(self, keywordCount = 30, conceptLangs = ["eng"], maxEventsToCluster = 10000):
        self.eventClustersKeywordCount = keywordCount
        self.eventClustersConceptLang = conceptLangs
        self.eventClustersMaxEventsToCluster = maxEventsToCluster
        self.resultType = "eventClusters"

# get distribution of events into dmoz categories
class RequestEventCategoryAggr(RequestEvent):
    def __init__(self):
        self.resultType = "categoryAggr"


# #####################################
# #####################################
class RequestArticle(object):
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestArticleInfo(RequestArticle):
    def __init__(self, page = 0, count = 20, sortBy = "date", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], bodyLen = 300, includeBody = True, includeTitle = True, includeConcepts = True, includeSourceInfo = True, includeStoryUri = True, includeCategories = True, includeLocation = True, includeStories = False, includeImage = True):
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy        # date, id, cosSim, fq
        self.articlesSortByAsc = sortByAsc
        self.articlesBodyLen = bodyLen;
        self.articlesConceptLang = conceptLang
        self.articlesConceptTypes = conceptTypes
        
        self.articlesIncludeBody = includeBody
        self.articlesIncludeTitle = includeTitle
        self.articlesIncludeConcepts = includeConcepts
        self.articlesIncludeSourceInfo = includeSourceInfo
        self.articlesIncludeStoryUri = includeStoryUri
        self.articlesIncludeCategories = includeCategories
        self.articlesIncludeLocation = includeLocation
        self.articlesIncludeImage = includeImage
        self.resultType = "articles"
        
# return a list of event uris
class RequestArticleUriList(RequestArticle):
    def __init__(self):
        self.resultType = "uriList"

# get time distribution of resulting articles
class RequestArticleTimeAggr(RequestArticle):
    def __init__(self):
        self.resultType = "timeAggr"

# get aggreate of categories of resulting articles
class RequestArticleCategoryAggr(RequestArticle):
    def __init__(self, articlesSampleSize = 20000):
        self.categoryAggrSampleSize = articlesSampleSize
        self.resultType = "categoryAggr"

# get aggreate of concepts of resulting articles
class RequestArticleConceptAggr(RequestArticle):
    def __init__(self, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], conceptCount = 25, articlesSampleSize = 1000):
        self.conceptAggrConceptLang = conceptLang
        self.conceptAggrConceptType = conceptTypes
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize        
        self.resultType = "conceptAggr"

# get aggreate of sources of resulting articles
class RequestArticleCategoryAggr(RequestArticle):
    def __init__(self, articlesSampleSize = 20000):
        self.categoryAggrSampleSize = articlesSampleSize
        self.resultType = "sourceAggr"

# get aggreate of sources of resulting articles
class RequestArticleKeywordAggr(RequestArticle):
    def __init__(self, lang = "eng", count = 50):
        self.keywordAggrLang = articlesSampleSize
        self.keywordAggrCount = count
        self.resultType = "keywordAggr"
        
# get aggreate of sources of resulting articles
class RequestArticleConceptMatrix(RequestArticle):
    def __init__(self, count = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLang = ["eng"], measure = "pmi", sampleSize = 500):
        self.conceptMatrixConceptCount = count
        self.conceptMatrixConceptLang = conceptLang
        self.conceptMatrixConceptType = conceptTypes
        self.conceptMatrixSampleSize = sampleSize
        self.conceptMatrixMeasure = measure             # pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
        self.resultType = "conceptMatrix"

# get concept graph of resulting articles
class RequestArticleConceptGraph(RequestArticle):
    def __init__(self, count = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLang = ["eng"], linkCount = 50, sampleSize = 500):
        self.conceptGraphConceptCount = count
        self.conceptGraphConceptLang = conceptLang
        self.conceptGraphConceptType = conceptTypes
        self.conceptGraphSampleSize = sampleSize
        self.conceptGraphLinkCount = linkCount
        self.resultType = "conceptGraph"

# get trending of concepts in the resulting articles
class RequestArticleTrendingConcepts(RequestArticle):
    def __init__(self, count = 25, conceptLang = ["eng"]):
        self.trendingConceptsConceptCount = count
        self.trendingConceptsConceptLang = conceptLang
        self.resultType = "trendingConcepts"

# get trending of concepts in the resulting articles
class RequestArticleTrendingConcepts(RequestArticle):
    def __init__(self):
        self.resultType = "dateMentionAggr"
        
# #####################################
# #####################################

# object that can access event registry 
class EventRegistry(object):
    def __init__(self, host = "http://eventregistry.org"):
        self.Host = host;

    # main method for executing the search queries. 
    def execQuery(self, query, convertToDict = True):
        params = query._encode();
        req = urllib2.Request(self.Host + query._getPath() + "?" + params);
        respInfo = urllib2.urlopen(req).read();
        if convertToDict:
            respInfo = json.loads(respInfo);
        return respInfo;

    # return a list of concepts that contain the given prefix
    # valid sources: concepts, entities, person, loc, org, wiki
    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", labelLang = "eng", page = 0, count = 20):      
        params = urllib.urlencode({ "prefix": prefix, "source": sources, "lang": lang, "labelLang": labelLang, "page": page, "count": count }, True);
        req = urllib2.Request(self.Host + "/json/suggestConcepts" + "?" + params);
        respInfo = urllib2.urlopen(req).read();
        respInfo = json.loads(respInfo);
        return respInfo;

    # return a list of news sources that match the prefix
    def suggestNewsSources(self, prefix, page = 0, count = 20):
        params = urllib.urlencode({ "prefix": prefix, "page": page, "count": count }, True);
        req = urllib2.Request(self.Host + "/json/suggestSources" + "?" + params);
        respInfo = urllib2.urlopen(req).read();
        respInfo = json.loads(respInfo);
        return respInfo;

    # return a list of locations (cities or countries) that contain the prefix
    def suggestLocations(self, prefix, count = 20, lang = "eng", source = ["city", "country"]):
        params = urllib.urlencode({ "prefix": prefix, "count": count, "source": source, "lang": lang }, True);
        req = urllib2.Request(self.Host + "/json/suggestLocations" + "?" + params);
        respInfo = urllib2.urlopen(req).read();
        respInfo = json.loads(respInfo);
        return respInfo;

    # return a list of dmoz categories that contain the prefix
    def suggestCategories(self, prefix, page = 0, count = 20, lang = "eng", source = ["city", "country"]):
        params = urllib.urlencode({ "prefix": prefix, "page": page, "count": count }, True);
        req = urllib2.Request(self.Host + "/json/suggestCategories" + "?" + params);
        respInfo = urllib2.urlopen(req).read();
        respInfo = json.loads(respInfo);
        return respInfo;

    # return a concept uri that is the best match for the given concept label
    def getConceptUri(self, conceptLabel, lang = "eng"):
        matches = self.suggestConcepts(conceptLabel, lang = lang);
        if len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"];
        return None;


if __name__ == '__main__':
    fileDir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(fileDir);
    er = EventRegistry(host = "http://beta.eventregistry.org")
    #er = EventRegistry(host = "http://localhost:8090")
    
    q = QueryEvents();
    q.addConcept(er.getConceptUri("Obama"));
    q.addRequestedResult(RequestEventUriList());
    q.addRequestedResult(RequestEventConceptAggr());
    res = er.execQuery(q);

    q = QueryEvents();
    places = er.suggestLocations("Berlin")
    q.addLocation(places[0]["wikiUri"])
    q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
    q.addRequestedResult(RequestEventTrendingConcepts());
    q.addRequestedResult(RequestEventCategoryAggr());
    q.addRequestedResult(RequestEventInfo());
    res = er.execQuery(q);

    q = QueryArticles();
    q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
    q.addKeyword("apple");
    q.addKeyword("iphone");
    q.addRequestedResult(RequestArticleInfo(page=0, count = 30));
    res = er.execQuery(q);

    print res;