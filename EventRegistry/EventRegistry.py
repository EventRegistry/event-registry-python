"""
classes responsible for obtaining results from the Event Registry
"""
import six, os, sys, traceback, json, re, requests, time
import threading
from eventregistry.Base import *
from eventregistry.EventForText import *
from eventregistry.ReturnInfo import *
from eventregistry.QueryEvents import *
from eventregistry.QueryEvent import *
from eventregistry.QueryArticles import *
from eventregistry.QueryArticle import *
from eventregistry.QueryStory import *
from eventregistry.Correlations import *
from eventregistry.Counts import *
from eventregistry.DailyShares import *
from eventregistry.Info import *
from eventregistry.Recent import *
from eventregistry.Trends import *

class EventRegistry(object):
    """
    the core object that is used to access any data in Event Registry
    it is used to send all the requests and queries
    """
    def __init__(self, host = None, logging = False,
                 minDelayBetweenRequests = 0.5,     # the minimum number of seconds between individual api calls
                 repeatFailedRequestCount = -1,     # if a request fails (for example, because ER is down), what is the max number of times the request should be repeated (-1 for indefinitely)
                 verboseOutput = False,             # if true, additional info about query times etc will be printed to console
                 apiKey = None):
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
        self._apiKey = apiKey

        # if there is a settings.json file in the directory then try using it to login to ER
        # and to read the host name from it (if custom host is not specified)
        currPath = os.path.split(__file__)[0]
        settPath = os.path.join(currPath, "settings.json")
        if os.path.exists(settPath):
            settings = json.load(open(settPath))
            self._host = host or settings.get("host", "http://eventregistry.org")
            # try logging in with username and password
            if "username" in settings and "password" in settings:
                print("found username and password in settings file which will be used for making requests. Trying to login...")
                self.login(settings.get("username", ""), settings.get("password", ""), False)
            # if api key is set, then use it when making the requests
            elif "apiKey" in settings:
                print("found apiKey in settings file which will be used for making requests")
                self._apiKey = settings["apiKey"]
            else:
                print("no authentication found in the settings file")
        else:
            self._host = host or "http://eventregistry.org"
        self._requestLogFName = os.path.join(currPath, "requests_log.txt")

        print("Event Registry host: %s" % (self._host))

    def setLogging(self, val):
        """should all requests be logged to a file or not?"""
        self._logRequests = val

    def getHost(self):
        return self._host

    def getLastException(self):
        """return the last exception"""
        return self._lastException

    def printLastException(self):
        print(str(self._lastException))

    def format(self, obj):
        """return a string containing the object in a pretty formated version"""
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

    def printConsole(self, text):
        """print time prefix + text to console"""
        print(time.strftime("%H:%M:%S") + " " + str(text))

    def getRemainingAvailableRequests(self):
        """get the number of requests that are still available for the user today"""
        return self._remainingAvailableRequests

    def getDailyAvailableRequests(self):
        """get the total number of requests that the user can make in a day"""
        return self._dailyAvailableRequests;


    def login(self, username, password, throwExceptOnFailure = True):
        """
        login the user. without logging in, the user is limited to 50 queries per day.
        if you have a registered account, the number of allowed requests per day can be higher, depending on your subscription plan
        """
        respInfoObj = None
        try:
            respInfo = self._reqSession.post(self._host + "/login", data = { "email": username, "pass": password })
            self._cookies = respInfo.cookies
            respInfoText = respInfo.text
            respInfoObj = json.loads(respInfoText)
            if throwExceptOnFailure and "error" in respInfoObj:
                raise Exception(respInfo["error"])
            elif "info" in respInfoObj:
                print("Successfully logged in with user %s" % (username))
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

        # if we have api key then add it to the paramDict
        if self._apiKey:
            if paramDict == None:
                paramDict = {}
            paramDict["apiKey"] = self._apiKey

        tryCount = 0
        returnData = None
        while self._repeatFailedRequestCount < 0 or tryCount < self._repeatFailedRequestCount:
            tryCount += 1
            try:
                url = self._host + methodUrl;

                # make the request
                respInfo = self._reqSession.post(url, json = paramDict, cookies = self._cookies)
                # if we got some error codes print the error and repeat the request after a short time period
                if respInfo.status_code != 200:
                    raise Exception(respInfo.text)
                # did we get a warning. if yes, print it
                if respInfo.headers.get("warning", ""):
                    print("=========== WARNING ===========\n%s\n===============================" % (respInfo.headers.get("warning", "")))
                # remember the available requests
                self._dailyAvailableRequests = tryParseInt(respInfo.headers.get("x-ratelimit-limit", ""), val = -1)
                self._remainingAvailableRequests = tryParseInt(respInfo.headers.get("x-ratelimit-remaining", ""), val = -1)
                if self._verboseOutput:
                    timeSec = int(respInfo.headers.get("x-response-time", "-1")) / 1000.
                    self.printConsole("request took %.3f sec. Response size: %.2fKB" % (timeSec, len(respInfo.text) / 1024.0))
                try:
                    returnData = respInfo.json()
                    break
                except Exception as ex:
                    print("EventRegistry.jsonRequest(): Exception while parsing the returned json object. Repeating the query...")
                    open("invalidJsonResponse.json", "w").write(respInfo.text)
            except Exception as ex:
                self._lastException = ex
                print("Event Registry exception while executing the request:")
                self.printLastException()
                time.sleep(10)   # sleep for 10 seconds on error
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
        return self.jsonRequest("/json/suggestConceptsFast", params)


    def suggestNewsSources(self, prefix, page = 1, count = 20):
        """return a list of news sources that match the prefix"""
        assert page > 0, "page parameter should be above 0"
        return self.jsonRequest("/json/suggestSourcesFast", { "prefix": prefix, "page": page, "count": count })


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
        return self.jsonRequest("/json/suggestCategoriesFast", params)


    def suggestConceptClasses(self, prefix, lang = "eng", conceptLang = "eng", source = ["dbpedia", "custom"], page = 1, count = 20, returnInfo = ReturnInfo()):
        """return a list of dmoz categories that contain the prefix"""
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "source": source, "page": page, "count": count }
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
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getLocationUri(self, locationLabel, lang = "eng", source = ["place", "country"], countryUri = None, sortByDistanceTo = None):
        """return a location uri that is the best match for the given location label"""
        matches = self.suggestLocations(locationLabel, lang = lang, source = source, countryUri = countryUri, sortByDistanceTo = sortByDistanceTo)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "wikiUri" in matches[0]:
            return matches[0]["wikiUri"]
        return None


    def getCategoryUri(self, categoryLabel):
        """return a category uri that is the best match for the given label"""
        matches = self.suggestCategories(categoryLabel)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getNewsSourceUri(self, sourceName):
        """return the news source that best matches the source name"""
        matches = self.suggestNewsSources(sourceName)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptClassUri(self, classLabel, lang = "eng"):
        """return a uri of the concept class that is the best match for the given label"""
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
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
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getRecentStats(self):
        """get some stats about recently imported articles and events"""
        return self.jsonRequest("/json/overview", { "action": "getRecentStats"})


    def getStats(self, addDailyArticles = False, addDailyAnnArticles = False, addDailyDuplArticles = False, addDailyEvents = False):
        """get total statistics about all imported articles, concepts, events as well as daily counts for these"""
        return self.jsonRequest("/json/overview", { "action": "getStats", "addDailyArticles": addDailyArticles, "addDailyAnnArticles": addDailyAnnArticles, "addDailyDuplArticles": addDailyDuplArticles, "addDailyEvents": addDailyEvents })


    def getArticleUris(self, articleUrls):
        """
        if you have article urls and you want to query them in ER you first have to
        obtain their uris in the ER.
        @param articleUrls a single article url or a list of article urls
        @returns dict where key is article url and value is None (if article not found) or article uri
        """
        assert isinstance(articleUrls, (six.string_types, list)), "Expected a single article url or a list of urls"
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
        if ret and len(list(ret.keys())) > 0:
            return ret[list(ret.keys())[0]].get("info")
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
        if articleUrl in self._articleUrlToUri:
            return self._articleUrlToUri[articleUrl]
        res = self._er.getArticleUris(articleUrl)
        if res and articleUrl in res:
            if self._rememberMappings:
                self._articleUrlToUri[articleUrl] = res[articleUrl]
            return res[articleUrl]
