"""
classes responsible for obtaining results from the Event Registry
"""
import os, sys, urllib2, urllib, json, datetime;

allLangs = ["eng", "deu", "zho", "slv", "spa"];

class Query(object):
    def __init__(self):
        self.queryParams = {};
        self.resultTypeList = [];

    def clearRequestedResults(self):
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

class RequestBase(object):
    def __init__(self):
        pass

    # parse the info that should be returned about an event
    def _parseEventFlags(self, prefix, **kwargs):
        self.__dict__[prefix + "IncludeArticleCounts"] = kwargs.pop("includeArticleCounts", True);
        self.__dict__[prefix + "IncludeConcepts"] = kwargs.pop("includeConcepts", True);
        self.__dict__[prefix + "IncludeMultiLingInfo"] = kwargs.pop("includeMultiLingInfo", True);
        self.__dict__[prefix + "IncludeCategories"] = kwargs.pop("includeCategories", True);
        self.__dict__[prefix + "IncludeLocation"] = kwargs.pop("includeLocation", True);
        self.__dict__[prefix + "IncludeStories"] = kwargs.pop("includeStories", False);
        self.__dict__[prefix + "IncludeImages"] = kwargs.pop("includeImages", False);
    
    # parse the info that should be returned about an article    
    def _parseArticleFlags(self, prefix, **kwargs):
        self.__dict__[prefix + "IncludeBasicInfo"] = kwargs.pop("includeBasicInfo", True);
        self.__dict__[prefix + "IncludeBody"] = kwargs.pop("includeBody", True);
        self.__dict__[prefix + "IncludeTitle"] = kwargs.pop("includeTitle", True);
        self.__dict__[prefix + "IncludeConcepts"] = kwargs.pop("includeConcepts", False);
        self.__dict__[prefix + "IncludeSourceInfo"] = kwargs.pop("includeSourceInfo", True);
        self.__dict__[prefix + "IncludeEventUri"] = kwargs.pop("includeEventUri", True);
        self.__dict__[prefix + "IncludeStoryUri"] = kwargs.pop("includeStoryUri", False);
        self.__dict__[prefix + "IncludeDuplicateList"] = kwargs.pop("includeDuplicateList", False);
        self.__dict__[prefix + "IncludeCategories"] = kwargs.pop("includeCategories", False);
        self.__dict__[prefix + "IncludeLocation"] = kwargs.pop("includeLocation", False);
        self.__dict__[prefix + "IncludeImage"] = kwargs.pop("includeImage", False);

    # parse the info that should be returned about a story
    def _parseStoryFlags(self, prefix, **kwargs):
        self.__dict__[prefix + "IncludeBasicStats"] = kwargs.pop("includeBasicStats", True);
        self.__dict__[prefix + "IncludeCategory"] = kwargs.pop("includeCategory", True);
        self.__dict__[prefix + "IncludeLocation"] = kwargs.pop("includeLocation", True);
        self.__dict__[prefix + "IncludeStoryDate"] = kwargs.pop("includeStoryDate", True);
        self.__dict__[prefix + "IncludeConcepts"] = kwargs.pop("includeConcepts", False);
        self.__dict__[prefix + "IncludeTitle"] = kwargs.pop("includeTitle", False);
        self.__dict__[prefix + "IncludeSummary"] = kwargs.pop("includeSummary", False);
        self.__dict__[prefix + "IncludeMedoidArticle"] = kwargs.pop("includeMedoidArticle", False);
        self.__dict__[prefix + "IncludeExtractedDates"] = kwargs.pop("includeExtractedDates", False);

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

    def addNewsSource(self, newsSourceUri):
        self.queryParams["publisherUri"].append(newsSourceUri)

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
        elif isinstance(startDate, str):
            self.queryParams["dateStart"] = startDate
        elif self.queryParams.has_key("dateStart"):
            del self.queryParams["dateStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateEnd"] = endDate.date().isoformat()
        elif isinstance(endDate, str):
            self.queryParams["dateEnd"] = endDate
        elif self.queryParams.has_key("dateEnd"):
            del self.queryParams["dateEnd"]
            
    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestEvents):
        if not isinstance(requestEvents, RequestEvents):
            raise AssertionError("QueryEvents class can only accept result requests that are of type RequestEvents");
        self.resultTypeList.append(requestEvents);


