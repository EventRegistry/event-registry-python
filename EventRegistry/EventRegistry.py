"""
classes responsible for obtaining results from the Event Registry
"""
import os, sys, urllib2, urllib, json, re, requests
from Base import *
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
        self._erUsername = None
        self._erPassword = None
        self._lastException = None
        self._logRequests = logging
        self._minDelayBetweenRequests = minDelayBetweenRequests
        self._repeatFailedRequestCount = repeatFailedRequestCount
        self._verboseOutput = verboseOutput
        self._lastQueryTime = time.time()
               
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

        print "Event Registry host: %s" % (self._host)

        
    def _sleepIfNecessary(self):
        """ensure that queries are not made too fast"""
        t = time.time()
        if t - self._lastQueryTime < self._minDelayBetweenRequests:
            time.sleep(self._minDelayBetweenRequests - (t - self._lastQueryTime))
        self._lastQueryTime = t

    def _getUrlResponse(self, methodUrl, data = None):
        """
        make the request - repeat it _repeatFailedRequestCount times, 
        if they fail (indefinitely if _repeatFailedRequestCount = -1)
        """
        if self._logRequests:
            with open(self._requestLogFName, "a") as log:
                if data != None:
                    log.write("# " + json.dumps(data) + "\n")
                log.write(methodUrl + "\n")                
        tryCount = 0
        while self._repeatFailedRequestCount < 0 or tryCount < self._repeatFailedRequestCount:
            tryCount += 1
            try:
                startT = datetime.datetime.now()
                url = self._host + methodUrl;
                respInfo = requests.get(url, data = data).text
                endT = datetime.datetime.now()
                if self._verboseOutput:
                    self.printConsole("request took %.3f sec. Response size: %.2fKB" % ((endT-startT).total_seconds(), len(respInfo) / 1024.0))
                return respInfo
            except Exception as ex:
                self._lastException = ex
                self.printLastException()
                time.sleep(5)   # sleep for 5 seconds on error
        return None

    def setLogging(val):
        """should all requests be logged to a file or not?"""
        self._logRequests = val

    def getLastException(self):
        """return the last exception"""
        return self._lastException

    def printLastException(self):
        print str(self._lastException)

    def prettyFormatObj(self, obj):
        """return an object in a pretty printed version"""
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

    def printConsole(self, text):
        """print time prefix + text to console"""
        print time.strftime("%H:%M:%S") + " " + str(text)

    def login(self, username, password, throwExceptOnFailure = True):
        """
        login the user. without logging in, the user is limited to 10.000 queries per day. 
        if you have a registered account, the number of allowed requests per day can be higher, depending on your subscription plan
        """
        self._erUsername = username
        self._erPassword = password
        respInfo = None
        try:
            respInfo = requests.post(self._host + "/login", data = { "email": username, "pass": password }).text
            respInfo = json.loads(respInfo)
            if throwExceptOnFailure and respInfo.has_key("error"):
                raise Exception(respInfo["error"])
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ConnectionError) and throwExceptOnFailure:
                raise ex
        finally:
            return respInfo
            
    def execQuery(self, query, convertToDict = True):
        """main method for executing the search queries."""
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the request
        respInfo = self.jsonRequest(query._getPath(), allParams, convertToDict)
        return respInfo


    def jsonRequest(self, methodUrl, paramDict, convertToDict = True):
        """
        make a request for json data
        @param methodUrl: url on er (e.g. "/json/article")
        @param paramDict: optional object containing the parameters to include in the request (e.g. { "articleUri": "123412342" }).
        @param convertToDict: should the returned result be first parsed to a python object?
        """
        self._sleepIfNecessary()
        self._lastException = None

        # add user credentials if specified
        if self._erUsername != None and self._erPassword != None:
            paramDict["erUsername"] = self._erUsername
            paramDict["erPassword"] = self._erPassword
        
        try:
            # make the request
            respInfo = self._getUrlResponse(methodUrl, paramDict)
            if respInfo != None:
                respInfo = json.loads(respInfo)
            return respInfo
        except Exception as ex:
            self._lastException = ex
            return None

    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", conceptLang = "eng", page = 0, count = 20):
        """
        return a list of concepts that contain the given prefix
        valid sources: person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki), conceptClass, conceptFolder
        """
        return self.jsonRequest("/json/suggestConcepts", { "prefix": prefix, "source": sources, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count})
        
    def suggestNewsSources(self, prefix, page = 0, count = 20):
        """return a list of news sources that match the prefix"""
        return self.jsonRequest("/json/suggestSources", { "prefix": prefix, "page": page, "count": count })
        
    def suggestLocations(self, prefix, count = 20, lang = "eng", source = ["place", "country"], countryUri = None):
        """return a list of geo locations (cities or countries) that contain the prefix"""
        return self.jsonRequest("/json/suggestLocations", { "prefix": prefix, "count": count, "source": source, "lang": lang, "countryUri": countryUri or "" })
        
    def suggestCategories(self, prefix, page = 0, count = 20):
        """return a list of dmoz categories that contain the prefix"""
        return self.jsonRequest("/json/suggestCategories", { "prefix": prefix, "page": page, "count": count })

    def suggestConceptClasses(self, prefix, lang = "eng", conceptLang = "eng", page = 0, count = 20):
        """return a list of dmoz categories that contain the prefix"""
        return self.jsonRequest("/json/suggestConceptClasses", { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count })
        
    def getConceptUri(self, conceptLabel, lang = "eng", sources = ["concepts"]):
        """return a concept uri that is the best match for the given concept label"""
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and matches[0].has_key("uri"):
            return matches[0]["uri"]
        return None

    def getLocationUri(self, locationLabel, lang = "eng", source = ["place", "country"], countryUri = None):
        """return a location uri that is the best match for the given location label"""
        matches = self.suggestLocations(locationLabel, lang = lang, source = source, countryUri = countryUri)
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

    def getRecentStats(self):
        """get some stats about recently imported articles and events"""
        return self.jsonRequest("/json/overview", { "action": "getRecentStats"})
