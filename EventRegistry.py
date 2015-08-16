"""
classes responsible for obtaining results from the Event Registry
"""
import os, sys, urllib2, urllib, json, re;
from cookielib import CookieJar
from ERBase import *
from ERReturnInfo import *
from ERQueryEvents import *
from ERQueryEvent import *
from ERQueryArticles import *
from ERQueryArticle import *
                

# #####################################
# #####################################

"""
trending information is computed by comparing how frequently are individual concepts/categories
mentioned in the articles. By default trends are computed by comparing the total number of mentions of a concept/category
in the last two days compared to the number of mentions in the two weeks before. The trend for each concept/category
is computed as the Pearson residual. The returned concepts/categories are the ones that have the highest residual.
"""
class TrendsBase(ParamsBase):
    def _getPath(self):
        return "/json/trends"

# get currently top trending concepts
class GetTrendingConcepts(TrendsBase):
    def __init__(self, 
                 source = "news", # source information from which to compute top trends. Possible values: "news", "social"
                 count = 20):     # number of top trends to return
        ParamsBase.__init__(self)
        self._setVal("action", "getTrendingConcepts")
        self._setVal("source", source)
        self._setVal("conceptCount", count)


# get currently top trending categories
class GetTrendingCategories(TrendsBase):
    def __init__(self, 
                 source = "news",   # source information from which to compute top trends. Possible values: "news", "social"
                 count = 20):       # number of top trends to return
        ParamsBase.__init__(self)
        self._setVal("action", "getTrendingCategories")
        self._setVal("source", source)
        self._setVal("categoryCount", count)

# get currently top trending items for which the users provided the data
# this data can be stock prices, energy prices, etc...
class GetTrendingCustomItems(TrendsBase):
    def __init__(self, source = "news", count = 20):
        ParamsBase.__init__(self)
        self._setVal("action", "getTrendingCustom")
        self._setVal("source", source)
        self._setVal("conceptCount", count)

# get currently top trending groups of concepts
# a group can be identified by the concept type or by a concept class uri
class GetTrendingConceptGroups(TrendsBase):
    def __init__(self, 
                 source = "news",   # source information from which to compute top trends. Possible values: "news", "social"
                 count = 20,        # number of top trends to return
                 **kwds):     
        ParamsBase.__init__(self)
        self._setVal("action", "getConceptTrendGroups")
        self._setVal("source", source)
        self._setVal("conceptCount", count)

        self._parseConceptFlags("concept", **kwargs);

    # request trending of concepts of specified types
    def getConceptTypeGroups(types = ["person", "org", "loc", "wiki"]):
        self._setVal("conceptType", types)

    # request trending of concepts assigned to the specified concept classes
    def getConceptClassUris(conceptClassUris):
        self._setVal("conceptClassUri", conceptClassUris)


# #####################################
# #####################################

"""
Using the bottom classes you can obtain information about articles and events that 
were shared the most on social media (Twitter and Facebook) on a particular day.
Given a date, articles published on that date are checked and top shared ones are returned. For an event,
events on that day are checked and top shared ones are returned.
Social score for an article is computed as the sum of shares on facebook and twitter.
Social score for an event is computed by checking 30 top shared articles in the event and averaging their social scores.
"""

class DailySharesBase(ParamsBase):
    def _getPath(self):
        return "/json/topDailyShares"

# get top shared articles for today or any other day
class GetTopSharedArticles(DailySharesBase):
    def __init__(self, 
                 date = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count = 20):     # number of top shared articles to return
        ParamsBase.__init__(self)
        self._setVal("action", "getArticles")
        self._setVal("count", count)
        
        if date == None:
            date = datetime.date.today();
        self._setDateVal("date", date)
        
        
# get top shared events for today or any other day
class GetTopSharedEvents(DailySharesBase):
    def __init__(self, 
                 date = None,     # specify the date (either in YYYY-MM-DD or datetime.date format) for which to return top shared articles. If None then today is used
                 count = 20):     # number of top shared articles to return
        ParamsBase.__init__(self)
        self._setProp("action", "getEvents")
        self._setProp("count", count)
        
        if date == None:
            date = datetime.date.today();
        self._setDateVal("date", date)
        

# #####################################
# #####################################