# query class for searching for events in the event registry 
class QueryEvent(Query):
    def __init__(self, eventUriOrList, **kwargs):
        super(QueryEvent, self).__init__();
        
        self.queryParams["action"] = "getEvent";

        self.queryParams["eventUri"] = eventUriOrList;                      # a single event uri or a list of event uris
        
    def _getPath(self):
        return "/json/event";   

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestEvent):
        if not isinstance(requestEvent, RequestEvent):
            raise AssertionError("QueryEvent class can only accept result requests that are of type RequestEvent");
        self.resultTypeList.append(requestEvent);

# query class for searching for articles in the event registry 
class QueryArticles(Query):
    def __init__(self,  **kwargs):
        super(QueryArticles, self).__init__();
        self.queryParams["action"] = "getArticles";
        self.queryParams["keywords"] = kwargs.pop("keywords", "");          # e.g. "bla bla"
        self.queryParams["conceptUri"] = kwargs.pop("conceptUri", []);      # a single concept uri or a list (e.g. ["http://en.wikipedia.org/wiki/Barack_Obama"])
        self.queryParams["lang"] = kwargs.pop("lang", []);                  # a single lang or list (possible: eng, deu, spa, zho, slv)
        self.queryParams["publisherUri"] = kwargs.pop("publisherUri", []);    # a single source uri or a list (e.g. ["www.bbc.co.uk"])
        self.queryParams["locationUri"] = kwargs.pop("locationUri", []);    # a single location uri or a list (e.g. ["http://en.wikipedia.org/wiki/Ljubljana"])
        self.queryParams["categoryUri"] = kwargs.pop("categoryUri", []);    # a single category uri or a list (e.g. ["http://www.dmoz.org/Science/Astronomy"])
        self.queryParams["categoryIncludeSub"] = kwargs.pop("categoryIncludeSub", True);    # also include the subcategories for the given categories
        self.queryParams["dateStart"] = kwargs.pop("dateStart", "");                # starting date of the published articles (e.g. 2014-05-02)
        self.queryParams["dateEnd"] = kwargs.pop("dateEnd", "");                    # ending date of the published articles (e.g. 2014-05-02)
        self.queryParams["dateMentionStart"] = kwargs.pop("dateMentionStart", "");  # first valid mentioned date detected in articles (e.g. 2014-05-02)
        self.queryParams["dateMentionEnd"] = kwargs.pop("dateMentionEnd", "");      # last valid mentioned date detected in articles (e.g. 2014-05-02)

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
        elif isinstance(startDate, str):
            self.queryParams["dateStart"] = startDate
        elif self.queryParams.has_key("dateStart"):
            del self.queryParams["dateStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateEnd"] = endDate.date().isoformat()
        elif isinstance(endDate, str):
            self.queryParams["dateEnd"] = endDate
        elif self.queryParams.has_key("dateEnd"):
            del self.queryParams["dateEnd"]

    def setDateMentionLimit(self, startDate, endDate):
        if isinstance(startDate, datetime.date):
            self.queryParams["dateMentionStart"] = startDate.isoformat()
        elif isinstance(startDate, datetime.datetime):
            self.queryParams["dateMentionStart"] = startDate.date().isoformat()
        elif isinstance(startDate, str):
            self.queryParams["dateMentionStart"] = startDate
        elif self.queryParams.has_key("dateMentionStart"):
            del self.queryParams["dateMentionStart"]

        if isinstance(endDate, datetime.date):
            self.queryParams["dateMentionEnd"] = endDate.isoformat()
        elif isinstance(endDate, datetime.datetime):
            self.queryParams["dateMentionEnd"] = endDate.date().isoformat()
        elif isinstance(endDate, str):
            self.queryParams["dateMentionEnd"] = endDate
        elif self.queryParams.has_key("dateMentionEnd"):
            del self.queryParams["dateMentionEnd"]

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestArticles):
        if not isinstance(requestArticles, RequestArticles):
            raise AssertionError("QueryArticles class can only accept result requests that are of type RequestArticles");
        self.resultTypeList.append(requestArticles);
               

