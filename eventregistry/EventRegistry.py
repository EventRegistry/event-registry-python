"""
main class responsible for obtaining results from the Event Registry
"""
import json
import os
import re
import threading
import time
from typing import Any, Dict, List, Mapping, Tuple, Union, Optional
from urllib.parse import urlencode

import requests

from eventregistry.Base import QueryParamsBase, tryParseInt
from eventregistry.Exceptions import (EventRegistryError, InvalidResponseError, NetworkError, QueryError, RateLimitError,
                                      getErrorClassForStatusCode)
from eventregistry.ReturnInfo import ConceptInfoFlags, ReturnInfo
from eventregistry.Logger import logger

# the names exported by "from eventregistry import *"
__all__ = ["RETRY_BASE_DELAY", "MAX_RETRY_DELAY", "EventRegistry", "ArticleMapper"]

# the delay before repeating a failed request grows exponentially (2, 4, 8, ... seconds) up to MAX_RETRY_DELAY seconds
RETRY_BASE_DELAY = 2
MAX_RETRY_DELAY = 60


class EventRegistry:
    """
    the core object that is used to access any data in Event Registry
    it is used to send all the requests and queries
    """
    def __init__(self,
                 apiKey: Union[str, None] = None,
                 host: Union[str, None] = None,
                 hostAnalytics: Union[str, None] = None,
                 minDelayBetweenRequests: float = 0.5,
                 repeatFailedRequestCount: int = 3,
                 allowUseOfArchive: bool = True,
                 verboseOutput: bool = False,
                 settingsFName: Union[str, None] = None):
        """
        Args:
            apiKey: API key that should be used to make the requests to the Event Registry. API key is assigned to each user account and can be obtained on
                this page: https://newsapi.ai/dashboard
                If not provided, the key is read from the EVENTREGISTRY_API_KEY environment variable or else from the settings file (see settingsFName)
            host: host to use to access the Event Registry backend. Use None to use the default host.
            hostAnalytics: the host address to use to perform the analytics api calls
            minDelayBetweenRequests: the minimum number of seconds between individual api calls
            repeatFailedRequestCount: if a request fails with a temporary error (connection problem, timeout, server error (5xx)),
                the max number of times the request should be repeated (-1 for indefinitely).
                The delay between the attempts grows exponentially (2, 4, 8, ... seconds, at most 60) or follows the server's Retry-After header.
                A request rejected because of too many simultaneous requests (429) is always repeated, until it succeeds.
                Other errors (invalid request, token limit reached, ...) are never repeated. When the request fails, an EventRegistryError
                subclass is raised (see Exceptions.py)
            allowUseOfArchive: default is True. Determines if the queries made should potentially be executed on the archive data.
                If False, all queries (regardless how the date conditions are set) will be executed on data from the last 31 days.
                Queries executed on the archive are more expensive so set it to False if you are just interested in recent data
            verboseOutput: if True, additional info about errors etc will be printed to console
            settingsFName: If provided it should be a full path to 'settings.json' file where apiKey an/or host can be loaded from.
                If None, we look for the settings file in the .eventregistry folder of the user's home directory (~/.eventregistry/settings.json)
                and, if it is not there, in the eventregistry module folder
        """
        self._host = host or "https://eventregistry.org"
        self._hostAnalytics = hostAnalytics or "https://analytics.eventregistry.org"
        self._lastException: Optional[Exception] = None
        self._logRequests = False
        self._minDelayBetweenRequests = minDelayBetweenRequests
        self._repeatFailedRequestCount = repeatFailedRequestCount
        self._allowUseOfArchive = allowUseOfArchive
        self._verboseOutput = verboseOutput
        # set to 0 so that the very first request is not throttled
        self._lastQueryTime = 0.0
        self._headers: Mapping[str, str] = {}
        self._dailyAvailableRequests = -1
        self._remainingAvailableRequests = -1

        # lock for making sure we make one request at a time - requests module otherwise sometimes returns incomplete json objects
        self._lock = threading.Lock()
        self._warnedSortBy: set = set()
        self._reqSession = requests.Session()
        # the api key given as the parameter is used first, then the EVENTREGISTRY_API_KEY environment variable and
        # then the key in the settings file
        self._apiKey = apiKey or os.environ.get("EVENTREGISTRY_API_KEY") or None
        self._extraParams: Optional[dict] = None

        # if there is a settings.json file then try using it to load the API key from it
        # and to read the host name from it (if custom host is not specified).
        # we first look for the settings file in the ~/.eventregistry folder and if not there, in the module folder
        userConfDir = os.path.join(os.path.expanduser("~"), ".eventregistry")
        currPath = os.path.split(os.path.realpath(__file__))[0]
        settFName = settingsFName or os.path.join(userConfDir, "settings.json")
        if settingsFName is None and not os.path.exists(settFName):
            settFName = os.path.join(currPath, "settings.json")
        if apiKey:
            logger.debug("using user provided API key for making requests")

        if os.path.exists(settFName):
            with open(settFName, encoding="utf-8") as settFile:
                settings = json.load(settFile)
            self._host = host or settings.get("host", "https://eventregistry.org")
            self._hostAnalytics = hostAnalytics or settings.get("hostAnalytics", "https://analytics.eventregistry.org")
            # if api key is set, then use it when making the requests
            if "apiKey" in settings and not self._apiKey:
                logger.debug("found apiKey in settings file which will be used for making requests")
                self._apiKey = settings["apiKey"]

        if self._apiKey is None:
            print("No API key was provided. You will be allowed to perform only a very limited number of requests per day.")
        self._requestLogFName = os.path.join(userConfDir, "requests_log.txt")

        logger.debug("Event Registry host: %s", self._host)
        logger.debug("Text analytics host: %s", self._hostAnalytics)

        # HTTP status codes that the API can return and their meaning (see https://newsapi.ai/documentation?tab=introduction)
        self._httpStatusCodes = {
            200: "Success. Everything worked as expected.",
            204: "Information not available. Request succeeded, but the requested information is not available.",
            400: "Bad request. The request was unacceptable, most likely due to invalid or missing parameter.",
            401: "Unauthorized. The API key is not valid or the user reached the limit of the tokens in his account. The requests are rejected.",
            403: "Forbidden. The user's IP or account is disabled, or all the tokens have been used. Check the error message for more details.",
            429: "Too many requests. The user is making too many simultaneous requests. The requests are rejected.",
            500: "Internal error. Internal error occured while processing the request.",
            503: "Service unavailable. The service is currently not available.",
        }
        # the maximum number of requests that a user can be executing at the same time (exceeding it results in status code 429)
        self._maxSimultaneousRequests = 5


    def checkVersion(self):
        """
        check what is the latest version of the python sdk and report in case there is a newer version
        """
        try:
            respInfo = self._reqSession.get(self._host + "/static/pythonSDKVersion.txt", timeout=10)
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
        except Exception:
            pass


    def setLogging(self, val: bool):
        """should all requests be logged to a file or not?"""
        self._logRequests = val


    def setExtraParams(self, params: dict):
        if params is not None:
            if not (isinstance(params, dict)):
                raise TypeError("params should be of type dict")
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

        Args:
            query: instance of Query class
        """
        if not (isinstance(query, QueryParamsBase)):
            raise TypeError("query parameter should be an instance of a class that has Query as a base class, such as QueryArticles or QueryEvents")
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the url
        url = self._host + query._getPath() + "?" + urlencode(allParams, doseq=True)
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
        print("Was archive used for the query: " + ("Yes" if self.getLastHeader("req-archive") == "1" else "No"))


    def getLastReqArchiveUse(self):
        """
        return True or False depending on whether the last request used the archive or not
        """
        return self.getLastHeader("req-archive", "0") == "1"


    def execQuery(self, query: QueryParamsBase, allowUseOfArchive: Union[bool, None] = None, raiseOnError: bool = False) -> dict:
        """
        main method for executing the search queries.

        Args:
            query: instance of Query class
            allowUseOfArchive: potentially override the value set when constructing EventRegistry class.
                If not None set it to boolean to determine if the request can be executed on the archive data or not
                If left to None then the value set in the EventRegistry constructor will be used
            raiseOnError: the server can process the request, but return {"error": "..."} instead of the results (for example
                for an invalid uri). If True, a QueryError is raised in that case. By default the response with the error is returned
        """
        if not (isinstance(query, QueryParamsBase)):
            raise TypeError("query parameter should be an instance of a class that has Query as a base class, such as QueryArticles or QueryEvents")
        # don't modify original query params
        allParams = query._getQueryParams()
        # make the request
        respInfo = self.jsonRequest(query._getPath(), allParams, allowUseOfArchive = allowUseOfArchive)
        if raiseOnError and isinstance(respInfo, dict) and "error" in respInfo:
            raise QueryError(str(respInfo["error"]), statusCode = 200, responseText = str(respInfo["error"]), url = self._host + query._getPath())
        return respInfo


    def jsonRequest(self,
                    methodUrl: str,
                    paramDict: dict,
                    customLogFName: Union[str, None] = None,
                    allowUseOfArchive: Union[bool, None] = None) -> Any:
        """
        make a request for json data. repeat it _repeatFailedRequestCount times, if they fail (indefinitely if _repeatFailedRequestCount = -1).
        A request rejected because of too many simultaneous requests (429) is repeated until it succeeds

        Args:
            methodUrl: url on er (e.g. "/api/v1/article")
            paramDict: optional object containing the parameters to include in the request (e.g. { "articleUri": "123412342" }).
            customLogFName: potentially a file name where the request information can be logged into
            allowUseOfArchive: potentially override the value set when constructing EventRegistry class.
                If not None set it to boolean to determine if the request can be executed on the archive data or not
                If left to None then the value set in the EventRegistry constructor will be used
        """
        self._lastException = None

        # work on a copy so that we don't modify the caller's dict (and don't leak the api key into it)
        paramDict = dict(paramDict) if isinstance(paramDict, dict) else {}
        self._warnAboutIgnoredSortBy(paramDict)

        if self._logRequests:
            # the lock keeps the log entries of concurrent threads from interleaving
            with self._lock:
                try:
                    logFName = customLogFName or self._requestLogFName
                    logDir = os.path.dirname(logFName)
                    if logDir:
                        os.makedirs(logDir, exist_ok=True)
                    with open(logFName, "a", encoding="utf-8") as log:
                        log.write("# " + json.dumps(paramDict) + "\n")
                        log.write(methodUrl + "\n\n")
                except Exception as ex:
                    self._lastException = ex

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

        return self._requestWithRetries(self._host + methodUrl, paramDict, isAnalytics = False)


    def _warnAboutIgnoredSortBy(self, paramDict: dict):
        """
        the server silently ignores some sort options (it accepts them, but returns the results in a different order),
        so log a warning (once per option) when one of them is used
        """
        for name, val in paramDict.items():
            if not (name.endswith("SortBy") and isinstance(val, str)) or val in self._warnedSortBy:
                continue
            valLc = val.lower()
            if valLc in ("socialscore", "facebookshares", "shares"):
                self._warnedSortBy.add(val)
                logger.warning("Sorting by '%s' is no longer supported, since the data about the shares on social media is not collected anymore. The results will be returned unsorted.", val)
            elif valLc in ("id", "twittershares"):
                self._warnedSortBy.add(val)
                logger.warning("Sorting by '%s' is not supported. The results will be sorted by date.", val)


    def jsonRequestAnalytics(self, methodUrl: str, paramDict: dict) -> Any:
        """
        call the analytics service to execute a method like annotation, categorization, etc.

        Args:
            methodUrl: api endpoint url to call
            paramDict: a dictionary with values to send to the api endpoint
        """
        self._lastException = None
        # work on a copy so that we don't modify the caller's dict (and don't leak the api key into it)
        paramDict = dict(paramDict) if isinstance(paramDict, dict) else {}
        if self._apiKey:
            paramDict["apiKey"] = self._apiKey
        return self._requestWithRetries(self._hostAnalytics + methodUrl, paramDict, isAnalytics = True)

    #
    # suggestion methods - return type is a list of matching items

    def suggestConcepts(self,
                        prefix: str,
                        sources: Union[str, list, None] = None,
                        lang: str = "eng",
                        conceptLang: str = "eng",
                        page: int = 1,
                        count: int = 20,
                        returnInfo: Union[ReturnInfo, None] = None,
                        **kwargs) -> List[dict]:
        """
        return a list of concepts that contain the given prefix. returned matching concepts are sorted based on their
            frequency of occurence in news (from most to least frequent)

        Args:
            prefix: input text that should be contained in the concept
            sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki)
            lang: language in which the prefix is specified
            conceptLang: languages in which the label(s) for the concepts are to be returned
            page:  page of the results (1, 2, ...)
            count: number of returned suggestions per page
            returnInfo: what details about concepts should be included in the returned information
        """
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        params = { "prefix": prefix, "source": sources if sources is not None else ["concepts"], "lang": lang, "conceptLang": conceptLang, "page": page, "count": count}
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestConceptsFast", params)


    def suggestCategories(self,
                          prefix: str,
                          page: int = 1,
                          count: int = 20,
                          returnInfo: Union[ReturnInfo, None] = None,
                          **kwargs) -> List[dict]:
        """
        return a list of dmoz categories that contain the prefix

        Args:
            prefix: input text that should be contained in the category name
            page:  page of the results (1, 2, ...)
            count: number of returned suggestions
            returnInfo: what details about categories should be included in the returned information
        """
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        params = { "prefix": prefix, "page": page, "count": count }
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestCategoriesFast", params)


    def suggestNewsSources(self,
                           prefix: str,
                           dataType: Union[str, list, None] = None,
                           page: int = 1,
                           count: int = 20,
                           **kwargs) -> List[dict]:
        """
        return a list of news sources that match the prefix

        Args:
            prefix: input text that should be contained in the source name or uri
            dataType: suggest sources that provide content in these data types ("news", "pr", "blog" or a list of any of those)
            page: page of results
            count: number of returned suggestions
        """
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        params = {"prefix": prefix, "dataType": dataType if dataType is not None else ["news", "pr", "blog"], "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestSourceGroups(self, prefix: str, page: int = 1, count: int = 20, **kwargs) -> List[dict]:
        """
        return a list of news source groups that match the prefix

        Args:
            prefix: input text that should be contained in the source group name or uri
            page:  page of the results (1, 2, ...)
            count: number of returned suggestions
        """
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        params = { "prefix": prefix, "page": page, "count": count }
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourceGroups", params)


    def suggestLocations(self,
                         prefix: str,
                         sources: Union[str, list, None] = None,
                         lang: str = "eng",
                         count: int = 20,
                         countryUri: Union[str, None] = None,
                         sortByDistanceTo: Union[List, Tuple, None] = None,
                         returnInfo: Union[ReturnInfo, None] = None,
                         **kwargs) -> List[dict]:
        """
        return a list of geo locations (cities or countries) that contain the prefix

        Args:
            prefix: input text that should be contained in the location name
            source: what types of locations are we interested in. Possible options are "place" and "country"
            lang: language in which the prefix is specified
            count: number of returned suggestions
            countryUri: if provided, then return only those locations that are inside the specified country
            sortByDistanceTo: if provided, then return the locations sorted by the distance to the (lat, long) provided in the tuple
            returnInfo: what details about locations should be included in the returned information
        """
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        params = { "prefix": prefix, "count": count, "source": sources if sources is not None else ["place", "country"], "lang": lang, "countryUri": countryUri or "" }
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())
        params.update(kwargs)
        if sortByDistanceTo:
            if not (isinstance(sortByDistanceTo, (tuple, list))):
                raise TypeError("sortByDistanceTo has to contain a tuple with latitude and longitude of the location")
            if not (len(sortByDistanceTo) == 2):
                raise ValueError("The sortByDistanceTo should contain two float numbers")
            params["closeToLat"] = sortByDistanceTo[0]
            params["closeToLon"] = sortByDistanceTo[1]
        return self.jsonRequest("/api/v1/suggestLocationsFast", params)


    def suggestLocationsAtCoordinate(self,
                                     latitude: Union[int, float],
                                     longitude: Union[int, float],
                                     radiusKm: Union[int, float],
                                     limitToCities: bool = False,
                                     lang: str = "eng",
                                     count: int = 20,
                                     returnInfo: Union[ReturnInfo, None] = None,
                                     **kwargs) -> List[dict]:
        """
        return a list of geo locations (cities or places) that are close to the provided (lat, long) values

        Args:
            latitude: latitude part of the coordinate
            longitude: longitude part of the coordinate
            radiusKm: radius in kilometres around the coordinates inside which the locations should be returned
            limitToCities: limit the set of results only to cities (True) or also to general places (False)
            lang: language in which the location label should be returned
            count: number of returned suggestions
            returnInfo: what details about locations should be included in the returned information
        """
        if not (isinstance(latitude, (int, float))):
            raise TypeError("The 'latitude' should be a number")
        if not (isinstance(longitude, (int, float))):
            raise TypeError("The 'longitude' should be a number")
        params = { "action": "getLocationsAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "limitToCities": limitToCities, "count": count, "lang": lang }
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestLocationsFast", params)


    def suggestSourcesAtCoordinate(self,
                                   latitude: Union[int, float],
                                   longitude: Union[int, float],
                                   radiusKm: Union[int, float],
                                   count: int = 20,
                                   **kwargs) -> List[dict]:
        """
        return a list of news sources that are close to the provided (lat, long) values

        Args:
            latitude: latitude part of the coordinate
            longitude: longitude part of the coordinate
            radiusKm: radius in kilometres around the coordinates inside which the news sources should be located
            count: number of returned suggestions
        """
        if not (isinstance(latitude, (int, float))):
            raise TypeError("The 'latitude' should be a number")
        if not (isinstance(longitude, (int, float))):
            raise TypeError("The 'longitude' should be a number")
        params = {"action": "getSourcesAtCoordinate", "lat": latitude, "lon": longitude, "radius": radiusKm, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestSourcesAtPlace(self, conceptUri: str, dataType: Union[str, List[str]] = "news", page: int = 1, count: int = 20, **kwargs) -> List[dict]:
        """
        return a list of news sources that are located at the place identified by the provided location concept

        Args:
            conceptUri: concept that represents a geographic location for which we would like to obtain a list of sources located at the place
            dataType: type of the news source ("news", "pr", "blog" or a list of any of those)
            page: page of the results (1, 2, ...)
            count: number of returned sources
        """
        if not (isinstance(conceptUri, str)):
            raise TypeError("The 'conceptUri' should be a string")
        params = {"action": "getSourcesAtPlace", "conceptUri": conceptUri, "page": page, "count": count, "dataType": dataType}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestSourcesFast", params)


    def suggestAuthors(self, prefix: str, page: int = 1, count: int = 20, **kwargs) -> List[dict]:
        """
        return a list of authors that match the prefix

        Args:
            prefix: input text that should be contained in the author name and source url
            page: page of results
            count: number of returned suggestions
        """
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestAuthorsFast", params)


    def suggestEventTypes(self, prefix: str, page: int = 1, count: int = 20, **kwargs) -> List[dict]:
        """
        return a list of event types that match the prefix

        Args:
            prefix: input text that should be contained in the industry name
            page: page of results
            count: number of returned suggestions
        """
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/eventType/suggestEventTypes", params)


    def suggestIndustries(self, prefix: str, page: int = 1, count: int = 20, **kwargs) -> List[dict]:
        """
        return a list of industries that match the prefix. Note: Industries can only be used when querying mentions (QueryMentions, QueryMentionsIter)

        Args:
            prefix: input text that should be contained in the industry name
            page: page of results
            count: number of returned suggestions
        """
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        params = {"prefix": prefix, "page": page, "count": count}
        params.update(kwargs)
        return self.jsonRequest("/api/v1/eventType/suggestIndustries", params)


    def getSdgUris(self) -> dict:
        """
        return a list of SDG uris. Note: Industries can only be used when querying mentions (QueryMentions, QueryMentionsIter)
        """
        return self.jsonRequest("/api/v1/eventType/sdg/getItems", {})


    def getSasbUris(self) -> dict:
        """
        return a list of SASB uris. Note: SASB uris can only be used when querying mentions (QueryMentions, QueryMentionsIter)
        """
        return self.jsonRequest("/api/v1/eventType/sasb/getItems", {})


    def suggestConceptClasses(self,
                              prefix: str,
                              lang: str = "eng",
                              conceptLang: str = "eng",
                              source: Union[str, List[str], None] = None,
                              page: int = 1,
                              count: int = 20,
                              returnInfo: Union[ReturnInfo, None] = None,
                              **kwargs) -> List[dict]:
        """
        return a list of concept classes that match the given prefix

        Args:
            prefix: input text that should be contained in the category name
            lang: language in which the prefix is specified
            conceptLang: languages in which the label(s) for the concepts are to be returned
            source: what types of concepts classes should be returned. valid values are 'dbpedia' or 'custom'
            page:  page of the results (1, 2, ...)
            count: number of returned suggestions
            returnInfo: what details about categories should be included in the returned information
        """
        if not (isinstance(prefix, str)):
            raise TypeError("The 'prefix' should be a string")
        if not (page > 0):
            raise ValueError("page parameter should be above 0")
        params = { "prefix": prefix, "lang": lang, "conceptLang": conceptLang, "source": source if source is not None else ["dbpedia", "custom"], "page": page, "count": count }
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams())
        params.update(kwargs)
        return self.jsonRequest("/api/v1/suggestConceptClasses", params)


    #
    # get info methods - return type is a single item that is the best match to the given input


    def getConceptUri(self,
                      conceptLabel: str,
                      lang: str = "eng",
                      sources: Union[str, List[str], None] = None) -> Optional[str]:
        """
        return a concept uri that is the best match for the given concept label
        if there are multiple matches for the given conceptLabel, they are sorted based on their frequency of occurence in news (most to least frequent)

        Args:
            conceptLabel: partial or full name of the concept for which to return the concept uri
            sources: what types of concepts should be returned. valid values are person, loc, org, wiki, entities (== person + loc + org), concepts (== entities + wiki)
        """
        if not (isinstance(conceptLabel, str)):
            raise TypeError("The 'conceptLabel' should be a string")
        if not (isinstance(lang, str)):
            raise TypeError("The 'lang' should be a string")
        matches = self.suggestConcepts(conceptLabel, lang = lang, sources = sources)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getLocationUri(self,
                       locationLabel: str,
                       lang: str = "eng",
                       sources: Union[str, List[str], None] = None,
                       countryUri: Union[str, None] = None,
                       sortByDistanceTo: Union[List, Tuple, None] = None) -> Optional[str]:
        """
        return a location uri that is the best match for the given location label

        Args:
            locationLabel: partial or full location name for which to return the location uri
            sources: what types of locations are we interested in. Possible options are "place" and "country"
            countryUri: if set, then filter the possible locatiosn to the locations from that country
            sortByDistanceTo: sort candidates by distance to the given (lat, long) pair
        """
        if not (isinstance(locationLabel, str)):
            raise TypeError("The 'locationLabel' should be a string")
        if not (isinstance(lang, str)):
            raise TypeError("The 'lang' should be a string")
        matches = self.suggestLocations(locationLabel, sources = sources, lang = lang, countryUri = countryUri, sortByDistanceTo = sortByDistanceTo)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "wikiUri" in matches[0]:
            return matches[0]["wikiUri"]
        return None


    def getCategoryUri(self, categoryLabel: str) -> Optional[str]:
        """
        return a category uri that is the best match for the given label

        Args:
            categoryLabel: partial or full name of the category for which to return category uri
        """
        if not (isinstance(categoryLabel, str)):
            raise TypeError("The 'categoryLabel' should be a string")
        matches = self.suggestCategories(categoryLabel)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getNewsSourceUri(self,
                         sourceName: str,
                         dataType: Union[str, List[str], None] = None) -> Optional[str]:
        """
        return the news source that best matches the source name

        Args:
            sourceName: partial or full name of the source or source uri for which to return source uri
            dataType: return the source uri that provides content of these data types ("news", "pr", "blog" or a list of any of those)
        """
        if not (isinstance(sourceName, str)):
            raise TypeError("The 'sourceName' should be a string")
        matches = self.suggestNewsSources(sourceName, dataType = dataType)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getSourceUri(self,
                     sourceName: str,
                     dataType: Union[str, List[str], None] = None) -> Optional[str]:
        """
        alternative (shorter) name for the method getNewsSourceUri()
        """
        return self.getNewsSourceUri(sourceName, dataType)


    def getSourceGroupUri(self, sourceGroupName: str) -> Optional[str]:
        """
        return the URI of the source group that best matches the name

        Args:
            sourceGroupName: partial or full name of the source group
        """
        matches = self.suggestSourceGroups(sourceGroupName)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptClassUri(self, classLabel: str, lang: str = "eng") -> Optional[str]:
        """
        return a uri of the concept class that is the best match for the given label

        Args:
            classLabel: partial or full name of the concept class for which to return class uri
        """
        matches = self.suggestConceptClasses(classLabel, lang = lang)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getConceptInfo(self, conceptUri: str,
                       returnInfo: Union[ReturnInfo, None] = None) -> dict:
        """
        return detailed information about a particular concept

        Args:
            conceptUri: uri of the concept
            returnInfo: what details about the concept should be included in the returned information
        """
        params = (returnInfo if returnInfo is not None else ReturnInfo(conceptInfo = ConceptInfoFlags(synonyms = True, image = True, description = True))).getParams()
        params.update({"uri": conceptUri })
        return self.jsonRequest("/api/v1/concept/getInfo", params)


    def getAuthorUri(self, authorName: str) -> Optional[str]:
        """
        return author uri that is the best match for the given author name (and potentially source url)
        if there are multiple matches for the given author name, they are sorted based on the number of articles they have written (from most to least frequent)

        Args:
            authorName: partial or full name of the author, potentially also containing the source url (e.g. "george brown nytimes")
        """
        matches = self.suggestAuthors(authorName)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    def getEventTypeUri(self, eventTypeLabel: str) -> Optional[str]:
        """
        return event type uri that is the best match for the given label

        Args:
            eventTypeLabel: partial or full name of the event type for which we want to retrieve uri
        """
        matches = self.suggestEventTypes(eventTypeLabel)
        if matches is not None and isinstance(matches, list) and len(matches) > 0 and "uri" in matches[0]:
            return matches[0]["uri"]
        return None


    @staticmethod
    def getUriFromUriWgt(uriWgtList: List[str]) -> List[str]:
        """
        convert an array of items that contain uri:wgt to a list of items with uri only. Used for QueryArticle and QueryEvent classes
        """
        if not (isinstance(uriWgtList, list)):
            raise TypeError("uriWgtList has to be a list of strings that represent article uris")
        uriList = [uriWgt.split(":")[0] for uriWgt in uriWgtList]
        return uriList


    #
    # additional utility methods


    def getArticleUris(self, articleUrl: str) -> dict:
        """
        if you have an article url and you want to query it in ER you first have to obtain its uri in the ER.

        Args:
            articleUrl: a single article url (the endpoint accepts only one url per call)

        Returns:
            returns dict where key is article url and value is either None if no match found or a string with article URI.
        """
        if not (isinstance(articleUrl, str)):
            raise TypeError("Expected a single article url as a string")
        return self.jsonRequest("/api/v1/articleMapper", { "articleUrl": articleUrl })


    def getSourceGroups(self) -> dict:
        """return the list of URIs of all known source groups"""
        ret = self.jsonRequest("/api/v1/sourceGroup/getSourceGroups", {})
        return ret


    def getSourceGroup(self, sourceGroupUri: str) -> dict:
        """return info about the source group"""
        if not (isinstance(sourceGroupUri, str)):
            raise TypeError("The 'sourceGroupUri' should be a string")
        ret = self.jsonRequest("/api/v1/sourceGroup/getSourceGroupInfo", { "uri": sourceGroupUri })
        return ret


    #
    # internal methods


    def _getHttpErrorMessage(self, respInfo) -> str:
        """describe a failed HTTP response: status code, its meaning (if known) and the text returned by the server"""
        description = self._httpStatusCodes.get(respInfo.status_code, "Unexpected status code")
        return "HTTP status code %d (%s): %s" % (respInfo.status_code, description, respInfo.text)


    def _requestWithRetries(self, url: str, paramDict: dict, isAnalytics: bool) -> Any:
        """
        make the request and return the returned json. A request that fails with a temporary error (EventRegistryError.isTemporary:
        connection problem, timeout, 5xx, invalid json) is repeated up to _repeatFailedRequestCount times (indefinitely if -1).
        A request rejected because of too many simultaneous requests (429) is always repeated: it succeeds once the other requests
        finish, while raising the error would end an iteration over the results that could then not be resumed.
        Other errors are raised immediately, since repeating the request would give the same result.
        We wait between the attempts without holding the lock, so a failing request does not block the requests of other threads.
        """
        tryCount = 0        # failed attempts so far - sets the delay before the next one
        failedCount = 0     # failed attempts that count towards _repeatFailedRequestCount (all except 429)
        while True:
            try:
                return self._requestOnce(url, paramDict, isAnalytics)
            except EventRegistryError as ex:
                self._lastException = ex
                if self._verboseOutput:
                    logger.error("Event Registry exception while executing the request:")
                    logger.error("endpoint: %s\nParams: %s", url, self._getParamsForLog(paramDict))
                    self.printLastException()
                if not ex.isTemporary:
                    raise
                tryCount += 1
                if isinstance(ex, RateLimitError):
                    logger.warning("Too many simultaneous requests. At most %d requests can be executed at the same time - make the requests sequentially, one after the other.", self._maxSimultaneousRequests)
                else:
                    failedCount += 1
                    if self._repeatFailedRequestCount >= 0 and failedCount > self._repeatFailedRequestCount:
                        raise
                delay = self._getRetryDelay(ex, tryCount)
                logger.info("The request will be automatically repeated in %d seconds...", delay)
                time.sleep(delay)


    def _requestOnce(self, url: str, paramDict: dict, isAnalytics: bool) -> Any:
        """
        make a single request and return the returned json. Raise an EventRegistryError subclass if the request fails.
        The requests of an instance are made one at a time - the requests module otherwise sometimes returns incomplete json objects
        """
        with self._lock:
            self._headers = {}  # reset any past data
            # throttle inside the lock so that concurrent threads cannot all pass the check at once
            if not isAnalytics:
                self._sleepIfNecessary()
            try:
                respInfo = self._reqSession.post(url, json = paramDict, timeout = 60)
            except requests.exceptions.RequestException as ex:
                raise NetworkError(f"The request to {url} failed: {ex}", url = url) from ex
            # remember the returned headers
            self._headers = respInfo.headers
            if respInfo.status_code != 200:
                raise self._getErrorForResponse(respInfo, url)
            if not isAnalytics:
                # did we get a warning. if yes, print it
                if self.getLastHeader("warning"):
                    logger.warning("=========== WARNING ===========\n%s\n===============================", self.getLastHeader("warning"))
                # remember the available requests
                self._dailyAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-limit", ""), val = -1)
                self._remainingAvailableRequests = tryParseInt(self.getLastHeader("x-ratelimit-remaining", ""), val = -1)
            try:
                return respInfo.json()
            except ValueError as ex:
                raise InvalidResponseError(f"The response of {url} is not valid json: {respInfo.text[:200]}",
                                           statusCode = respInfo.status_code, responseText = respInfo.text, url = url) from ex


    def _getErrorForResponse(self, respInfo, url: str) -> EventRegistryError:
        """the exception describing a response with a status code other than 200"""
        errorClass = getErrorClassForStatusCode(respInfo.status_code)
        retryAfter = tryParseInt(respInfo.headers.get("Retry-After", ""), val = None) if respInfo.headers else None
        return errorClass(self._getHttpErrorMessage(respInfo), statusCode = respInfo.status_code,
                          responseText = respInfo.text, url = url, retryAfter = retryAfter)


    @staticmethod
    def _getRetryDelay(error: EventRegistryError, tryCount: int) -> int:
        """seconds to wait before repeating the request: what the server asked for (Retry-After) or an exponentially growing delay"""
        if error.retryAfter is not None and error.retryAfter > 0:
            return min(error.retryAfter, MAX_RETRY_DELAY)
        return min(RETRY_BASE_DELAY * 2 ** (tryCount - 1), MAX_RETRY_DELAY)


    @staticmethod
    def _getParamsForLog(paramDict: dict) -> str:
        """the request parameters as json, with the api key and proxy credentials masked so that they don't end up in logs"""
        params = dict(paramDict)
        if params.get("apiKey"):
            params["apiKey"] = "***"
        if isinstance(params.get("proxyUrl"), str):
            params["proxyUrl"] = re.sub(r"//[^/@]+@", "//***@", params["proxyUrl"])
        return json.dumps(params, indent = 4)


    def _sleepIfNecessary(self):
        """ensure that queries are not made too fast"""
        t = time.time()
        if t - self._lastQueryTime < self._minDelayBetweenRequests:
            time.sleep(self._minDelayBetweenRequests - (t - self._lastQueryTime))
        self._lastQueryTime = time.time()



class ArticleMapper:
    def __init__(self, er: EventRegistry, rememberMappings: bool = True):
        """
        create instance of article mapper
        it will map from article urls to article uris
        the mappings can be remembered so it will not repeat requests for the same article urls
        """
        self._er = er
        self._articleUrlToUri: Dict[str, Any] = {}
        self._rememberMappings = rememberMappings


    def getArticleUri(self, articleUrl: str):
        """
        given the article url, return the corresponding article uri(s) as mapped by the server, or None if the url is not known.
        Not all returned article uris are necessarily valid anymore. For news sources of lower importance
        we remove the duplicated articles and just keep the latest content

        Args:
            articleUrl: string containing the article url

        Returns:
            value provided by the server for the given url (a string or a list of strings representing article uris) or None if no mapping exists
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