# object that can access event registry 
class EventRegistry(object):
    def __init__(self, host = "http://eventregistry.org", logging = False, 
                 minDelayBetweenRequests = 0.5,     # the minimum number of seconds between individual api calls
                 repeatFailedRequestCount = -1,    # if a request fails (for example, because ER is down), what is the max number of times the request should be repeated (-1 for indefinitely)
                 verboseOutput = False):            # if true, additional info about query times etc will be printed to console
        self.Host = host
        self._lastException = None
        self._logRequests = logging
        self._erUsername = None
        self._erPassword = None
        self._minDelayBetweenRequests = minDelayBetweenRequests
        self._repeatFailedRequestCount = repeatFailedRequestCount
        self._verboseOutput = verboseOutput
        self._lastQueryTime = time.time()

        cj = CookieJar()
        self._reqOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        # if there is a settings.json file in the directory then try using it to login to ER
        currPath = os.path.split(__file__)[0]
        settPath = os.path.join(currPath, "settings.json")
        if os.path.exists(settPath):
            settings = json.load(open(settPath))
            self.login(settings.get("username", ""), settings.get("password", ""), False)
        
    # ensure that queries are not made too fast
    def _sleepIfNecessary(self):
        t = time.time();
        if t - self._lastQueryTime < self._minDelayBetweenRequests:
            time.sleep(self._minDelayBetweenRequests - (t - self._lastQueryTime))
        self._lastQueryTime = t

     # make the request - repeat it _repeatFailedRequestCount times, if they fail (indefinitely if _repeatFailedRequestCount = -1)
    def _getUrlResponse(self, url, data = None):
        tryCount = 0
        while self._repeatFailedRequestCount < 0 or tryCount < self._repeatFailedRequestCount:
            tryCount += 1
            try:
                startT = datetime.datetime.now()
                req = urllib2.Request(url, data)
                respInfo = self._reqOpener.open(req).read()
                endT = datetime.datetime.now()
                if self._verboseOutput:
                    self.printConsole("request took %.3f sec" % ((endT-startT).total_seconds()))
                return respInfo
            except Exception as ex:
                self._lastException = ex
                self.printLastException()
                time.sleep(5)   # sleep for 5 seconds on error
        return None

    def setLogging(val):
        self._logRequests = val

    def getLastException(self):
        return self._lastException

    def printLastException(self):
        print str(self._lastException)

    # print time prefix + text
    def printConsole(self, text):
        print time.strftime("%H:%M:%S") + " " + str(text)

    # login the user. without logging in, the user is limited to 10.000 queries per day. 
    # if you have a registered account, the number of allowed requests per day can be higher, depending on your subscription plan
    def login(self, username, password, throwExceptOnFailure = True):
        self._erUsername = username
        self._erPassword = password
        req = urllib2.Request(self.Host + "/login", urllib.urlencode({ "email": username, "pass": password }))
        respInfo = self._reqOpener.open(req).read()
        respInfo = json.loads(respInfo);
        if throwExceptOnFailure and respInfo.has_key("error"):
            raise Exception(respInfo["error"]);
        return respInfo;

    # make a get request
    def jsonRequest(self, methodUrl, paramDict):
        self._sleepIfNecessary();
        self._lastException = None

        # add user credentials if specified
        if self._erUsername != None and self._erPassword != None:
            paramDict["erUsername"] = self._erUsername
            paramDict["erPassword"] = self._erPassword
        
        try:
            params = urllib.urlencode(paramDict, True)
            url = self.Host + methodUrl + "?" + params
            if self._logRequests:
                with open("requests_log.txt", "a") as log:
                    log.write(url + "\n")
            # make the request
            respInfo = self._getUrlResponse(url)
            if respInfo != None:
                respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex;
            return None

    # make a post request where all parameters are encoded in the body - use for requests with many parameters
    def jsonPostRequest(self, methodUrl, paramDict):
        self._sleepIfNecessary();
        self._lastException = None

        # add user credentials if specified
        if self._erUsername != None and self._erPassword != None:
            paramDict["erUsername"] = self._erUsername
            paramDict["erPassword"] = self._erPassword
        
        try:
            params = urllib.urlencode(paramDict, True)
            url = self.Host + methodUrl
            if self._logRequests:
                with open("requests_log.txt", "a") as log:
                    log.write(url + "\n")
            # make the request
            respInfo = self._getUrlResponse(url, params)
            if respInfo != None:
                respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex;
            return None
            
    # main method for executing the search queries. 
    def execQuery(self, query, convertToDict = True):
        self._sleepIfNecessary();
        self._lastException = None

        try:
            params = query._encode(self._erUsername, self._erPassword)
            url = self.Host + query._getPath() + "?" + params
            if self._logRequests:
                with open("requests_log.txt", "a") as log:
                    log.write(url + "\n")
            # make the request
            respInfo = self._getUrlResponse(url)
            if respInfo != None and convertToDict:
                respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex
            return None

    # return a list of concepts that contain the given prefix
    # valid sources: person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki), conceptClass, conceptFolder
    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", labelLang = "eng", page = 0, count = 20):      
        return self.jsonRequest("/json/suggestConcepts", { "prefix": prefix, "source": sources, "lang": lang, "labelLang": labelLang, "page": page, "count": count})
        
    # return a list of news sources that match the prefix
    def suggestNewsSources(self, prefix, page = 0, count = 20):
        return self.jsonRequest("/json/suggestSources", { "prefix": prefix, "page": page, "count": count })
        
    # return a list of geo locations (cities or countries) that contain the prefix
    def suggestLocations(self, prefix, count = 20, lang = "eng", source = ["place", "country"]):
        return self.jsonRequest("/json/suggestLocations", { "prefix": prefix, "count": count, "source": source, "lang": lang })
        
    # return a list of dmoz categories that contain the prefix
    def suggestCategories(self, prefix, page = 0, count = 20):
        return self.jsonRequest("/json/suggestCategories", { "prefix": prefix, "page": page, "count": count })

    # return a list of dmoz categories that contain the prefix
    def suggestConceptClasses(self, prefix, lang = "eng", labelLang = "eng", page = 0, count = 20):
        return self.jsonRequest("/json/suggestConceptClasses", { "prefix": prefix, "lang": lang, "labelLang": labelLang, "page": page, "count": count })
        
    # return a concept uri that is the best match for the given concept label
    def getConceptUri(self, conceptLabel, lang = "eng", sources = ["concepts"]):
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches != None and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None

    # return a location uri that is the best match for the given location label
    def getLocationUri(self, locationLabel, lang = "eng", source = ["place", "country"]):
        matches = self.suggestLocations(locationLabel, lang = lang, source = source);
        if matches != None and len(matches) > 0 and matches[0].has_key("wikiUri"):
            return matches[0]["wikiUri"]
        return None;

    # return a category uri that is the best match for the given label
    def getCategoryUri(self, categoryLabel):
        matches = self.suggestCategories(categoryLabel);
        if matches != None and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None;

    # return the news source that best matches the source name
    def getNewsSourceUri(self, sourceName):
        matches = self.suggestNewsSources(sourceName);
        if matches != None and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None;
    
    # return a uri of the concept class that is the best match for the given label
    def getConceptClass(self, classLabel, lang = "eng"):
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches != None and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None    

    ### return info about recently modified events
    # maxEventCount determines the maximum number of events to return in a single call (max 250)
    # maxMinsBack sets how much in the history are we interested to look
    # set mandatoryLang if you wish to only get events covered at least by the specified language
    # if mandatoryLocation == True then return only events that have a known geographic location
    # lastActivityId is another way of settings how much in the history are we interested to look. Set when you have repeated calls of the method. Set it to lastActivityId obtained in the last response
    def getRecentEvents(self, 
                        maxEventCount = 60, 
                        maxMinsBack = 10 * 60, 
                        mandatoryLang = None, 
                        mandatoryLocation = True, 
                        lastActivityId = 0, 
                        returnInfo = ReturnInfo()):
        assert maxEventCount <= 1000
        params = {  "action": "getRecentActivity",
                    "addEvents": True,
                    "addArticles": False,
                    "recentActivityEventsMaxEventCount": maxEventCount,             # max number of returned events
                    "recentActivityEventsMaxMinsBack": maxMinsBack,
                    "recentActivityEventsMandatoryLocation": mandatoryLocation,     # return only events that have a known geo location
                    "recentActivityEventsLastActivityId": lastActivityId       # one criteria for telling the system about what was the latest activity already received (obtained by previous calls to this method)
                  }
        # return only events that have at least a story in the specified language
        if mandatoryLang != None:
            params["recentActivityEventsMandatoryLang"] = mandatoryLang;

        returnParams = returnInfo.getParams("recentActivityEvents")
        params.update(returnParams)

        return self.jsonRequest("/json/overview", params)

    ### return info about recently added articles
    # maxArticleCount determines the maximum number of articles to return in a single call (max 250)
    # maxMinsBack sets how much in the history are we interested to look
    # if mandatorySourceLocation == True then return only articles from sources for which we know geographic location
    # lastActivityId is another way of settings how much in the history are we interested to look. Set when you have repeated calls of the method. Set it to lastActivityId obtained in the last response
    def getRecentArticles(self, 
                          maxArticleCount = 60, 
                          maxMinsBack = 10 * 60, 
                          mandatorySourceLocation = True, 
                          lastActivityId = 0, 
                          returnInfo = ReturnInfo()):
        assert maxArticleCount <= 1000
        params = {
            "action": "getRecentActivity",
            "addEvents": False,
            "addArticles": True,
            "recentActivityArticlesMaxMinsBack": maxMinsBack,
            "recentActivityArticlesMaxArticleCount": maxArticleCount,                   # max number of returned events
            "recentActivityArticlesMandatorySourceLocation": mandatorySourceLocation,   # return only articles that have a known geo location
            "recentActivityArticlesLastActivityId": lastActivityId                      # one criteria for telling the system about what was the latest activity already received (obtained by previous calls to this method)
            }

        returnParams = returnInfo.getParams("recentActivityArticles")
        params.update(returnParams)
        return self.jsonRequest("/json/overview", params)

    # get some stats about recently imported articles and events
    def getRecentStats(self):
        return self.jsonRequest("/json/overview", { "action": "getRecentStats"})