# class for finding all available info for one or more articles in the event registry 
class QueryArticle(Query):
    def __init__(self, articleUriOrList, **kwargs):
        super(QueryArticle, self).__init__();
        self.queryParams["articleUri"] = articleUriOrList;      # a single article uri or a list of article uris
        self.queryParams["action"] = "getArticle";
                
    def _getPath(self):
        return "/json/article";   

    # what info does one want to get as a result of the query
    def addRequestedResult(self, requestArticle):
        if not isinstance(requestArticle, RequestArticle):
            raise AssertionError("QueryArticle class can only accept result requests that are of type RequestArticle");
        self.resultTypeList.append(requestArticle);

# #####################################
# #####################################
class RequestEvent(RequestBase):
    def __init__(self):
        self.resultType = None;
        
# return a list of event details
class RequestEventInfo(RequestEvent):
    def __init__(self, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"],
                 # what info about the event to return:
                 **kwargs):
        self.infoConceptLang = conceptLang      # in which language should be the labels of concepts in the event
        self.infoConceptType = conceptTypes     # which types of concepts to return for the event

        self._parseEventFlags("info", **kwargs);
                
        self.resultType = "info"

# return a list of articles
class RequestEventArticles(RequestEvent):
    def __init__(self, page = 0, count = 20, lang = allLangs, bodyLen = 200, sortBy = "cosSim", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"],      # what info about the articles to include:
            **kwargs):
        self.articlesLang = lang                # return articles in specified language(s)
        self.articlesPage = page                # page of the articles
        self.articlesCount = count              # number of articles to return
        self.articlesSortBy = sortBy            # how are the event articles sorted (date, id, cosSim, fq)
        self.articlesSortByAsc = sortByAsc      
        self.articlesBodyLen = bodyLen              # length of the body to return (-1 for whole article)
        self.articlesConceptLang = conceptLang      # in which language should be the labels of concepts in the articles
        self.articlesConceptType = conceptTypes     # which types of concepts to return for each article

        self._parseArticleFlags("article", **kwargs);
        self.resultType = "articles"

# return a list of article uris
class RequestEventArticleUris(RequestEvent):
    def __init__(self, lang = allLangs, sortBy = "cosSim", sortByAsc = False):
        self.articleUrisLang = lang
        self.articleUrisSortBy = sortBy          # none, id, date, cosSim, fq
        self.articleUrisSortByAsc = sortByAsc
        self.resultType = "articleUris"

# get keyword aggregate of articles in the event
class RequestEventKeywordAggr(RequestEvent):
    def __init__(self):
        self.resultType = "keywordAggr"

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
    def __init__(self, lang = allLangs, minArticleCosSim = -1, bodyLen = 0, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], **kwargs):
        self.articleTrendLang = lang
        self.articleTrendMinArticleCosSim = minArticleCosSim;

        self.articleTrendBodyLen = bodyLen              # length of the body to return (-1 for whole article)
        self.articleTrendConceptLang = conceptLang      # in which language should be the labels of concepts in the articles
        self.articleTrendConceptType = conceptTypes     # which types of concepts to return for each article
        
        self._parseArticleFlags("articleTrend", **kwargs);

        self.resultType = "articleTrend"

# get information about similar events
class RequestEventSimilarEvents(RequestEvent):
    def __init__(self, count = 20, source = "concept", maxDayDiff = sys.maxint, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], addArticleTrendInfo = False, similarEventsAggrHours = 6, includeSelf = False,
                 # which info about events to include:
                 **kwargs):
        self.similarEventsCount = count                 # number of similar events to return
        self.similarEventsConceptLang = conceptLang     # in which language(s) should be the labels of the concepts
        self.similarEventsConceptType = conceptTypes    # which concept types to use when computing similarity (relevant when source == "concept")
        self.similarEventsSource = source               # concept, cca - how to compute similarity
        self.similarEventsMaxDayDiff = maxDayDiff       # what is the maximum time difference between the similar events and this one
        
        self.similarEventsAddArticleTrendInfo = addArticleTrendInfo     # add info how the articles in the similar events are distributed over time
        self.similarEventsAggrHours = aggrHours                         # if similarEventsAddArticleTrendInfo == True then this is the aggregating window

        self.similarEventsIncludeSelf = includeSelf                     # should the info about the event itself be included among the results

        self._parseEventFlags("similarEvents", **kwargs);

        self.resultType = "similarEvents"

