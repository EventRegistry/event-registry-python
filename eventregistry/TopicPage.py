"""
class that provides the ability to use topic pages (monitoring functionality)
through the API
"""

import six, json
from eventregistry.Base import *
from eventregistry.ReturnInfo import *
from eventregistry.EventRegistry import EventRegistry
from typing import Union, List


class TopicPages(QueryParamsBase):
    """
    get the list of user owned topic pages
    """
    def __init__(self, eventRegistry: EventRegistry):
        """
        create an instance of a topic page

        @param eventRegistry: instance of class EventRegistry
        """
        super(QueryParamsBase, self).__init__()
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

        @param eventRegistry: instance of class EventRegistry
        """
        super(QueryParamsBase, self).__init__()
        self.eventRegistry = eventRegistry
        # topic page definition
        self.topicPage = self._createEmptyTopicPage()
        self.concept = {}


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
        @param uri: uri of the topic page saved in your Event Registry account
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
        assert isinstance(definitionDict, dict)
        self.topicPage = definitionDict


    def loadTopicPageFromFile(self, fname: str):
        """
        load topic page from an existing file
        """
        assert os.path.exists(fname)
        f = open(fname, "r", encoding="utf-8")
        self.topicPage = json.load(f)


    def saveTopicPageDefinition(self):
        """
        return a python dict containing the topic page definition. you can use it to load a topic page later
        """
        return self.topicPage


    def saveTopicPageDefinitionToFile(self, fname: str):
        """
        save the topic page definition to a file
        """
        open(fname, "w", encoding="utf-8").write(json.dumps(self.topicPage, indent = 4, sort_keys = True))

    #
    # methods for adding filters to the topic
    #

    def setArticleThreshold(self, value: int):
        """
        what is the minimum total weight that an article has to have in order to get it among the results?
        @param value: threshold to use
        """
        assert isinstance(value, int)
        assert value >= 0
        self.topicPage["articleTreshWgt"] = value


    def setEventThreshold(self, value: int):
        """
        what is the minimum total weight that an event has to have in order to get it among the results?
        @param value: threshold to use
        """
        assert isinstance(value, int)
        assert value >= 0
        self.topicPage["eventTreshWgt"] = value


    def setArticleIsDuplicateFilter(self, value: str):
        """
        @param value: some articles can be duplicates of other articles. What should be done with them. Possible values are:
            "skipDuplicates" (skip the resulting articles that are duplicates of other articles)
            "keepOnlyDuplicates" (return only the duplicate articles)
            "keepAll" (no filtering, default)
        """
        assert value == "skipDuplicates" or value == "keepOnlyDuplicates" or value == "keepAll"
        self.topicPage["isDuplicateFilter"] = value


    def setArticleHasEventFilter(self, value: str):
        """
        @param value: some articles describe a known event and some don't. This filter allows you to filter the resulting articles based on this criteria.
            Possible values are:
            "skipArticlesWithoutEvent" (skip articles that are not describing any known event in ER)
            "keepOnlyArticlesWithoutEvent" (return only the articles that are not describing any known event in ER)
            "keepAll" (no filtering, default)
        """
        assert value == "skipArticlesWithoutEvent" or value == "keepOnlyArticlesWithoutEvent" or value == "keepAll"
        self.topicPage["articleHasEvent"] = value


    def setArticleHasDuplicateFilter(self, value: str):
        """
        @param value: some articles are later copied by others. What should be done with such articles. Possible values are:
            "skipHasDuplicates" (skip the articles that have been later copied by others)
            "keepOnlyHasDuplicates" (return only the articles that have been later copied by others)
            "keepAll" (no filtering, default)
        """
        assert value == "skipHasDuplicates" or value == "keepOnlyHasDuplicates" or value == "keepAll"
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
        assert isinstance(maxDaysBack, int), "maxDaysBack value has to be a positive integer"
        assert maxDaysBack >= 1
        self.topicPage["maxDaysBack"] = maxDaysBack


    def setSourceRankPercentile(self, startPercentile: int = 0, endPercentile: int = 100):
        assert startPercentile >= 0 and startPercentile <= 90, "startPercentile is out of valid values (0 - 90)"
        assert endPercentile >= 10 and endPercentile <= 100, "endPercentile is out of valid values (10 - 100)"
        assert startPercentile < endPercentile, "startPercentile has to be smaller than endPercentile"
        assert startPercentile % 10 == 0, "startPecentile has to be a multiple of 10"
        assert endPercentile % 10 == 0, "endPercentile has to be a multiple of 10"
        self.topicPage["startSourceRankPercentile"] = startPercentile
        self.topicPage["endSourceRankPercentile"] = endPercentile


    def setSentiment(self, minSentiment: float = -1, maxSentiment: float = 1):
        """
        what should be the sentiment of the returned articles and events?
        """
        assert minSentiment >= -1, "minSentiment has to be >= -1"
        assert maxSentiment <= 1, "maxSentiment has to be <= 1"
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
        @param conceptUri: uri of the concept to be added
        @param weight: importance of the provided concept (typically in range 1 - 50)
        @param required: if true, then all results will HAVE TO be annotated with this concept
        @param excluded: if true, then all results annotated with this concept will be ignored
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        assert not (required is True and excluded is True), "Parameters required and excluded can not be True at the same time"
        concept = {"uri": conceptUri, "wgt": weight, "required": required, "excluded": excluded }
        if label is not None:
            concept["label"] = label
        if conceptType is not None:
            concept["type"] = conceptType
        self.topicPage["concepts"].append(concept)


    def addKeyword(self, keyword: str, weight: float, required: bool = False, excluded: bool = False):
        """
        add a relevant keyword to the topic page
        @param keyword: keyword or phrase to be added
        @param weight: importance of the provided keyword (typically in range 1 - 50)
        @param required: if true, then all results will HAVE TO mention this keyword to appear in the results
        @param excluded: if true, then no results that mention this keyword will be returned
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        assert not (required is True and excluded is True), "Parameters required and excluded can not be True at the same time"
        self.topicPage["keywords"].append({"keyword": keyword, "wgt": weight, "required": required, "excluded": excluded })


    def addCategory(self, categoryUri: str, weight: float, required: bool = False, excluded: bool = False):
        """
        add a relevant category to the topic page
        @param categoryUri: uri of the category to be added
        @param weight: importance of the provided category (typically in range 1 - 50)
        @param required: if true, then all results will HAVE TO be annotated with this category to appear in the results
        @param excluded: if true, then no results with this category will be returned
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        assert not (required is True and excluded is True), "Parameters required and excluded can not be True at the same time"
        self.topicPage["categories"].append({"uri": categoryUri, "wgt": weight, "required": required, "excluded": excluded })


    def addSource(self, sourceUri: str, weight: float, excluded: bool = False):
        """
        add a news source to the topic page
        @param sourceUri: uri of the news source to add to the topic page
        @param weight: importance of the news source (typically in range 1 - 50)
        @param excluded: if true, then the results from these sources will be ignored
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        self.topicPage["sources"].append({"uri": sourceUri, "wgt": weight, "excluded": excluded })


    def addSourceLocation(self, sourceLocationUri: str, weight: float, excluded: bool = False):
        """
        add a list of relevant sources by identifying them by their geographic location
        @param sourceLocationUri: uri of the location where the sources should be geographically located
        @param weight: importance of the provided list of sources (typically in range 1 - 50)
        @param excluded: if true, then the results from the sources from this location will be ignored
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        self.topicPage["sourceLocations"].append({"uri": sourceLocationUri, "wgt": weight, "excluded": excluded })


    def addSourceGroup(self, sourceGroupUri: str, weight: float, excluded: bool = False):
        """
        add a list of relevant sources by specifying a whole source group to the topic page
        @param sourceGroupUri: uri of the source group to add
        @param weight: importance of the provided list of sources (typically in range 1 - 50)
        @param excluded: if true, then the results from sources from this group will be ignored
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        self.topicPage["sourceGroups"].append({"uri": sourceGroupUri, "wgt": weight, "excluded": excluded })


    def addLocation(self, locationUri: str, weight: float):
        """
        add relevant location to the topic page
        @param locationUri: uri of the location to add
        @param weight: importance of the provided location (typically in range 1 - 50)
        """
        assert isinstance(weight, (float, int)), "weight value has to be a positive or negative integer"
        self.topicPage["locations"].append({"uri": locationUri, "wgt": weight})


    def setLanguages(self, languages: Union[str, List[str]]):
        """
        restrict the results to the list of specified languages
        """
        if isinstance(languages, six.string_types):
            languages = [languages]
        for lang in languages:
            assert len(lang) == 3, "Expected to get language in ISO3 code"
        self.topicPage["langs"] = languages


    def restrictToSetConceptsAndKeywords(self, restrict: bool):
        """
        if true then the results have to mention at least one of the specified concepts or keywords
        """
        assert isinstance(restrict, bool), "restrict value has to be a boolean value"
        self.topicPage["restrictToSetConcepts"] = restrict


    def restrictToSetCategories(self, restrict: bool):
        """
        if set to true then return only results that are assigned to one of the specified categories
        """
        assert isinstance(restrict, bool), "restrict value has to be a boolean value"
        self.topicPage["restrictToSetCategories"] = restrict


    def restrictToSetSources(self, restrict: bool):
        """
        if set to true then return only results from one of the specified news sources
        this includes also sources set by source groups or by source locations
        """
        assert isinstance(restrict, bool), "restrict value has to be a boolean value"
        self.topicPage["restrictToSetSources"] = restrict


    def restrictToSetLocations(self, restrict: bool):
        """
        if set to true, then return only results that are located at one of the specified locations
        """
        assert isinstance(restrict, bool), "restrict value has to be a boolean value"
        self.topicPage["restrictToSetLocations"] = restrict


    #
    # getting content
    #


    def getArticles(self,
                page: int = 1,
                count: int = 100,
                sortBy: str = "rel",
                sortByAsc: bool = False,
                returnInfo: ReturnInfo = ReturnInfo(),
                **kwargs):
        """
        return a list of articles that match the topic page
        @param page: which page of the results to return (default: 1)
        @param count: number of articles to return (default: 100)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1
        assert count <= 100
        params = {
            "action": "getArticlesForTopicPage",
            "resultType": "articles",
            "dataType": self.topicPage["dataType"],
            "articlesCount": count,
            "articlesSortBy": sortBy,
            "articlesSortByAsc": sortByAsc,
            "articlesPage": page,
            "topicPage": json.dumps(self.topicPage)
        }
        params.update(returnInfo.getParams("articles"))
        params.update(kwargs)
        return self.eventRegistry.jsonRequest("/api/v1/article", params)


    def getEvents(self,
                page: int = 1,
                count: int = 50,
                sortBy: str = "rel",
                sortByAsc: bool = False,
                returnInfo: ReturnInfo = ReturnInfo(),
                **kwargs):
        """
        return a list of events that match the topic page
        @param page: which page of the results to return (default: 1)
        @param count: number of articles to return (default: 50)
        @param sortBy: how are articles sorted. Options: id (internal id), date (publishing date), cosSim (closeness to the event centroid), rel (relevance to the query), sourceImportance (manually curated score of source importance - high value, high importance), sourceImportanceRank (reverse of sourceImportance), sourceAlexaGlobalRank (global rank of the news source), sourceAlexaCountryRank (country rank of the news source), socialScore (total shares on social media), facebookShares (shares on Facebook only)
        @param sortByAsc: should the results be sorted in ascending order (True) or descending (False)
        @param returnInfo: what details should be included in the returned information
        """
        assert page >= 1
        assert count <= 50
        params = {
            "action": "getEventsForTopicPage",
            "resultType": "events",
            "dataType": self.topicPage["dataType"],
            "eventsCount": count,
            "eventsPage": page,
            "eventsSortBy": sortBy,
            "eventsSortByAsc": sortByAsc,
            "topicPage": json.dumps(self.topicPage)
        }
        params.update(returnInfo.getParams("events"))
        params.update(kwargs)
        return self.eventRegistry.jsonRequest("/api/v1/event", params)
