"""
main class responsible for obtaining results from the Event Registry
"""
import six, os, sys, traceback, json, re, requests, time
import threading
from eventregistry.Base import *
from eventregistry.EventForText import *
from eventregistry.ReturnInfo import *
from eventregistry.Query import *
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
    def __init__(self,
                 apiKey = None,
                 host = None,
                 logging = False,
                 minDelayBetweenRequests = 0.5,
                 repeatFailedRequestCount = -1,
                 allowUseOfArchive = True,
                 verboseOutput = False,
                 settingsFName = None):
        """
        @param apiKey: API key that should be used to make the requests to the Event Registry. API key is assigned to each user account and can be obtained on this page: http://eventregistry.org/me?tab=settings
        @param host: host to use to access the Event Registry backend. Use None to use the default host.
        @param logging: log all requests made to a 'requests_log.txt' file
        @param minDelayBetweenRequests: the minimum number of seconds between individual api calls
        @param repeatFailedRequestCount: if a request fails (for example, because ER is down), what is the max number of times the request should be repeated (-1 for indefinitely)
        @param allowUseOfArchive: default is True. Determines if the queries made should potentially be executed on the archive data. If False, all queries (regardless how the date conditions are set) will be
                executed on data from the last 31 days. Queries executed on the archive are more expensive so set it to False if you are just interested in recent data
        @param verboseOutput: if True, additional info about query times etc will be printed to console
        @param settingsFName: If provided it should be a full path to 'settings.json' file where apiKey an/or host can be loaded from. If None, we will look for the settings file in the eventregistry module folder
        """
        self._host = host
        self._lastException = None
        self._logRequests = logging
        self._minDelayBetweenRequests = minDelayBetweenRequests
        self._repeatFailedRequestCount = repeatFailedRequestCount
        self._allowUseOfArchive = allowUseOfArchive
        self._verboseOutput = verboseOutput
        self._lastQueryTime = time.time()
        self._headers = {}
        self._dailyAvailableRequests = -1
        self._remainingAvailableRequests = -1

        # lock for making sure we make one request at a time - requests module otherwise sometimes returns incomplete json objects
        self._lock = threading.Lock()
        self._reqSession = requests.Session()
        self._apiKey = apiKey
        self._extraParams = None

        # if there is a settings.json file in the directory then try using it to load the API key from it
        # and to read the host name from it (if custom host is not specified)
        currPath = os.path.split(__file__)[0]
        settFName = settingsFName or os.path.join(currPath, "settings.json")
        if apiKey:
            print("using user provided API key for making requests")

        if os.path.exists(settFName):
            settings = json.load(open(settFName))
            self._host = host or settings.get("host", "http://eventregistry.org")
            # if api key is set, then use it when making the requests
            if "apiKey" in settings and not apiKey:
                print("found apiKey in settings file which will be used for making requests")
                self._apiKey = settings["apiKey"]
        else:
            self._host = host or "http://eventregistry.org"

        if self._apiKey == None:
            print("No API key was provided. You will be allowed to perform only a very limited number of requests per day.")
        self._requestLogFName = os.path.join(currPath, "requests_log.txt")

        print("Event Registry host: %s" % (self._host))
        # check what is the version of your module compared to the latest one
        self.checkVersion()


    def checkVersion(self):
        """
        check what is the latest version of the python sdk and report in case there is a newer version
        """
        try:
            respInfo = self._reqSession.get(self._host + "/static/pythonSDKVersion.txt")
            if respInfo.status_code != 200 or len(respInfo.text) > 20:
                return
            latestVersion = respInfo.text.strip()
            import eventregistry._version as _version
            currentVersion = _version.__version__
            for (latest, current) in zip(latestVersion.split("."), currentVersion.split(".")):
                if int(latest) > int(current):
                    print("==============\nYour version of the module is outdated, please update to the latest version")
                    print("Your version is %s while the latest is %s" % (currentVersion, latestVersion))
                    print("Update by calling: pip install --upgrade eventregistry\n==============")
                    return
                # in case the server mistakenly has a lower version that the user has, don't report an error
                elif int(latest) < int(current):
                    return
        except:
            pass


    def setLogging(self, val):
        """should all requests be logged to a file or not?"""
        self._logRequests = val


    def setExtraParams(self, params):
        if params != None:
            assert(isinstance(params, dict))
        self._extraParams = params


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
        return self._dailyAvailableRequests


    def getUrl(self, query):
        """
        return the url that can be used to get the content that matches the query
        @param query: instance of Query class
        """
        assert isinstance(query, QueryParamsBase), "query parameter should be an instance of a class that has Query as a base class, such as QueryArticles or QueryEvents"
        import urllib
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the url
        url = self._host + query._getPath() + "?" + urllib.urlencode(allParams, doseq=True)
        return url


    def getLastHeaders(self):
        """
        return the headers returned in the response object of the last executed request
        """
        return self._headers


    def getLastHeader(self, headerName, default = None):
        """
        get a value of the header headerName that was set in the headers in the last response object
        """
        return self._headers.get(headerName, default)


    def printLastReqStats(self):
        """
        print some statistics about the last executed request
        """
        print("Tokens used by the request: " + self.getLastHeader("req-tokens"))
        print("Performed action: " + self.getLastHeader("req-action"))
        print("Was archive used for the query: " + (self.getLastHeader("req-archive") == "1" and "Yes" or "No"))


    def getLastReqArchiveUse(self):
        """
        return True or False depending on whether the last request used the archive or not
        """
        return self.getLastHeader("req-archive", "0") == "1"


    def execQuery(self, query, allowUseOfArchive = None):
        """
        main method for executing the search queries.
        @param query: instance of Query class
        @param allowUseOfArchive: potentially override the value set when constructing EventRegistry class.
            If not None set it to boolean to determine if the request can be executed on the archive data or not
            If left to None then the value set in the EventRegistry constructor will be used
        """
        assert isinstance(query, QueryParamsBase), "query parameter should be an instance of a class that has Query as a base class, such as QueryArticles or QueryEvents"
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the request
        respInfo = self.jsonRequest(query._getPath(), allParams, allowUseOfArchive = allowUseOfArchive)
        return respInfo


    def jsonRequest(self, methodUrl, paramDict, customLogFName = None, allowUseOfArchive = None):
        """
        make a request for json data. repeat it _repeatFailedRequestCount times, if they fail (indefinitely if _repeatFailedRequestCount = -1)
        @param methodUrl: url on er (e.g. "/json/article")
        @param paramDict: optional object containing the parameters to include in the request (e.g. { "articleUri": "123412342" }).
        @param customLogFName: potentially a file name where the request information can be logged into
        @param allowUseOfArchive: potentially override the value set when constructing EventRegistry class.
            If not None set it to boolean to determine if the request can be executed on the archive data or not
            If left to None then the value set in the EventRegistry constructor will be used
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

        if paramDict == None:
            paramDict = {}
        # if we have api key then add it to the paramDict
        if self._apiKey:
            paramDict["apiKey"] = self._apiKey
        # if we want to ignore the archive, set the flag
        if allowUseOfArchive != None:
            if not allowUseOfArchive:
                paramDict["forceMaxDataTimeWindow"] = 31
        # if we didn't override the parameter then check what we've set when constructing the EventRegistry class
        elif self._allowUseOfArchive == False:
            paramDict["forceMaxDataTimeWindow"] = 31
        # if we also have some extra parameters, then set those too
        if self._extraParams:
            paramDict.update(self._extraParams)

        tryCount = 0
        self._headers = {}  # reset any past data
        returnData = None
        while self._repeatFailedRequestCount < 0 or tryCount < self._repeatFailedRequestCount:
            tryCount += 1
            try:
                url = self._host + methodUrl

                # make the request
                respInfo = self._reqSession.post(url, json = paramDict)
                # remember the returned headers
                self._headers = respInfo.headers
                # if we got some error codes print the error and repeat the request after a short time period
                if respInfo.status_code != 200:
                    raise Exception(respInfo.text)
                # did we get a warning. if yes, print it
                if self.getLastHeader("warning"):
                    print("=========== WARNING ===========\n%s\n===============================" % (self.getLastHeader("warning")))
                # remember the available requests
                self._dailyAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-limit", ""), val = -1)
                self._remainingAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-remaining", ""), val = -1)
                if self._verboseOutput:
                    timeSec = int(self.getLastHeader("x-response-time", "0")) / 1000.
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
                #time.sleep(3)   # sleep for X seconds on error
        self._lock.release()
        if returnData == None:
            raise self._lastException
        return returnData

    #
    # suggestion methods - return type is a list of matching items

    def suggestConcepts(self, prefix, sources = ["concepts"], lang = "eng", conceptLang = "eng", page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of concepts that contain the given prefix. returned matching concepts are sorted based on their frequency of occurence in news (from most to least frequent)
        @param prefix: input text that should be contained in the concept
        @param sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki), conceptClass, conceptFolder
        @param lang: language in which the prefix is specified
        @param conceptLang: languages in which the label(s) for the concepts are to be returned
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions per page
        @param returnInfo: what details about concepts should be included in the returned information
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "source": sources, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count}
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestConcepts", params)


    def suggestCategories(self, prefix, page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of dmoz categories that contain the prefix
        @param prefix: input text that should be contained in the category name
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        @param returnInfo: what details about categories should be included in the returned information
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestCategories", params)


    def suggestNewsSources(self, prefix, page = 1, count = 20):
        """
        return a list of news sources that match the prefix
        @param prefix: input text that should be contained in the source name or uri
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "page": page, "count": count }
        return self.jsonRequest("/json/suggestSources", params)


    def suggestSourceGroups(self, prefix, page = 1, count = 20):
        """
        return a list of news source groups that match the prefix
        @param prefix: input text that should be contained in the source group name or uri
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        return self.jsonRequest("/json/suggestSourceGroups", { "prefix": prefix, "page": page, "count": count })


    def suggestLocations(self, prefix, sources = ["place", "country"], lang = "eng", count = 20, countryUri = None, sortByDistanceTo = None, returnInfo = ReturnInfo()):
        """
        return a list of geo locations (cities or countries) that contain the prefix
        @param prefix: input text that should be contained in the location name
        @param source: what types of locations are we interested in. Possible options are "place" and "country"
        @param lang: language in which the prefix is specified
        @param count: number of returned suggestions
        @param countryUri: if provided, then return only those locations that are inside the specified country
        @param sortByDistanceTo: if provided, then return the locations sorted by the distance to the (lat, long) provided in the tuple
        @param returnInfo: what details about locations should be included in the returned information
        """
        params = { "prefix": prefix, "count": count, "source": sources, "lang": lang, "countryUri": countryUri or "" }
        params.update(returnInfo.getParams())
        if sortByDistanceTo:
            assert isinstance(sortByDistanceTo, (tuple, list)), "sortByDistanceTo has to contain a tuple with latitude and longitude of the location"
            assert len(sortByDistanceTo) == 2, "The sortByDistanceTo should contain two float numbers"
            params["closeToLat"] = sortByDistanceTo[0]
            params["closeToLon"] = sortByDistanceTo[1]
        return self.jsonRequest("/json/suggestLocations", params)


    def suggestLocationsAtCoordinate(self, latitude, longitude, radiusKm, limitToCities = False, lang = "eng", count = 20, ignoreNonWiki = True, returnInfo = ReturnInfo()):
        """
        return a list of geo locations (cities or places) that are close to the provided (lat, long) values
        @param latitude: latitude part of the coordinate
        @param longitude: longitude part of the coordinate
        @param radiusKm: radius in kilometres around the coordinates inside which the locations should be returned
        @param limitToCities: limit the set of results only to cities (True) or also to general places (False)
        @param lang: language in which the location label should be returned
        @param count: number of returned suggestions
        @param ignoreNonWiki: ignore locations that don't have a wiki page and can not be used for concept search
        @param returnInfo: what details about locations should be included in the returned information
        """
        assert isinstance(latitude, (int, float)), "The 'latitude' should be a number"
        assert isinstance(longitude, (int, float)), "The 'longitude' should be a number"
        params = { "action": "getLocationsAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "limitToCities": limitToCities, "count": count, "lang": lang }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestLocations", params)


    def suggestSourcesAtCoordinate(self, latitude, longitude, radiusKm, count = 20):
        """
        return a list of news sources that are close to the provided (lat, long) values
        @param latitude: latitude part of the coordinate
        @param longitude: longitude part of the coordinate
        @param radiusKm: radius in kilometres around the coordinates inside which the news sources should be located
        @param count: number of returned suggestions
        """
        assert isinstance(latitude, (int, float)), "The 'latitude' should be a number"
        assert isinstance(longitude, (int, float)), "The 'longitude' should be a number"
        params = { "action": "getSourcesAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "count": count }
        return self.jsonRequest("/json/suggestSources", params)


    def suggestSourcesAtPlace(self, conceptUri, page = 1, count = 20):
        """
        return a list of news sources that are close to the provided (lat, long) values
        @param conceptUri: concept that represents a geographic location for which we would like to obtain a list of sources located at the place
        @param page: page of the results (1, 2, ...)
        @param count: number of returned sources
        """
        params = { "action": "getSourcesAtPlace", "conceptUri": conceptUri, "page": page, "count": count }
        return self.jsonRequest("/json/suggestSources", params)


    def suggestConceptClasses(self, prefix, lang = "eng", conceptLang = "eng", source = ["dbpedia", "custom"], page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of concept classes that match the given prefix
        @param prefix: input text that should be contained in the category name
        @param lang: language in which the prefix is specified
        @param conceptLang: languages in which the label(s) for the concepts are to be returned
        @param source: what types of concepts classes should be returned. valid values are 'dbpedia' or 'custom'
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        @param returnInfo: what details about categories should be included in the returned information
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "source": source, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestConceptClasses", params)


    def suggestCustomConcepts(self, prefix, lang = "eng", conceptLang = "eng", page = 1, count = 20, returnInfo = ReturnInfo()):
        """
        return a list of custom concepts that contain the given prefix. Custom concepts are the things (indicators, stock prices, ...) for which we import daily trending values that can be obtained using GetCounts class
        @param prefix: input text that should be contained in the concept name
        @param lang: language in which the prefix is specified
        @param conceptLang: languages in which the label(s) for the concepts are to be returned
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        @param returnInfo: what details about categories should be included in the returned information
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count }
        params.update(returnInfo.getParams())
        return self.jsonRequest("/json/suggestCustomConcepts", params)


    #
    # get info methods - return type is a single item that is the best match to the given input

    def getConceptUri(self, conceptLabel, lang = "eng", sources = ["concepts"]):
        """
        return a concept uri that is the best match for the given concept label
        if there are multiple matches for the given conceptLabel, they are sorted based on their frequency of occurence in news (most to least frequent)
        @param conceptLabel: partial or full name of the concept for which to return the concept uri
        @param sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki), conceptClass, conceptFolder
        """
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getLocationUri(self, locationLabel, lang = "eng", sources = ["place", "country"], countryUri = None, sortByDistanceTo = None):
        """
        return a location uri that is the best match for the given location label
        @param locationLabel: partial or full location name for which to return the location uri
        @param sources: what types of locations are we interested in. Possible options are "place" and "country"
        @param countryUri: if set, then filter the possible locatiosn to the locations from that country
        @param sortByDistanceTo: sort candidates by distance to the given (lat, long) pair
        """
        matches = self.suggestLocations(locationLabel, sources = sources, lang = lang, countryUri = countryUri, sortByDistanceTo = sortByDistanceTo)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "wikiUri" in matches[0]:
            return matches[0]["wikiUri"]
        return None


    def getCategoryUri(self, categoryLabel):
        """
        return a category uri that is the best match for the given label
        @param categoryLabel: partial or full name of the category for which to return category uri
        """
        matches = self.suggestCategories(categoryLabel)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getNewsSourceUri(self, sourceName):
        """
        return the news source that best matches the source name
        @param sourceName: partial or full name of the source or source uri for which to return source uri
        """
        matches = self.suggestNewsSources(sourceName)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getSourceGroupUri(self, sourceGroupName):
        """
        return the URI of the source group that best matches the name
        @param sourceGroupName: partial or full name of the source group
        """
        matches = self.suggestSourceGroups(sourceGroupName)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptClassUri(self, classLabel, lang = "eng"):
        """
        return a uri of the concept class that is the best match for the given label
        @param classLabel: partial or full name of the concept class for which to return class uri
        """
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptInfo(self, conceptUri,
                       returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(
                           synonyms = True, image = True, description = True))):
        """
        return detailed information about a particular concept
        @param conceptUri: uri of the concept
        @param returnInfo: what details about the concept should be included in the returned information
        """
        params = returnInfo.getParams()
        params.update({"uri": conceptUri, "action": "getInfo" })
        return self.jsonRequest("/json/concept", params)


    def getCustomConceptUri(self, label, lang = "eng"):
        """
        return a custom concept uri that is the best match for the given custom concept label
        note that for the custom concepts we don't have a sensible way of sorting the candidates that match the label
        if multiple candidates match the label we cannot guarantee which one will be returned
        @param label: label of the custom concept
        """
        matches = self.suggestCustomConcepts(label, lang = lang)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    #
    # additional utility methods

    def getRecentStats(self):
        """get some stats about recently imported articles and events"""
        return self.jsonRequest("/json/overview", { "action": "getRecentStats"})


    def getStats(self, addDailyArticles = False, addDailyAnnArticles = False, addDailyDuplArticles = False, addDailyEvents = False):
        """get total statistics about all imported articles, concepts, events as well as daily counts for these"""
        return self.jsonRequest("/json/overview", { "action": "getStats", "addDailyArticles": addDailyArticles, "addDailyAnnArticles": addDailyAnnArticles, "addDailyDuplArticles": addDailyDuplArticles, "addDailyEvents": addDailyEvents })


    def getArticleUris(self, articleUrls):
        """
        if you have article urls and you want to query them in ER you first have to obtain their uris in the ER.
        @param articleUrls a single article url or a list of article urls
        @returns returns dict where key is article url and value is either None if no match found or a string with article URI.
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
        q.setRequestedResult(RequestArticleInfo(returnInfo))
        ret = self.execQuery(q)
        if ret and len(list(ret.keys())) > 0:
            return ret[list(ret.keys())[0]].get("info")
        return None


    def getSourceGroups(self):
        """return the list of URIs of all known source groups"""
        ret = self.jsonRequest("/json/sourceGroup", { "action": "getSourceGroups" })
        return ret


    def getSourceGroup(self, sourceGroupUri):
        """return info about the source group"""
        ret = self.jsonRequest("/json/sourceGroup", { "action": "getSourceGroupInfo", "uri": sourceGroupUri })
        return ret


    #
    # internal methods

    def _sleepIfNecessary(self):
        """ensure that queries are not made too fast"""
        t = time.time()
        if t - self._lastQueryTime < self._minDelayBetweenRequests:
            time.sleep(self._minDelayBetweenRequests - (t - self._lastQueryTime))
        self._lastQueryTime = t



class ArticleMapper:
    def __init__(self, er, rememberMappings = True):
        """
        create instance of article mapper
        it will map from article urls to article uris
        the mappings can be remembered so it will not repeat requests for the same article urls
        """
        self._er = er
        self._articleUrlToUri = {}
        self._rememberMappings = rememberMappings


    def getArticleUri(self, articleUrl):
        """
        given the article url, return an array with 0, 1 or more article uris. Not all returned article uris are necessarily valid anymore. For news sources
        of lower importance we remove the duplicated articles and just keep the latest content
        @param articleUrl: string containing the article url
        @returns string: list of strings representing article uris.
        """
        if articleUrl in self._articleUrlToUri:
            return self._articleUrlToUri[articleUrl]
        res = self._er.getArticleUris(articleUrl)
        if res and articleUrl in res:
            val = res[articleUrl]
            if self._rememberMappings:
                self._articleUrlToUri[articleUrl] = val
            return val
        return None