# get information about similar stories (clusters)
class RequestEventSimilarStories(RequestEvent):
    def __init__(self, count = 20, source = "concept", lang = ["eng"], maxDayDiff = sys.maxint, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"],
                 # which info about stories to include:
                 **kwargs):
        self.similarStoriesCount = count                # number of similar stories to return
        self.similarStoriesLang = lang                  # in which language should be the stories
        self.similarStoriesConceptLang = conceptLang    # in which language(s) should be the labels of the concepts
        self.similarStoriesConceptType = conceptTypes   # which concept types to use when computing similarity (relevant when source == "concept")
        self.similarStoriesSource = source               # concept, cca - how to compute similarity
        self.similarStoriesMaxDayDiff = maxDayDiff       # what is the maximum time difference between the similar stories and this one

        self._parseStoryFlags("similarStories", **kwargs);

        self.resultType = "similarEvents"

# #####################################
# #####################################
class RequestArticle(RequestBase):
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestArticleInfo(RequestArticle):
    def __init__(self, bodyLen = -1, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 # what info about the article to include:
                 **kwargs):
        self.infoBodyLen = bodyLen
        self.infoConceptLang = conceptLang      # in which language should be the labels of concepts in the article
        self.infoConceptType = conceptTypes     # which types of concepts to return for the article
                
        self._parseArticleFlags("info", **kwargs);
                        
        self.resultType = "info"


# return a list of similar articles based on the CCA
class RequestArticleSimilarArticles(RequestArticle):
    def __init__(self, page = 0, count = 20, lang = ["eng"], bodyLen = -1, sortBy = "cosSim", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 # what info about the article to include:
                 **kwargs):
        self.similarArticlesPage = page                 # page of the articles
        self.similarArticlesCount = count               # number of articles to return
        self.similarArticlesLang = lang                 # in which language(s) should be the similar articles
        self.similarArticlesSortBy = sortBy             # how are the event articles sorted (date, id, cosSim, fq)
        self.similarArticlesSortByAsc = sortByAsc      
        
        self.similarArticlesBodyLen = bodyLen              # length of the body to return (-1 for whole article)
        self.similarArticlesConceptLang = conceptLang      # in which language should be the labels of concepts in the articles
        self.similarArticlesConceptType = conceptTypes     # which types of concepts to return for each article

        self._parseArticleFlags("similarArticles", **kwargs);
        
        self.resultType = "similarArticles"
        

# return a list of duplicated articles of the current article
class RequestArticleDuplicatedArticles(RequestArticle):
    def __init__(self, page = 0, count = 20, bodyLen = -1, sortBy = "cosSim", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 # what info about the article to include:
                 **kwargs):
        self.duplicatedArticlesPage = page                 # page of the articles
        self.duplicatedArticlesCount = count               # number of articles to return
        self.duplicatedArticlesSortBy = sortBy             # how are the event articles sorted (date, id)
        self.duplicatedArticlesSortByAsc = sortByAsc      
        
        self.duplicatedArticlesBodyLen = bodyLen              # length of the body to return (-1 for whole article)
        self.duplicatedArticlesConceptLang = conceptLang      # in which language should be the labels of concepts in the articles
        self.duplicatedArticlesConceptType = conceptTypes     # which types of concepts to return for each article

        self._parseArticleFlags("duplicatedArticles", **kwargs);
        
        self.resultType = "duplicatedArticles"


# return the article that is the original of the given article (the current article is a duplicate)
class RequestArticleOriginalArticle(RequestArticle):
    def __init__(self, bodyLen = -1, sortBy = "cosSim", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 # what info about the article to include:
                 **kwargs):
        self._parseArticleFlags("originalArticle", **kwargs);

        self.resultType = "originalArticle"


# #####################################
# #####################################
class RequestEvents(RequestBase):
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestEventsInfo(RequestEvents):
    def __init__(self, page = 0, count = 20, sortBy = "date", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], 
                 # what info about events to include:
                 **kwargs):
        self.eventsPage = page
        self.eventsCount = count
        self.eventsSortBy = sortBy          # date, size, rel
        self.eventsSortByAsc = sortByAsc
        self.eventsConceptLang = conceptLang
        self.eventsConceptType = conceptTypes

        self._parseEventFlags("events", **kwargs);
        
        self.resultType = "events"

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
        self.keywordAggrLang = lang;
        self.resultType = "keywordAggr"

