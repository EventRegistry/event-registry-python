"""
classes responsible for obtaining results from the Event Registry
"""
import os, sys, traceback, urllib2, urllib, json, re, requests, time
import urllib, urllib2, threading
#from cookielib import CookieJar
from Base import *
from EventForText import *
from ReturnInfo import *
from QueryEvents import *
from QueryEvent import *
from QueryArticles import *
from QueryArticle import *
from QueryStory import *
from Correlations import *
from Counts import *
from DailyShares import *
from Info import *
from Recent import *
from Trends import *

class EventRegistry(object):
    """
    the core object that is used to access any data in Event Registry
    it is used to send all the requests and queries
    """
    def __init__(self, host = None, logging = False,
                 minDelayBetweenRequests = 0.5,     # the minimum number of seconds between individual api calls
                 repeatFailedRequestCount = -1,    # if a request fails (for example, because ER is down), what is the max number of times the request should be repeated (-1 for indefinitely)
                 verboseOutput = False):            # if true, additional info about query times etc will be printed to console
        self._host = host
        self._lastException = None
        self._logRequests = logging
        self._minDelayBetweenRequests = minDelayBetweenRequests
        self._repeatFailedRequestCount = repeatFailedRequestCount
        self._verboseOutput = verboseOutput
        self._lastQueryTime = time.time()
        self._cookies = None
        self._dailyAvailableRequests = -1
        self._remainingAvailableRequests = -1

        # lock for making sure we make one request at a time - requests module otherwise sometimes returns incomplete json objects
        self._lock = threading.Lock()
        self._reqSession = requests.Session()
                       
        # if there is a settings.json file in the directory then try using it to login to ER
        # and to read the host name from it (if custom host is not specified)
        currPath = os.path.split(__file__)[0]
        settPath = os.path.join(currPath, "settings.json")
        if os.path.exists(settPath):
            settings = json.load(open(settPath))
            self._host = host or settings.get("host", "http://eventregistry.org")
            if settings.has_key("username") and settings.has_key("password"):
                self.login(settings.get("username", ""), settings.get("password", ""), False)
        else:
            self._host = host or "http://eventregistry.org"
        self._requestLogFName = os.path.join(currPath, "requests_log.txt")

        #cj = CookieJar()
        #self._reqOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        print "Event Registry host: %s" % (self._host)

    def setLogging(self, val):
        """should all requests be logged to a file or not?"""
        self._logRequests = val

    def getHost(self):
        return self._host

    def getLastException(self):
        """return the last exception"""
        return self._lastException

    def printLastException(self):
        print str(self._lastException)

    def format(self, obj):
        """return a string containing the object in a pretty formated version"""
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

    def printConsole(self, text):
        """print time prefix + text to console"""
        print time.strftime("%H:%M:%S") + " " + str(text)

    def getRemainingAvailableRequests(self):
        """get the number of requests that are still available for the user today"""
        return self._remainingAvailableRequests

    def getDailyAvailableRequests(self):
        """get the total number of requests that the user can make in a day"""
        return self._dailyAvailableRequests;


    def login(self, username, password, throwExceptOnFailure = True):
        """
        login the user. without logging in, the user is limited to 10.000 queries per day. 
        if you have a registered account, the number of allowed requests per day can be higher, depending on your subscription plan
        """
        respInfoObj = None
        try:
            respInfo = self._reqSession.post(self._host + "/login", data = { "email": username, "pass": password })
            self._cookies = respInfo.cookies
            respInfoText = respInfo.text
            respInfoObj = json.loads(respInfoText)
            if throwExceptOnFailure and respInfoObj.has_key("error"):
                raise Exception(respInfo["error"])
            elif respInfoObj.has_key("info"):
                print "Successfully logged in with user %s" % (username)
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ConnectionError) and throwExceptOnFailure:
                raise ex
        finally:
            return respInfoObj
         
           
    def execQuery(self, query):
        """main method for executing the search queries."""
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the request
        respInfo = self.jsonRequest(query._getPath(), allParams)
        return respInfo


    def jsonRequest(self, methodUrl, paramDict, customLogFName = None):
        """
        make a request for json data. repeat it _repeatFailedRequestCount times, if they fail (indefinitely if _repeatFailedRequestCount = -1)
        @param methodUrl: url on er (e.g. "/json/article")
        @param paramDict: optional object containing the parameters to include in the request (e.g. { "articleUri": "123412342" }).
        """
        self._sleepIfNecessary()
        self._lastException = None

        self._lock.acquire()
        if self._logRequests:
            try:
                with open(customLogFName or self._requestLogFName, "a") as log:
                    if paramDict != None:
                        log.write("# " + json.dumps(paramDict) + "\n")
                    log.write(methodUrl + "\n")                
            except Exception as ex:
                self._lastException = ex
        
        tryCount = 0
        returnData = None
        while self._repeatFailedRequestCount < 0 or tryCount < self._repeatFailedRequestCount:
            tryCount += 1
            try:
                startT = datetime.datetime.now()
                url = self._host + methodUrl;
                
                #data = urllib.urlencode(data, True)
                #req = urllib2.Request(url, data)
                #respInfoContent = self._reqOpener.open(req).read()
                
                # make the request
                respInfo = self._reqSession.post(url, json = paramDict, cookies = self._cookies)
                if respInfo.status_code in [401, 429, 500, 503]:
                    raise Exception(respInfo.text)
                # remember the available requests
                self._dailyAvailableRequests = tryParseInt(respInfo.headers.get("x-ratelimit-limit", ""), val = -1)
                self._remainingAvailableRequests = tryParseInt(respInfo.headers.get("x-ratelimit-remaining", ""), val = -1)
                endT = datetime.datetime.now()
                if self._verboseOutput:
                    self.printConsole("request took %.3f sec. Response size: %.2fKB" % ((endT-startT).total_seconds(), len(respInfo.text) / 1024.0))
                try:
                    returnData = respInfo.json()
                    break
                except Exception as ex:
                    print "EventRegistry.jsonRequest(): Exception while parsing the returned json object. Repeating the query..."
                    open("invalidJsonResponse.json", "w").write(respInfo.text)
            except Exception as ex:
                self._lastException = ex
                print "EventRegistry.jsonRequest(): Exception while executing the request"
                self.printLastException()
                time.sleep(5)   # sleep for 5 seconds on error
        self._lock.release()
        return returnData


    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", conceptLang = "eng", page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of concepts that contain the given prefix
        valid sources: person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki), conceptClass, conceptFolder
        returned matching concepts are sorted based on their frequency of occurence in news (from most to least frequent)
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "source": sources, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count}
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestConcepts", params)
        

    def suggestNewsSources(self, prefix, page = 1, count = 20):
        """return a list of news sources that match the prefix"""
        assert page > 0, "page parameter should be above 0"
        return self.jsonRequest("/json/suggestSources", { "prefix": prefix, "page": page, "count": count })
        

    def suggestLocations(self, prefix, count = 20, lang = "eng", source = ["place", "country"], countryUri = None, sortByDistanceTo = None, returnInfo = ReturnInfo()):
        """
        return a list of geo locations (cities or countries) that contain the prefix
        if countryUri is provided then return only those locations that are inside the specified country
        if sortByDistanceto is provided then return the locations sorted by the distance to the (lat, long) provided in the tuple
        """
        params = { "prefix": prefix, "count": count, "source": source, "lang": lang, "countryUri": countryUri or "" }
        params.update(returnInfo.getParams())
        if sortByDistanceTo:
            assert isinstance(sortByDistanceTo, (tuple, list)), "sortByDistanceTo has to contain a tuple with latitude and longitude of the location"
            assert len(sortByDistanceTo) == 2, "The sortByDistanceTo should contain two float numbers"
            params["closeToLat"] = sortByDistanceTo[0]
            params["closeToLon"] = sortByDistanceTo[1]
        return self.jsonRequest("/json/suggestLocations", params)
        

    def suggestCategories(self, prefix, page = 1, count = 20, returnInfo = ReturnInfo()):
        """return a list of dmoz categories that contain the prefix"""
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestCategories", params)


    def suggestConceptClasses(self, prefix, lang = "eng", conceptLang = "eng", source = ["dbpedia", "custom"], page = 1, count = 20, returnInfo = ReturnInfo()):
        """return a list of dmoz categories that contain the prefix"""
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, source: source, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestConceptClasses", params)


    def suggestCustomConcepts(self, prefix, lang = "eng", conceptLang = "eng", page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of custom concepts that contain the given prefix
        custom concepts are the things (indicators, stock prices, ...) for which we import daily trending values that can be obtained using GetCounts class
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestCustomConcepts", params)
        

    def getConceptUri(self, conceptLabel, lang = "eng", sources = ["concepts"]):
        """
        return a concept uri that is the best match for the given concept label
        if there are multiple matches for the given conceptLabel, they are sorted based on their frequency of occurence in news (most to least frequent)
        """
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None


    def getLocationUri(self, locationLabel, lang = "eng", source = ["place", "country"], countryUri = None, sortByDistanceTo = None):
        """return a location uri that is the best match for the given location label"""
        matches = self.suggestLocations(locationLabel, lang = lang, source = source, countryUri = countryUri, sortByDistanceTo = sortByDistanceTo)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("wikiUri"):
            return matches[0]["wikiUri"]
        return None


    def getCategoryUri(self, categoryLabel):
        """return a category uri that is the best match for the given label"""
        matches = self.suggestCategories(categoryLabel)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None


    def getNewsSourceUri(self, sourceName):
        """return the news source that best matches the source name"""
        matches = self.suggestNewsSources(sourceName)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None
    

    def getConceptClassUri(self, classLabel, lang = "eng"):
        """return a uri of the concept class that is the best match for the given label"""
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None    


    def getConceptInfo(self, conceptUri, 
                       returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(
                           synonyms = True, image = True, description = True))):
        """return detailed information about a particular concept"""
        params = returnInfo.getParams()
        params.update({"uri": conceptUri, "action": "getInfo" })
        return self.jsonRequest("/json/concept", params)


    def getCustomConceptUri(self, label, lang = "eng"):
        """
        return a custom concept uri that is the best match for the given custom concept label
        note that for the custom concepts we don't have a sensible way of sorting the candidates that match the label
        if multiple candidates match the label we cannot guarantee which one will be returned
        """
        matches = self.suggestCustomConcepts(label, lang = lang)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None


    def getRecentStats(self):
        """get some stats about recently imported articles and events"""
        return self.jsonRequest("/json/overview", { "action": "getRecentStats"})

    
    def getArticleUris(self, articleUrls):
        """ 
        if you have article urls and you want to query them in ER you first have to
        obtain their uris in the ER. 
        @param articleUrls a single article url or a list of article urls
        @returns dict where key is article url and value is None (if article not found) or article uri
        """
        assert isinstance(articleUrls, (str, unicode, list)), "Expected a single article url or a list of urls"
        return self.jsonRequest("/json/articleMapper", { "articleUrl": articleUrls })


    def getLatestArticle(self, returnInfo = ReturnInfo()):
        """
        return information about the latest imported article
        """
        stats = self.getRecentStats()
        latestId = stats["totalArticleCount"]-1
        q = QueryArticle.queryById(latestId)
        q.addRequestedResult(RequestArticleInfo(returnInfo))
        ret = self.execQuery(q)
        if ret and len(ret.keys()) > 0:
            return ret[ret.keys()[0]].get("info")
        return None
    
    # utility methods

    def _sleepIfNecessary(self):
        """ensure that queries are not made too fast"""
        t = time.time()
        if t - self._lastQueryTime < self._minDelayBetweenRequests:
            time.sleep(self._minDelayBetweenRequests - (t - self._lastQueryTime))
        self._lastQueryTime = t



class ArticleMapper:
    """ 
    create instance of article mapper
    it will map from article urls to article uris
    the mappings can be remembered so it will not repeat requests for the same article urls
    """
    def __init__(self, er, rememberMappings = True):
        self._er = er
        self._articleUrlToUri = {}
        self._rememberMappings = rememberMappings
        
    def getArticleUri(self, articleUrl):
        if self._articleUrlToUri.has_key(articleUrl):
            return self._articleUrlToUri[articleUrl]
        res = self._er.getArticleUris(articleUrl)
        if res and res.has_key(articleUrl):
            if self._rememberMappings:
                self._articleUrlToUri[articleUrl] = res[articleUrl]
            return res[articleUrl]
