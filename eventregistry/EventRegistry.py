"""
main class responsible for obtaining results from the Event Registry
"""
import six, os, sys, traceback, json, re, requests, time, logging, threading

from typing import Union, List, Tuple
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.Logger import logger


class EventRegistry(object):
    """
    the core object that is used to access any data in Event Registry
    it is used to send all the requests and queries
    """
    def __init__(self,
                 apiKey: Union[str, None] = None,
                 host: Union[str, None] = None,
                 hostAnalytics: Union[str, None] = None,
                 minDelayBetweenRequests: float = 0.5,
                 repeatFailedRequestCount: int = -1,
                 allowUseOfArchive: bool = True,
                 verboseOutput: bool = False,
                 settingsFName: Union[str, None] = None):
        """
        @param apiKey: API key that should be used to make the requests to the Event Registry. API key is assigned to each user account and can be obtained on
            this page: https://newsapi.ai/dashboard
        @param host: host to use to access the Event Registry backend. Use None to use the default host.
        @param hostAnalytics: the host address to use to perform the analytics api calls
        @param minDelayBetweenRequests: the minimum number of seconds between individual api calls
        @param repeatFailedRequestCount: if a request fails (for example, because ER is down), what is the max number of times the request
            should be repeated (-1 for indefinitely)
        @param allowUseOfArchive: default is True. Determines if the queries made should potentially be executed on the archive data.
            If False, all queries (regardless how the date conditions are set) will be executed on data from the last 31 days.
            Queries executed on the archive are more expensive so set it to False if you are just interested in recent data
        @param verboseOutput: if True, additional info about errors etc will be printed to console
        @param settingsFName: If provided it should be a full path to 'settings.json' file where apiKey an/or host can be loaded from.
            If None, we will look for the settings file in the eventregistry module folder
        """
        self._host = host or "http://eventregistry.org"
        self._hostAnalytics = hostAnalytics or "http://analytics.eventregistry.org"
        self._lastException = None
        self._logRequests = False
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
        currPath = os.path.split(os.path.realpath(__file__))[0]
        settFName = settingsFName or os.path.join(currPath, "settings.json")
        if apiKey:
            logger.debug("using user provided API key for making requests")

        if os.path.exists(settFName):
            settings = json.load(open(settFName))
            self._host = host or settings.get("host", "http://eventregistry.org")
            self._hostAnalytics = hostAnalytics or settings.get("hostAnalytics", "http://analytics.eventregistry.org")
            # if api key is set, then use it when making the requests
            if "apiKey" in settings and not apiKey:
                logger.debug("found apiKey in settings file which will be used for making requests")
                self._apiKey = settings["apiKey"]

        if self._apiKey == None:
            print("No API key was provided. You will be allowed to perform only a very limited number of requests per day.")
        self._requestLogFName = os.path.join(currPath, "requests_log.txt")

        logger.debug("Event Registry host: %s", self._host)
        logger.debug("Text analytics host: %s", self._hostAnalytics)

        # list of status codes - when we get them as a response from the call, we don't want to repeat the query as the response will likely always be the same
        self._stopStatusCodes = set([
            204,        # Information not available. Request succeeded, but the requested information is not available.
            400,        # Bad request. The request was unacceptable, most likely due to invalid or missing parameter.
            401,        # User's limit reached. The user reached the limit of the tokens in his account. The requests are rejected.
            403,        # Invalid account. The user's IP or account is disabled, potentially due to misuse.
        ])


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
                    logger.info("==============\nYour version of the module is outdated, please update to the latest version")
                    logger.info("Your version is %s while the latest is %s", currentVersion, latestVersion)
                    logger.info("Update by calling: pip install --upgrade eventregistry\n==============")
                    return
                # in case the server mistakenly has a lower version that the user has, don't report an error
                elif int(latest) < int(current):
                    return
        except:
            pass


    def setLogging(self, val: bool):
        """should all requests be logged to a file or not?"""
        self._logRequests = val


    def setExtraParams(self, params: dict):
        if params is not None:
            assert(isinstance(params, dict))
        self._extraParams = params


    def getHost(self):
        return self._host


    def getLastException(self):
        """return the last exception"""
        return self._lastException


    def printLastException(self):
        logger.error(str(self._lastException))


    def format(self, obj):
        """return a string containing the object in a pretty formated version"""
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


    def getRemainingAvailableRequests(self):
        """get the number of requests that are still available for the user today. Information is only accessible after you make some query."""
        return self._remainingAvailableRequests


    def getDailyAvailableRequests(self):
        """get the total number of requests that the user can make in a day. Information is only accessible after you make some query."""
        return self._dailyAvailableRequests


    def getUsageInfo(self):
        """return the number of used and total available tokens. Can be used at any time (also before making queries)"""
        return self.jsonRequest("/api/v1/usage", { "apiKey": self._apiKey })


    def getServiceStatus(self):
        """return the status of various services used in Event Registry pipeline"""
        return self.jsonRequest("/api/v1/getServiceStatus", {"apiKey": self._apiKey})


    def getUrl(self, query: QueryParamsBase):
        """
        return the url that can be used to get the content that matches the query
        @param query: instance of Query class
        """
        assert isinstance(query, QueryParamsBase), "query parameter should be an instance of a class that has Query as a base class, such as QueryArticles or QueryEvents"
        import urllib
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the url
        url = self._host + query._getPath() + "?" + urllib.parse.urlencode(allParams, doseq=True)
        return url


    def getLastHeaders(self):
        """
        return the headers returned in the response object of the last executed request
        """
        return self._headers


    def getLastHeader(self, headerName: str, default = None):
        """
        get a value of the header headerName that was set in the headers in the last response object
        """
        return self._headers.get(headerName, default)


    def printLastReqStats(self):
        """
        print some statistics about the last executed request
        """
        print("Tokens used by the request: " + str(self.getLastHeader("req-tokens")))
        print("Performed action: " + str(self.getLastHeader("req-action")))
        print("Was archive used for the query: " + (self.getLastHeader("req-archive") == "1" and "Yes" or "No"))


    def getLastReqArchiveUse(self):
        """
        return True or False depending on whether the last request used the archive or not
        """
        return self.getLastHeader("req-archive", "0") == "1"


    def execQuery(self, query:QueryParamsBase, allowUseOfArchive: Union[bool, None] = None):
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


    def jsonRequest(self, methodUrl: str, paramDict: dict, customLogFName: Union[str, None] = None, allowUseOfArchive: Union[bool, None] = None):
        """
        make a request for json data. repeat it _repeatFailedRequestCount times, if they fail (indefinitely if _repeatFailedRequestCount = -1)
        @param methodUrl: url on er (e.g. "/api/v1/article")
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
                with open(customLogFName or self._requestLogFName, "a", encoding="utf-8") as log:
                    if isinstance(paramDict, dict):
                        log.write("# " + json.dumps(paramDict) + "\n")
                    log.write(methodUrl + "\n\n")
            except Exception as ex:
                self._lastException = ex

        if paramDict is None:
            paramDict = {}
        # if we have api key then add it to the paramDict
        if self._apiKey:
            paramDict["apiKey"] = self._apiKey
        # if we want to ignore the archive, set the flag
        if isinstance(allowUseOfArchive, bool):
            if not allowUseOfArchive:
                paramDict["forceMaxDataTimeWindow"] = 31
        # if we didn't override the parameter then check what we've set when constructing the EventRegistry class
        elif self._allowUseOfArchive is False:
            paramDict["forceMaxDataTimeWindow"] = 31
        # if we also have some extra parameters, then set those too
        if self._extraParams:
            paramDict.update(self._extraParams)

        tryCount = 0
        self._headers = {}  # reset any past data
        returnData = None
        respInfo = None
        url = self._host + methodUrl
        while self._repeatFailedRequestCount < 0 or tryCount <= self._repeatFailedRequestCount:
            tryCount += 1
            try:
                # make the request
                respInfo = self._reqSession.post(url, json = paramDict, timeout=60)
                # remember the returned headers
                self._headers = respInfo.headers
                # if we got some error codes print the error and repeat the request after a short time period
                if respInfo.status_code != 200:
                    raise Exception(respInfo.text)
                # did we get a warning. if yes, print it
                if self.getLastHeader("warning"):
                    logger.warning("=========== WARNING ===========\n%s\n===============================", self.getLastHeader("warning"))
                # remember the available requests
                self._dailyAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-limit", ""), val = -1)
                self._remainingAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-remaining", ""), val = -1)

                returnData = respInfo.json()
                break
            except Exception as ex:
                self._lastException = ex
                if self._verboseOutput:
                    logger.error("Event Registry exception while executing the request:")
                    logger.error("endpoint: %s\nParams: %s", url, json.dumps(paramDict, indent=4))
                    self.printLastException()
                # in case of invalid input parameters, don't try to repeat the search but we simply raise the same exception again
                if respInfo is not None and respInfo.status_code in self._stopStatusCodes:
                    break
                # in case of the other exceptions (maybe the service is temporarily unavailable) we try to repeat the query
                logger.info("The request will be automatically repeated in 3 seconds...")
                time.sleep(5)   # sleep for X seconds on error
        self._lock.release()
        if returnData is None:
            raise self._lastException or Exception("No valid return data provided")
        return returnData


    def jsonRequestAnalytics(self, methodUrl: str, paramDict: dict):
        """
        call the analytics service to execute a method like annotation, categorization, etc.
        @param methodUrl: api endpoint url to call
        @param paramDict: a dictionary with values to send to the api endpoint
        """
        if self._apiKey:
            paramDict["apiKey"] = self._apiKey
        self._lock.acquire()
        returnData = None
        respInfo = None
        self._lastException = None
        self._headers = {}  # reset any past data
        tryCount = 0
        while self._repeatFailedRequestCount < 0 or tryCount <= self._repeatFailedRequestCount:
            tryCount += 1
            try:
                url = self._hostAnalytics + methodUrl
                # make the request
                respInfo = self._reqSession.post(url, json = paramDict, timeout=60)
                # remember the returned headers
                self._headers = respInfo.headers
                # if we got some error codes print the error and repeat the request after a short time period
                if respInfo.status_code != 200:
                    raise Exception(respInfo.text)
                returnData = respInfo.json()
                break
            except Exception as ex:
                self._lastException = ex
                if self._verboseOutput:
                    logger.error("Event Registry Analytics exception while executing the request:")
                    logger.error("endpoint: %s\nParams: %s", url, json.dumps(paramDict, indent=4))
                    self.printLastException()
                # in case of invalid input parameters, don't try to repeat the search but we simply raise the same exception again
                if respInfo is not None and respInfo.status_code in self._stopStatusCodes:
                    break
                logger.info("The request will be automatically repeated in 3 seconds...")
                time.sleep(5)   # sleep for X seconds on error
        self._lock.release()
        if returnData is None:
            raise self._lastException or Exception("No valid return data provided")
        return returnData

    #
    # suggestion methods - return type is a list of matching items

    def suggestConcepts(self, prefix: str, sources: Union[str, list] = ["concepts"], lang: str = "eng", conceptLang: str = "eng", page: int = 1, count: int = 20, returnInfo: ReturnInfo = ReturnInfo(), **kwargs):
        """
        return a list of concepts that contain the given prefix. returned matching concepts are sorted based on their
            frequency of occurence in news (from most to least frequent)
        @param prefix: input text that should be contained in the concept
        @param sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki)
        @param lang: language in which the prefix is specified
        @param conceptLang: languages in which the label(s) for the concepts are to be returned
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions per page
        @param returnInfo: what details about concepts should be included in the returned information
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "source": sources, "lang": lang, "conceptLang": conceptLang, "page": page, "count": count}
        params.update(returnInfo.getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestConceptsFast", params)


    def suggestCategories(self, prefix: str, page: int = 1, count: int = 20, returnInfo: ReturnInfo = ReturnInfo(), **kwargs):
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
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestCategoriesFast", params)


    def suggestNewsSources(self, prefix: str, dataType: Union[str, list] = ["news", "pr", "blog"], page: int = 1, count: int = 20, **kwargs):
        """
        return a list of news sources that match the prefix
        @param prefix: input text that should be contained in the source name or uri
        @param dataType: suggest sources that provide content in these data types ("news", "pr", "blog" or a list of any of those)
        @param page: page of results
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = {"prefix": prefix, "dataType": dataType, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestSourceGroups(self, prefix: str, page: int = 1, count: int = 20, **kwargs):
        """
        return a list of news source groups that match the prefix
        @param prefix: input text that should be contained in the source group name or uri
        @param page:  page of the results (1, 2, ...)
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = { "prefix": prefix, "page": page, "count": count }
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourceGroups", params)


    def suggestLocations(self, prefix: str, sources: Union[str, list] = ["place", "country"], lang: str = "eng", count: int = 20, countryUri: Union[str, None] = None, sortByDistanceTo: Union[List, Tuple, None] = None, returnInfo: ReturnInfo = ReturnInfo(), **kwargs):
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
        params.update(kwargs)
        if sortByDistanceTo:
            assert isinstance(sortByDistanceTo, (tuple, list)), "sortByDistanceTo has to contain a tuple with latitude and longitude of the location"
            assert len(sortByDistanceTo) == 2, "The sortByDistanceTo should contain two float numbers"
            params["closeToLat"] = sortByDistanceTo[0]
            params["closeToLon"] = sortByDistanceTo[1]
        return self.jsonRequest("/api/v1/suggestLocationsFast", params)


    def suggestLocationsAtCoordinate(self, latitude: Union[int, float], longitude: Union[int, float], radiusKm: Union[int, float], limitToCities: bool = False, lang: str = "eng", count: int = 20, returnInfo: ReturnInfo = ReturnInfo(), **kwargs):
        """
        return a list of geo locations (cities or places) that are close to the provided (lat, long) values
        @param latitude: latitude part of the coordinate
        @param longitude: longitude part of the coordinate
        @param radiusKm: radius in kilometres around the coordinates inside which the locations should be returned
        @param limitToCities: limit the set of results only to cities (True) or also to general places (False)
        @param lang: language in which the location label should be returned
        @param count: number of returned suggestions
        @param returnInfo: what details about locations should be included in the returned information
        """
        assert isinstance(latitude, (int, float)), "The 'latitude' should be a number"
        assert isinstance(longitude, (int, float)), "The 'longitude' should be a number"
        params = { "action": "getLocationsAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "limitToCities": limitToCities, "count": count, "lang": lang }
        params.update(returnInfo.getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestLocationsFast", params)


    def suggestSourcesAtCoordinate(self, latitude: Union[int, float], longitude: Union[int, float], radiusKm: Union[int, float], count: int = 20, **kwargs):
        """
        return a list of news sources that are close to the provided (lat, long) values
        @param latitude: latitude part of the coordinate
        @param longitude: longitude part of the coordinate
        @param radiusKm: radius in kilometres around the coordinates inside which the news sources should be located
        @param count: number of returned suggestions
        """
        assert isinstance(latitude, (int, float)), "The 'latitude' should be a number"
        assert isinstance(longitude, (int, float)), "The 'longitude' should be a number"
        params = {"action": "getSourcesAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestSourcesAtPlace(self, conceptUri: str, dataType: Union[str, List[str]] = "news", page = 1, count = 20, **kwargs):
        """
        return a list of news sources that are close to the provided (lat, long) values
        @param conceptUri: concept that represents a geographic location for which we would like to obtain a list of sources located at the place
        @param dataType: type of the news source ("news", "pr", "blog" or a list of any of those)
        @param page: page of the results (1, 2, ...)
        @param count: number of returned sources
        """
        params = {"action": "getSourcesAtPlace", "conceptUri": conceptUri, "page": page, "count": count, "dataType": dataType}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestAuthors(self, prefix: str, page: int = 1, count: int = 20, **kwargs):
        """
        return a list of news sources that match the prefix
        @param prefix: input text that should be contained in the author name and source url
        @param page: page of results
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestAuthorsFast", params)


    def suggestEventTypes(self, prefix: str, page: int = 1, count: int = 20, **kwargs):
        """
        return a list of event types that match the prefix
        @param prefix: input text that should be contained in the industry name
        @param page: page of results
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/eventType/suggestEventTypes", params)


    def suggestIndustries(self, prefix: str, page: int = 1, count: int = 20, **kwargs):
        """
        return a list of industries that match the prefix. Note: Industries can only be used when querying mentions (QueryMentions, QueryMentionsIter)
        @param prefix: input text that should be contained in the industry name
        @param page: page of results
        @param count: number of returned suggestions
        """
        assert page > 0, "page parameter should be above 0"
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/eventType/suggestIndustries", params)


    def getSdgUris(self):
        """
        return a list of SDG uris. Note: Industries can only be used when querying mentions (QueryMentions, QueryMentionsIter)
        """
        return self.jsonRequest("/api/v1/eventType/sdg/getItems", {})


    def getSasbUris(self):
        """
        return a list of SASB uris. Note: SASB uris can only be used when querying mentions (QueryMentions, QueryMentionsIter)
        """
        return self.jsonRequest("/api/v1/eventType/sasb/getItems", {})


    def suggestConceptClasses(self, prefix: str, lang: str = "eng", conceptLang: str = "eng", source: Union[str, List[str]] = ["dbpedia", "custom"], page: int = 1, count: int = 20, returnInfo: ReturnInfo = ReturnInfo(), **kwargs):
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
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestConceptClasses", params)


    #
    # get info methods - return type is a single item that is the best match to the given input

    def getConceptUri(self, conceptLabel: str, lang: str = "eng", sources: Union[str, List[str]] = ["concepts"]):
        """
        return a concept uri that is the best match for the given concept label
        if there are multiple matches for the given conceptLabel, they are sorted based on their frequency of occurence in news (most to least frequent)
        @param conceptLabel: partial or full name of the concept for which to return the concept uri
        @param sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki)
        """
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getLocationUri(self, locationLabel: str, lang: str = "eng", sources: Union[str, List[str]] = ["place", "country"], countryUri: Union[str, None] = None, sortByDistanceTo: Union[List, Tuple, None] = None):
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


    def getCategoryUri(self, categoryLabel: str):
        """
        return a category uri that is the best match for the given label
        @param categoryLabel: partial or full name of the category for which to return category uri
        """
        matches = self.suggestCategories(categoryLabel)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getNewsSourceUri(self, sourceName: str, dataType: Union[str, List[str]] = ["news", "pr", "blog"]):
        """
        return the news source that best matches the source name
        @param sourceName: partial or full name of the source or source uri for which to return source uri
        @param dataType: return the source uri that provides content of these data types ("news", "pr", "blog" or a list of any of those)
        """
        matches = self.suggestNewsSources(sourceName, dataType = dataType)
        if matches != None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getSourceUri(self, sourceName: str, dataType: Union[str, List[str]] = ["news", "pr", "blog"]):
        """
        alternative (shorter) name for the method getNewsSourceUri()
        """
        return self.getNewsSourceUri(sourceName, dataType)


    def getSourceGroupUri(self, sourceGroupName: str):
        """
        return the URI of the source group that best matches the name
        @param sourceGroupName: partial or full name of the source group
        """
        matches = self.suggestSourceGroups(sourceGroupName)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptClassUri(self, classLabel: str, lang: str = "eng"):
        """
        return a uri of the concept class that is the best match for the given label
        @param classLabel: partial or full name of the concept class for which to return class uri
        """
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptInfo(self, conceptUri: str,
                       returnInfo: ReturnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(synonyms = True, image = True, description = True))):
        """
        return detailed information about a particular concept
        @param conceptUri: uri of the concept
        @param returnInfo: what details about the concept should be included in the returned information
        """
        params = returnInfo.getParams()
        params.update({"uri": conceptUri })
        return self.jsonRequest("/api/v1/concept/getInfo", params)


    def getAuthorUri(self, authorName: str):
        """
        return author uri that is the best match for the given author name (and potentially source url)
        if there are multiple matches for the given author name, they are sorted based on the number of articles they have written (from most to least frequent)
        @param authorName: partial or full name of the author, potentially also containing the source url (e.g. "george brown nytimes")
        """
        matches = self.suggestAuthors(authorName)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getEventTypeUri(self, eventTypeLabel: str):
        """
        return event type uri that is the best match for the given label
        @param eventTypeLabel: partial or full name of the event type for which we want to retrieve uri
        """
        matches = self.suggestEventTypes(eventTypeLabel)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    @staticmethod
    def getUriFromUriWgt(uriWgtList: List[str]):
        """
        convert an array of items that contain uri:wgt to a list of items with uri only. Used for QueryArticle and QueryEvent classes
        """
        assert isinstance(uriWgtList, list), "uriWgtList has to be a list of strings that represent article uris"
        uriList = [uriWgt.split(":")[0] for uriWgt in uriWgtList]
        return uriList


    #
    # additional utility methods

    def getArticleUris(self, articleUrls: Union[str, List[str]]):
        """
        if you have article urls and you want to query them in ER you first have to obtain their uris in the ER.
        @param articleUrls a single article url or a list of article urls
        @returns returns dict where key is article url and value is either None if no match found or a string with article URI.
        """
        assert isinstance(articleUrls, (six.string_types, list)), "Expected a single article url or a list of urls"
        return self.jsonRequest("/api/v1/articleMapper", { "articleUrl": articleUrls })


    def getSourceGroups(self):
        """return the list of URIs of all known source groups"""
        ret = self.jsonRequest("/api/v1/sourceGroup/getSourceGroups", {})
        return ret


    def getSourceGroup(self, sourceGroupUri: str):
        """return info about the source group"""
        ret = self.jsonRequest("/api/v1/sourceGroup/getSourceGroupInfo", { "uri": sourceGroupUri })
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
    def __init__(self, er: EventRegistry, rememberMappings: bool = True):
        """
        create instance of article mapper
        it will map from article urls to article uris
        the mappings can be remembered so it will not repeat requests for the same article urls
        """
        self._er = er
        self._articleUrlToUri = {}
        self._rememberMappings = rememberMappings


    def getArticleUri(self, articleUrl: str):
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