# get aggreate of locations of resulting events
class RequestEventsLocAggr(RequestEvents):
    def __init__(self, conceptLangs = ["eng"]):
        self.locAggrConceptLang = conceptLangs
        self.resultType = "locAggr"

# get aggreate of locations and times of resulting events
class RequestEventsLocTimeAggr(RequestEvents):
    def __init__(self, conceptLangs = ["eng"]):
        self.locTimeAggrConceptLang = conceptLangs
        self.resultType = "locTimeAggr"

# list of top publishers that report about events that are among the results
class RequestEventsTopPublisherAggr(RequestEvents):
    def __init__(self, topPublisherCount = 20, includePublisherDetails = True):
        self.topPublisherAggrTopPublisherCount = topPublisherCount
        self.topPublisherAggrIncludePublisherDetails = includePublisherDetails
        self.resultType = "topPublisherAggr"

# get aggregated list of concepts - top concepts that appear in events 
class RequestEventsConceptAggr(RequestEvents):
    def __init__(self, conceptCount = 20, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"]):
        self.conceptAggrConceptType = conceptTypes
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrConceptLang = conceptLangs
        self.resultType = "conceptAggr"

# get a graph of concepts - connect concepts that are frequently in the same events
class RequestEventsConceptGraph(RequestEvents):
    def __init__(self, conceptCount = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"], linkCount = 50, eventsSampleSize = 500):
        self.conceptGraphConceptType = conceptTypes
        self.conceptGraphConceptCount = conceptCount
        self.conceptGraphConceptLang = conceptLangs
        self.conceptGraphLinkCount = linkCount
        self.conceptGraphSampleSize = eventsSampleSize
        self.resultType = "conceptGraph"

# get a matrix of concepts and their dependencies
class RequestEventsConceptMatrix(RequestEvents):
    def __init__(self, conceptCount = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"], measure = "pmi", eventsSampleSize = 500):
        self.conceptMatrixConceptType = conceptTypes
        self.conceptMatrixConceptCount = conceptCount
        self.conceptMatrixConceptLang = conceptLangs
        self.conceptMatrixMeasure = measure
        self.conceptMatrixSampleSize = eventsSampleSize
        self.resultType = "conceptMatrix"

# get a list of top trending concepts and their daily trends over time
class RequestEventsTrendingConcepts(RequestEvents):
    def __init__(self, conceptCount = 10, conceptTypes = ["person", "org", "loc", "wiki"], conceptLangs = ["eng"]):
        self.trendingConceptsConceptType = conceptTypes
        self.trendingConceptsConceptCount = conceptCount
        self.trendingConceptsConceptLang = conceptLangs
        self.resultType = "trendingConcepts"

# get events and the dates they mention
class RequestEventsDateMentionAggr(RequestEvents):
    def __init__(self, minDaysApart = 0, minDateMentionCount = 5):
        self.dateMentionAggrMinDateMentionCount = minDateMentionCount
        self.dateMentionAggrMinDaysApart = minDaysApart
        self.resultType = "dateMentionAggr"

# get hierarchical clustering of events into smaller clusters.
class RequestEventsEventClusters(RequestEvents):
    def __init__(self, keywordCount = 30, conceptLangs = ["eng"], maxEventsToCluster = 10000):
        self.eventClustersKeywordCount = keywordCount
        self.eventClustersConceptLang = conceptLangs
        self.eventClustersMaxEventsToCluster = maxEventsToCluster
        self.resultType = "eventClusters"

# get distribution of events into dmoz categories
class RequestEventsCategoryAggr(RequestEvents):
    def __init__(self):
        self.resultType = "categoryAggr"

# get list of recently changed events
class RequestEventsRecentActivity(RequestEvents):
    def __init__(self, maxEventCount = 60, maxMinsBack = 10 * 60, lastEventActivityId = 0, lang = "eng", eventsWithLocationOnly = True, eventsWithLangOnly = False, minAvgCosSim = 0):
        self.eventsRecentActivityMaxEventCount = maxEventCount
        self.eventsRecentActivityMaxMinsBack = maxMinsBack
        self.eventsRecentActivityLastEventActivityId = lastEventActivityId
        self.eventsRecentActivityEventLang = lang                                   # the language in which title should be returned
        self.eventsRecentActivityEventsWithLocationOnly = eventsWithLocationOnly    # return only events for which we've recognized their location
        self.eventsRecentActivityEventsWithLangOnly = eventsWithLangOnly            # return only event that have a cluster at least in the lang language
        self.eventsRecentActivityMinAvgCosSim = minAvgCosSim                        # the minimum avg cos sim of the events to be returned (events with lower quality should not be included)
        self.resultType = "recentActivity"


# #####################################
# #####################################
class RequestArticles(RequestBase):
    def __init__(self):
        self.resultType = None;

# return a list of event details
class RequestArticlesInfo(RequestArticles):
    def __init__(self, page = 0, count = 20, sortBy = "date", sortByAsc = False, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], bodyLen = 300, 
                 # what info about articles to return:
                 **kwargs):
        self.articlesPage = page
        self.articlesCount = count
        self.articlesSortBy = sortBy        # date, id, cosSim, fq
        self.articlesSortByAsc = sortByAsc
        self.articlesBodyLen = bodyLen;
        self.articlesConceptLang = conceptLang
        self.articlesConceptTypes = conceptTypes
        
        self._parseArticleFlags("articles", **kwargs);
                
        self.resultType = "articles"
        
# return a list of event uris
class RequestArticlesUriList(RequestArticles):
    def __init__(self):
        self.resultType = "uriList"

# get time distribution of resulting articles
class RequestArticlesTimeAggr(RequestArticles):
    def __init__(self):
        self.resultType = "timeAggr"

# get aggreate of categories of resulting articles
class RequestArticlesCategoryAggr(RequestArticles):
    def __init__(self, articlesSampleSize = 20000):
        self.categoryAggrSampleSize = articlesSampleSize
        self.resultType = "categoryAggr"

# get aggreate of concepts of resulting articles
class RequestArticlesConceptAggr(RequestArticles):
    def __init__(self, conceptLang = ["eng"], conceptTypes = ["person", "org", "loc", "wiki"], conceptCount = 25, articlesSampleSize = 1000):
        self.conceptAggrConceptLang = conceptLang
        self.conceptAggrConceptType = conceptTypes
        self.conceptAggrConceptCount = conceptCount
        self.conceptAggrSampleSize = articlesSampleSize        
        self.resultType = "conceptAggr"

# get aggreate of sources of resulting articles
class RequestArticlesSourceAggr(RequestArticles):
    def __init__(self):
        self.resultType = "sourceAggr"

# get aggreate of sources of resulting articles
class RequestArticlesKeywordAggr(RequestArticles):
    def __init__(self, lang = "eng", count = 50):
        self.keywordAggrLang = articlesSampleSize
        self.keywordAggrCount = count
        self.resultType = "keywordAggr"
        
# get aggreate of sources of resulting articles
class RequestArticlesConceptMatrix(RequestArticles):
    def __init__(self, count = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLang = ["eng"], measure = "pmi", sampleSize = 500):
        self.conceptMatrixConceptCount = count
        self.conceptMatrixConceptLang = conceptLang
        self.conceptMatrixConceptType = conceptTypes
        self.conceptMatrixSampleSize = sampleSize
        self.conceptMatrixMeasure = measure             # pmi (pointwise mutual information), pairTfIdf (pair frequence * IDF of individual concepts), chiSquare
        self.resultType = "conceptMatrix"

# get concept graph of resulting articles
class RequestArticlesConceptGraph(RequestArticles):
    def __init__(self, count = 25, conceptTypes = ["person", "org", "loc", "wiki"], conceptLang = ["eng"], linkCount = 50, sampleSize = 500):
        self.conceptGraphConceptCount = count
        self.conceptGraphConceptLang = conceptLang
        self.conceptGraphConceptType = conceptTypes
        self.conceptGraphSampleSize = sampleSize
        self.conceptGraphLinkCount = linkCount
        self.resultType = "conceptGraph"

# get trending of concepts in the resulting articles
class RequestArticlesTrendingConcepts(RequestArticles):
    def __init__(self, count = 25, conceptLang = ["eng"]):
        self.trendingConceptsConceptCount = count
        self.trendingConceptsConceptLang = conceptLang
        self.resultType = "trendingConcepts"

# get trending of concepts in the resulting articles
class RequestArticlesTrendingConcepts(RequestArticles):
    def __init__(self):
        self.resultType = "dateMentionAggr"

# get the list of articles that were added recently
class RequestArticlesRecentActivity(RequestArticles):
    def __init__(self, maxArticleCount = 60, maxMinsBack = 10 * 60, lastArticleActivityId = 0, articlesWithLocationOnly = True):
        self.articleRecentActivityMaxArticleCount  = maxArticleCount
        self.articleRecentActivityMaxMinsBack = maxMinsBack
        self.articleRecentActivityLastArticleActivityId  = lastArticleActivityId
        self.articleRecentActivityArticlesWithLocationOnly  = articlesWithLocationOnly
        self.resultType = "recentActivity"
        
# #####################################
# #####################################

# object that can access event registry 
class EventRegistry(object):
    def __init__(self, host = "http://beta.eventregistry.org"):
        self.Host = host
        self._lastException = None

    def getLastException(self):
        return self._lastException;

    def _jsonRequest(self, methodUrl, paramDict):
        self._lastException = None;
        try:
            params = urllib.urlencode(paramDict, True)
            req = urllib2.Request(self.Host + methodUrl + "?" + params)
            respInfo = urllib2.urlopen(req).read()
            respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex;
            return None

    # main method for executing the search queries. 
    def execQuery(self, query, convertToDict = True):
        self._lastException = None;
        try:
            params = query._encode()
            req = urllib2.Request(self.Host + query._getPath() + "?" + params)
            respInfo = urllib2.urlopen(req).read()
            if convertToDict:
                respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex
            return None

    # return a list of concepts that contain the given prefix
    # valid sources: concepts, entities, person, loc, org, wiki
    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", labelLang = "eng", page = 0, count = 20):      
        return self._jsonRequest("/json/suggestConcepts", { "prefix": prefix, "source": sources, "lang": lang, "labelLang": labelLang, "page": page, "count": count })
        
    # return a list of news sources that match the prefix
    def suggestNewsSources(self, prefix, page = 0, count = 20):
        return self._jsonRequest("/json/suggestSources", { "prefix": prefix, "page": page, "count": count })
        
    # return a list of locations (cities or countries) that contain the prefix
    def suggestLocations(self, prefix, count = 20, lang = "eng", source = ["city", "country"]):
        return self._jsonRequest("/json/suggestLocations", { "prefix": prefix, "count": count, "source": source, "lang": lang })
        
    # return a list of dmoz categories that contain the prefix
    def suggestCategories(self, prefix, page = 0, count = 20):
        return self._jsonRequest("/json/suggestCategories", { "prefix": prefix, "page": page, "count": count })
        
    # return a concept uri that is the best match for the given concept label
    def getConceptUri(self, conceptLabel, lang = "eng"):
        matches = self.suggestConcepts(conceptLabel, lang = lang)
        if len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None

    # return a location uri that is the best match for the given location label
    def getLocationUri(self, locationLabel, lang = "eng"):
        matches = self.suggestLocations(locationLabel, lang = lang);
        if len(matches) > 0 and matches[0].has_key("wikiUri"):
            return matches[0]["wikiUri"]
        return None;

    # return a category uri that is the best match for the given label
    def getCategoryUri(self, categoryLabel):
        matches = self.suggestCategories(categoryLabel);
        if len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None;

    def getNewsSourceUri(self, sourceName):
        matches = self.suggestNewsSources(sourceName);
        if len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None;

    # return info about recently modified articles
    def getRecentEvents(self, maxEventCount = 60, maxMinsBack = 10 * 60, lang = "eng", eventsWithLocationOnly = True, eventsWithLangOnly = False, lastStoryActivityId = 0, eventUpdatesAfter = ""):
        params = {  "action": "getEventActivity",
                    "eventCount": maxEventCount,                     # max number of returned events
                    "eventsWithLocationOnly": eventsWithLocationOnly, # return only events that have a known geo location
                    "eventLang": lang,                                # language of the event to return
                    "eventsWithLangOnly": eventsWithLangOnly,         # return only events that have at least a story in the specified lang language
                    "lastStoryActivityId": lastStoryActivityId,       # one criteria for telling the system about what was the latest activity already received (obtained by previous calls to this method)
                    "eventUpdatesAfter": eventUpdatesAfter            # include only events changed after a specified date (format YYYY-MM-DD)
                  }
        return self._jsonRequest("/json/overview", params)

    # return info about recently added articles
    def getRecentArticles(self, maxArticleCount = 60, articlesWithLocationOnly = True, lastArticleActivityId = 0, articleUpdatesAfter = ""):
        params = {  "action": "getArticleActivity",
                    "articleCount": maxArticleCount,                     # max number of returned events
                    "articlesWithLocationOnly": articlesWithLocationOnly, # return only articles that have a known geo location
                    "lastArticleActivityId": lastArticleActivityId,       # one criteria for telling the system about what was the latest activity already received (obtained by previous calls to this method)
                    "articleUpdatesAfter": articleUpdatesAfter            # include only articles added after the specified date-time (format "YYYY-MM-DD HH:MM:SS")
                  }
        return self._jsonRequest("/json/overview", params)

    def getRecentStats(self):
        return self._jsonRequest("/json/overview", { "action": "getRecentStats"})


if __name__ == '__main__':
    fileDir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(fileDir)
    er = EventRegistry(host = "http://beta.eventregistry.org")
    #er = EventRegistry(host = "http://localhost:8090")

    q = QueryEvents()
    q.addConcept(er.getConceptUri("Obama"))                 # get events related to obama
    q.addCategory(er.getCategoryUri("society issues"))      # and are related to issues in society
    q.addNewsSource(er.getNewsSourceUri("bbc"))             # and have been reported by BBC
    q.addRequestedResult(RequestEventsUriList())            # return uris of all events
    q.addRequestedResult(RequestEventsInfo(page = 0, count = 30))   # return event details for first 30 events
    q.addRequestedResult(RequestEventsConceptAggr())        # compute concept aggregate on the events
    res = er.execQuery(q)

    q = QueryEvents();
    q.addLocation(er.getLocationUri("Berlin"))
    q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
    q.addRequestedResult(RequestEventsTrendingConcepts(40, conceptTypes=["person"]))
    q.addRequestedResult(RequestEventsCategoryAggr())
    q.addRequestedResult(RequestEventsInfo())
    res = er.execQuery(q)

    # get info about event with uri "123"
    q = QueryEvent("123");
    q.addRequestedResult(RequestEventInfo(["eng", "spa", "slv"]))
    q.addRequestedResult(RequestEventArticles(0, 10))        # get 10 articles about the event (any language is ok) that are closest to the center of the event
    q.addRequestedResult(RequestEventArticleTrend())
    q.addRequestedResult(RequestEventKeywordAggr())
    eventRes = er.execQuery(q);

    if (eventRes.has_key("articles") and len(eventRes["articles"]) > 0):
        articleUris = [art["uri"] for art in eventRes["articles"]["results"][:2]]  # take only first two articles
        # query info about specific articles
        qa = QueryArticle(articleUris);
        qa.addRequestedResult(RequestArticleInfo())                 # get all info about the specified article
        qa.addRequestedResult(RequestArticleDuplicatedArticles())   # get info about duplicated articles for the specified two articles
        articleRes = er.execQuery(qa);
            
    q = QueryArticles();
    q.setDateLimit(datetime.date(2014, 4, 16), datetime.date(2014, 4, 28))
    q.addKeyword("apple")
    q.addKeyword("iphone")
    q.addRequestedResult(RequestArticlesInfo(page=0, count = 30));
    res = er.execQuery(q)

    # recent activity
    q = QueryEvents()
    q.addConcept(er.getConceptUri("Obama"))
    q.addRequestedResult(RequestEventsRecentActivity())     # get most recently updated events related to obama
    res = er.execQuery(q)

    q = QueryArticles()
    q.addConcept(er.getConceptUri("Obama"))
    q.addRequestedResult(RequestArticlesRecentActivity())     # get most recently added articles related to obama
    res = er.execQuery(q)

    recentEvents = er.getRecentEvents()
    recentArticles = er.getRecentArticles()

    print er.getRecentStats()

    #print res;