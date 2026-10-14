"""
class that provides the ability to use topic pages (monitoring functionality)
through the API
"""

import datetime
import os
import json
from eventregistry.Base import QueryParamsBase
from eventregistry.ReturnInfo import ReturnInfo
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List

# the names exported by "from eventregistry import *"
__all__ = ["TopicPages", "TopicPage"]


class TopicPages(QueryParamsBase):
    """
    get the list of user owned topic pages
    """
    def __init__(self, eventRegistry: EventRegistry):
        """
        create an instance of a topic page

        Args:
            eventRegistry: instance of class EventRegistry
        """
        super().__init__()
        self.eventRegistry = eventRegistry


    def getMyTopicPages(self):
        """
        get the list of topic pages owned by me
        """
        userProfile = self.eventRegistry.jsonRequest("/api/v1/user/getUserProfile", {})
        return userProfile.get("ownedTopicPages", [])



class TopicPage(QueryParamsBase):
    def __init__(self, eventRegistry: EventRegistry):
        """
        create an instance of a topic page

        Args:
            eventRegistry: instance of class EventRegistry
        """
        super().__init__()
        self.eventRegistry = eventRegistry
        # topic page definition
        self.topicPage = self._createEmptyTopicPage()
        self.concept: dict = {}


    def _createEmptyTopicPage(self):
        return {
            "autoAddArticles": True,

            "articleHasDuplicate": "keepAll",
            "articleHasEvent": "keepAll",
            "articleIsDuplicate": "skipDuplicates",
            "maxDaysBack": 7,
            "articleTreshWgt": 0,
            "eventTreshWgt": 0,

            "concepts": [],
            "keywords": [],
            "categories": [],
            "sources": [],
            "sourceGroups": [],
            "sourceLocations": [],
            "locations": [],
            "langs": [],
            "restrictToSetConcepts": False,
            "restrictToSetCategories": False,
            "restrictToSetSources": False,
            "restrictToSetLocations": False,

            "dataType": [ "news" ]
        }


    def loadTopicPageFromER(self, uri: str):
        """
        load an existing topic page from Event Registry based on the topic page URI

        Args:
            uri: uri of the topic page saved in your Event Registry account
        """
        params = {
            "action": "getTopicPageJson",
            "includeConceptDescription": True,
            "includeConceptImage": True,
            "includeTopicPageDefinition": True,
            "includeTopicPageOwner": True,
            "uri": uri
        }
        self.topicPage = self._createEmptyTopicPage()
        self.concept = self.eventRegistry.jsonRequest("/api/v1/topicPage", params)
        self.topicPage.update(self.concept.get("topicPage", {}))


    def loadTopicPageFromDefinition(self, definitionDict: dict):
        """
        load the topic page definition from a python dictionary
        """
        if not (isinstance(definitionDict, dict)):
            raise TypeError("definitionDict should be of type dict")
        # start from the default definition, so that the properties missing in the provided definition have a value
        self.topicPage = self._createEmptyTopicPage()
        self.topicPage.update(definitionDict)


    def loadTopicPageFromFile(self, fname: str):
        """
        load topic page from an existing file
        """
        if not (os.path.exists(fname)):
            raise FileNotFoundError(f"file {fname} does not exist")
        with open(fname, "r", encoding="utf-8") as f:
            self.loadTopicPageFromDefinition(json.load(f))


    def saveTopicPageDefinition(self):
        """
        return a python dict containing the topic page definition. you can use it to load a topic page later
        """
        return self.topicPage


    def saveTopicPageDefinitionToFile(self, fname: str):
        """
        save the topic page definition to a file
        """
        with open(fname, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.topicPage, indent = 4, sort_keys = True))

    #
    # methods for adding filters to the topic
    #

    def setArticleThreshold(self, value: int):
        """
        what is the minimum total weight that an article has to have in order to get it among the results?

        Args:
            value: threshold to use
        """
        if not (isinstance(value, int)):
            raise TypeError("value should be of type int")
        if not (value >= 0):
            raise ValueError("value should be at least 0")
        self.topicPage["articleTreshWgt"] = value


    def setEventThreshold(self, value: int):
        """
        what is the minimum total weight that an event has to have in order to get it among the results?

        Args:
            value: threshold to use
        """
        if not (isinstance(value, int)):
            raise TypeError("value should be of type int")
        if not (value >= 0):
            raise ValueError("value should be at least 0")
        self.topicPage["eventTreshWgt"] = value


    def setArticleIsDuplicateFilter(self, value: str):
        """
        Args:
            value: some articles can be duplicates of other articles. What should be done with them. Possible values are:
                "skipDuplicates" (skip the resulting articles that are duplicates of other articles)
                "keepOnlyDuplicates" (return only the duplicate articles)
                "keepAll" (no filtering, default)
        """
        if not (value == "skipDuplicates" or value == "keepOnlyDuplicates" or value == "keepAll"):
            raise ValueError("value should be one of: skipDuplicates, keepOnlyDuplicates, keepAll")
        self.topicPage["articleIsDuplicate"] = value


    def setArticleHasEventFilter(self, value: str):
        """
        Args:
            value: some articles describe a known event and some don't. This filter allows you to filter the resulting articles based on this criteria.
                Possible values are:
                "skipArticlesWithoutEvent" (skip articles that are not describing any known event in ER)
                "keepOnlyArticlesWithoutEvent" (return only the articles that are not describing any known event in ER)
                "keepAll" (no filtering, default)
        """
        if not (value == "skipArticlesWithoutEvent" or value == "keepOnlyArticlesWithoutEvent" or value == "keepAll"):
            raise ValueError("value should be one of: skipArticlesWithoutEvent, keepOnlyArticlesWithoutEvent, keepAll")
        self.topicPage["articleHasEvent"] = value


    def setArticleHasDuplicateFilter(self, value: str):
        """
        Args:
            value: some articles are later copied by others. What should be done with such articles. Possible values are:
                "skipHasDuplicates" (skip the articles that have been later copied by others)
                "keepOnlyHasDuplicates" (return only the articles that have been later copied by others)
                "keepAll" (no filtering, default)
        """
        if not (value == "skipHasDuplicates" or value == "keepOnlyHasDuplicates" or value == "keepAll"):
            raise ValueError("value should be one of: skipHasDuplicates, keepOnlyHasDuplicates, keepAll")
        self.topicPage["articleHasDuplicate"] = value


    def setDataTypes(self, dataTypes: Union[str, List[str]]):
        """
        what data types should we search? "news" (news content, default), "pr" (press releases), or "blog".
            If you want to use multiple data types, put them in an array (e.g. ["news", "pr"])
        """
        self.topicPage["dataType"] = dataTypes


    def setMaxDaysBack(self, maxDaysBack: int):
        """
        what is the maximum allowed age of the results?
        """
        if not (isinstance(maxDaysBack, int)):
            raise TypeError("maxDaysBack value has to be a positive integer")
        if not (maxDaysBack >= 1):
            raise ValueError("maxDaysBack should be at least 1")
        self.topicPage["maxDaysBack"] = maxDaysBack


    def setSourceRankPercentile(self, startPercentile: int = 0, endPercentile: int = 100):
        if not (startPercentile >= 0 and startPercentile <= 90):
            raise ValueError("startPercentile is out of valid values (0 - 90)")
        if not (endPercentile >= 10 and endPercentile <= 100):
            raise ValueError("endPercentile is out of valid values (10 - 100)")
        if not (startPercentile < endPercentile):
            raise ValueError("startPercentile has to be smaller than endPercentile")
        if not (startPercentile % 10 == 0):
            raise ValueError("startPecentile has to be a multiple of 10")
        if not (endPercentile % 10 == 0):
            raise ValueError("endPercentile has to be a multiple of 10")
        self.topicPage["startSourceRankPercentile"] = startPercentile
        self.topicPage["endSourceRankPercentile"] = endPercentile


    def setSentiment(self, minSentiment: float = -1, maxSentiment: float = 1):
        """
        what should be the sentiment of the returned articles and events?
        """
        if not (minSentiment >= -1):
            raise ValueError("minSentiment has to be >= -1")
        if not (maxSentiment <= 1):
            raise ValueError("maxSentiment has to be <= 1")
        self.topicPage["minSentiment"] = minSentiment
        self.topicPage["maxSentiment"] = maxSentiment


    def clearConcepts(self):
        self.topicPage["concepts"] = []


    def clearKeywords(self):
        self.topicPage["keywords"] = []


    def clearCategories(self):
        self.topicPage["categories"] = []


    def clearSources(self):
        self.topicPage["sources"] = []


    def clearSourceLocations(self):
        self.topicPage["sourceLocations"] = []


    def clearSourceGroups(self):
        self.topicPage["sourceGroups"] = []


    def clearLocations(self):
        self.topicPage["locations"] = []


    def addConcept(self, conceptUri: str, weight: float, label: Union[str, None] = None, conceptType: Union[str, None] = None, required: bool = False, excluded: bool = False):
        """
        add a relevant concept to the topic page

        Args:
            conceptUri: uri of the concept to be added
            weight: importance of the provided concept (typically in range 1 - 50)
            required: if true, then all results will HAVE TO be annotated with this concept
            excluded: if true, then all results annotated with this concept will be ignored
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(conceptUri, str)):
            raise TypeError("conceptUri has to be a string")
        if not (len(conceptUri) > 0):
            raise ValueError("conceptUri can not be an empty string")
        if not (not (required is True and excluded is True)):
            raise ValueError("Parameters required and excluded can not be True at the same time")
        concept = {"uri": conceptUri, "wgt": weight, "required": required, "excluded": excluded }
        if label is not None:
            concept["label"] = label
        if conceptType is not None:
            concept["type"] = conceptType
        self.topicPage["concepts"].append(concept)


    def addKeyword(self, keyword: str, weight: float, required: bool = False, excluded: bool = False):
        """
        add a relevant keyword to the topic page

        Args:
            keyword: keyword or phrase to be added
            weight: importance of the provided keyword (typically in range 1 - 50)
            required: if true, then all results will HAVE TO mention this keyword to appear in the results
            excluded: if true, then no results that mention this keyword will be returned
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(keyword, str)):
            raise TypeError("keyword has to be a string")
        if not (len(keyword) > 0):
            raise ValueError("keyword can not be an empty string")
        if not (not (required is True and excluded is True)):
            raise ValueError("Parameters required and excluded can not be True at the same time")
        self.topicPage["keywords"].append({"keyword": keyword, "wgt": weight, "required": required, "excluded": excluded })


    def addCategory(self, categoryUri: str, weight: float, required: bool = False, excluded: bool = False):
        """
        add a relevant category to the topic page

        Args:
            categoryUri: uri of the category to be added
            weight: importance of the provided category (typically in range 1 - 50)
            required: if true, then all results will HAVE TO be annotated with this category to appear in the results
            excluded: if true, then no results with this category will be returned
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(categoryUri, str)):
            raise TypeError("categoryUri has to be a string")
        if not (len(categoryUri) > 0):
            raise ValueError("categoryUri can not be an empty string")
        if not (not (required is True and excluded is True)):
            raise ValueError("Parameters required and excluded can not be True at the same time")
        self.topicPage["categories"].append({"uri": categoryUri, "wgt": weight, "required": required, "excluded": excluded })


    def addSource(self, sourceUri: str, weight: float, excluded: bool = False):
        """
        add a news source to the topic page

        Args:
            sourceUri: uri of the news source to add to the topic page
            weight: importance of the news source (typically in range 1 - 50)
            excluded: if true, then the results from these sources will be ignored
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(sourceUri, str)):
            raise TypeError("sourceUri has to be a string")
        if not (len(sourceUri) > 0):
            raise ValueError("sourceUri can not be an empty string")
        self.topicPage["sources"].append({"uri": sourceUri, "wgt": weight, "excluded": excluded })


    def addSourceLocation(self, sourceLocationUri: str, weight: float, excluded: bool = False):
        """
        add a list of relevant sources by identifying them by their geographic location

        Args:
            sourceLocationUri: uri of the location where the sources should be geographically located
            weight: importance of the provided list of sources (typically in range 1 - 50)
            excluded: if true, then the results from the sources from this location will be ignored
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(sourceLocationUri, str)):
            raise TypeError("sourceLocationUri has to be a string")
        if not (len(sourceLocationUri) > 0):
            raise ValueError("sourceLocationUri can not be an empty string")
        self.topicPage["sourceLocations"].append({"uri": sourceLocationUri, "wgt": weight, "excluded": excluded })


    def addSourceGroup(self, sourceGroupUri: str, weight: float, excluded: bool = False):
        """
        add a list of relevant sources by specifying a whole source group to the topic page

        Args:
            sourceGroupUri: uri of the source group to add
            weight: importance of the provided list of sources (typically in range 1 - 50)
            excluded: if true, then the results from sources from this group will be ignored
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(sourceGroupUri, str)):
            raise TypeError("sourceGroupUri has to be a string")
        if not (len(sourceGroupUri) > 0):
            raise ValueError("sourceGroupUri can not be an empty string")
        self.topicPage["sourceGroups"].append({"uri": sourceGroupUri, "wgt": weight, "excluded": excluded })


    def addLocation(self, locationUri: str, weight: float):
        """
        add relevant location to the topic page

        Args:
            locationUri: uri of the location to add
            weight: importance of the provided location (typically in range 1 - 50)
        """
        if not (isinstance(weight, (float, int))):
            raise TypeError("weight value has to be a positive or negative integer")
        if not (isinstance(locationUri, str)):
            raise TypeError("locationUri has to be a string")
        if not (len(locationUri) > 0):
            raise ValueError("locationUri can not be an empty string")
        self.topicPage["locations"].append({"uri": locationUri, "wgt": weight})


    def setLanguages(self, languages: Union[str, List[str]]):
        """
        restrict the results to the list of specified languages
        """
        if isinstance(languages, str):
            languages = [languages]
        for lang in languages:
            if not (len(lang) == 3):
                raise ValueError("Expected to get language in ISO3 code")
        self.topicPage["langs"] = languages


    def restrictToSetConceptsAndKeywords(self, restrict: bool):
        """
        if true then the results have to mention at least one of the specified concepts or keywords
        """
        if not (isinstance(restrict, bool)):
            raise TypeError("restrict value has to be a boolean value")
        self.topicPage["restrictToSetConcepts"] = restrict


    def restrictToSetCategories(self, restrict: bool):
        """
        if set to true then return only results that are assigned to one of the specified categories
        """
        if not (isinstance(restrict, bool)):
            raise TypeError("restrict value has to be a boolean value")
        self.topicPage["restrictToSetCategories"] = restrict


    def restrictToSetSources(self, restrict: bool):
        """
        if set to true then return only results from one of the specified news sources
        this includes also sources set by source groups or by source locations
        """
        if not (isinstance(restrict, bool)):
            raise TypeError("restrict value has to be a boolean value")
        self.topicPage["restrictToSetSources"] = restrict


    def restrictToSetLocations(self, restrict: bool):
        """
        if set to true, then return only results that are located at one of the specified locations
        """
        if not (isinstance(restrict, bool)):
            raise TypeError("restrict value has to be a boolean value")
        self.topicPage["restrictToSetLocations"] = restrict


    #
    # getting content
    #


    def _getContentParams(self, uri: Union[str, None], onlyAfterTm, maxDaysBack: Union[int, None]) -> dict:
        """
        the parameters that specify for which topic page and what time period we want the content
        """
        params: dict = {}
        if uri is not None:
            # use the topic page that is saved on the server
            params["uri"] = uri
        else:
            params["dataType"] = self.topicPage["dataType"]
            params["topicPage"] = json.dumps(self.topicPage)
        if onlyAfterTm is not None:
            params["onlyAfterTm"] = QueryParamsBase.encodeDateTime(onlyAfterTm)
        if maxDaysBack is not None:
            params["maxDaysBack"] = maxDaysBack
        return params


    def getArticles(self,
                page: int = 1,
                count: int = 100,
                sortBy: str = "rel",
                sortByAsc: bool = False,
                returnInfo: Union[ReturnInfo, None] = None,
                uri: Union[str, None] = None,
                onlyAfterTm: Union[datetime.datetime, str, None] = None,
                maxDaysBack: Union[int, None] = None,
                **kwargs):
        """
        return a list of articles that match the topic page

        Args:
            page: which page of the results to return (default: 1)
            count: number of articles to return (default: 100)
            sortBy: how are articles sorted. Options: date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            uri: the uri of a topic page saved in your Event Registry account. If given, the articles that match the saved
                topic page are returned, instead of the ones that match the definition in this object (which is then not sent to the server)
            onlyAfterTm: return only the articles that were added to Event Registry after the given time (a datetime or
                a string in the 'YYYY-MM-DDTHH:MM:SS' format, in UTC). Useful to repeatedly get just the new articles: remember
                the time of the previous call and use it in the next one
            maxDaysBack: the returned articles should not be older than this number of days. If None, the value set
                in the topic page is used
        """
        if not (page >= 1):
            raise ValueError("page should be at least 1")
        if not (count <= 100):
            raise ValueError("count should be at most 100")
        params = {
            "action": "getArticlesForTopicPage",
            "resultType": "articles",
            "articlesCount": count,
            "articlesSortBy": sortBy,
            "articlesSortByAsc": sortByAsc,
            "articlesPage": page
        }
        params.update(self._getContentParams(uri, onlyAfterTm, maxDaysBack))
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("articles"))
        params.update(kwargs)
        return self.eventRegistry.jsonRequest("/api/v1/article", params)


    def getEvents(self,
                page: int = 1,
                count: int = 50,
                sortBy: str = "rel",
                sortByAsc: bool = False,
                returnInfo: Union[ReturnInfo, None] = None,
                uri: Union[str, None] = None,
                onlyAfterTm: Union[datetime.datetime, str, None] = None,
                maxDaysBack: Union[int, None] = None,
                **kwargs):
        """
        return a list of events that match the topic page

        Args:
            page: which page of the results to return (default: 1)
            count: number of events to return (default: 50)
            sortBy: how are events sorted. Options: date (by event date), rel (relevance to the query), size (number of articles), none (no specific sorting)
            sortByAsc: should the results be sorted in ascending order (True) or descending (False)
            returnInfo: what details should be included in the returned information
            uri: the uri of a topic page saved in your Event Registry account. If given, the events that match the saved
                topic page are returned, instead of the ones that match the definition in this object (which is then not sent to the server)
            onlyAfterTm: return only the events that were added or updated after the given time (a datetime or
                a string in the 'YYYY-MM-DDTHH:MM:SS' format, in UTC)
            maxDaysBack: the returned events should not be older than this number of days. If None, the value set
                in the topic page is used
        """
        if not (page >= 1):
            raise ValueError("page should be at least 1")
        if not (count <= 50):
            raise ValueError("count should be at most 50")
        params = {
            "action": "getEventsForTopicPage",
            "resultType": "events",
            "eventsCount": count,
            "eventsPage": page,
            "eventsSortBy": sortBy,
            "eventsSortByAsc": sortByAsc
        }
        params.update(self._getContentParams(uri, onlyAfterTm, maxDaysBack))
        params.update((returnInfo if returnInfo is not None else ReturnInfo()).getParams("events"))
        params.update(kwargs)
        return self.eventRegistry.jsonRequest("/api/v1/event", params)
