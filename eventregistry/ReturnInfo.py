"""
the classes here represent all the types of information that can be returned
from Event Registry requests

the ReturnInfo class specifies all types of these parameters and is needed as
a parameter in all query requests
"""

class ReturnInfoFlagsBase(object):
    """
    base class for the return info types
    """

    def _setFlag(self, name, val, defVal):
        """set the objects property propName if the dictKey key exists in dict and it is not the same as default value defVal"""
        if not hasattr(self, "flags"):
            self.flags = {}
        if val != defVal:
            self.flags[name] = val

    def _getFlags(self, prefix):
        """return the dict of stored flags, where each flag name should be first prefixed using prefix"""
        if not hasattr(self, "flags"):
            self.flags = {}
        dict = {}
        for key in list(self.flags.keys()):
            dict[prefix + key] = self.flags[key]
        return dict

    def _setVal(self, name, val):
        """set value of name to val"""
        if not hasattr(self, "vals"):
            self.vals = {}
        self.vals[name] = val

    def _setVal(self, name, val, defVal):
        """set value of name to val in case the val != defVal"""
        if val == defVal:
            return
        if not hasattr(self, "vals"):
            self.vals = {}
        self.vals[name] = val

    def _getVals(self, prefix):
        """
        return the values in the vals dict
        in case prefix is "", change the first letter of the name to lowercase, otherwise use prefix+name as the new name
        """
        if not hasattr(self, "vals"):
            self.vals = {}
        dict = {}
        for key in list(self.vals.keys()):
            # if no prefix then lower the first letter
            if prefix == "":
                newkey = key[:1].lower() + key[1:] if key else ""
                dict[newkey] = self.vals[key]
            else:
                dict[prefix + key] = self.vals[key]
        return dict


class ArticleInfoFlags(ReturnInfoFlagsBase):
    """"
    What information about an article should be returned by the API call

    @param bodyLen: max length of the article body (use -1 for full body, 0 for empty)
    @param basicInfo: core article information -
    @param title: article title
    @param body: article body
    @param url: article url
    @param eventUri: uri of the event to which the article belongs
    @param concepts: the list of concepts mentioned in the article
    @param storyUri: uri of the story (cluster) to which the article belongs
    @param duplicateList: the list of articles that are a copy of this article
    @param originalArticle: if the article is a duplicate, this will provide information about the original article
    @param categories: the list of categories assigned to the article
    @param location: the geographic location that the event mentioned in the article is about
    @param image: url to the image associated with the article
    @param dates: the dates when the articles was crawled and the date when it was published (based on the rss feed date)
    @param extractedDates: the list of dates found mentioned in the article
    @param socialScore: information about the number of times the article was shared on facebook and twitter
    @param details: potential additional details
    """
    def __init__(self,
                 bodyLen = 300,
                 basicInfo = True,
                 title = True,
                 body = True,
                 url = True,
                 eventUri = True,
                 concepts = False,
                 storyUri = False,
                 duplicateList = False,
                 originalArticle = False,
                 categories = False,
                 location = False,
                 image = False,
                 dates = False,
                 extractedDates = False,
                 socialScore = False,
                 details = False):
        self._setVal("ArticleBodyLen", bodyLen, 300)
        self._setFlag("IncludeArticleBasicInfo", basicInfo, True)
        self._setFlag("IncludeArticleTitle", title, True)
        self._setFlag("IncludeArticleBody", body, True)
        self._setFlag("IncludeArticleUrl", url, True)
        self._setFlag("IncludeArticleEventUri", eventUri, True)
        self._setFlag("IncludeArticleConcepts", concepts, False)
        self._setFlag("IncludeArticleStoryUri", storyUri, False)
        self._setFlag("IncludeArticleDuplicateList", duplicateList, False)
        self._setFlag("IncludeArticleOriginalArticle", originalArticle, False)
        self._setFlag("IncludeArticleCategories", categories, False)
        self._setFlag("IncludeArticleLocation", location, False)
        self._setFlag("IncludeArticleImage", image, False)
        self._setFlag("IncludeArticleDates", dates, False)
        self._setFlag("IncludeArticleExtractedDates", extractedDates, False)
        self._setFlag("IncludeArticleSocialScore", socialScore, False)
        self._setFlag("IncludeArticleDetails", details, False)


class StoryInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a story (cluster of articles) should be returned by the API call

    @param basicStats: core stats about the story
    @param location: geographic location that the story is about
    @param categories: categories associated with the story
    @param title: title of the story
    @param summary: summary of the story
    @param medoidArticle: the article that is closest to the center of the cluster of articles assigned to the story
    @param commonDates: dates that were frequently identified in the articles belonging to the story
    @param socialScore: score computed based on how frequently the articles in the story were shared on social media
    @param imageCount: number of images to be returned for a story
    @param flags: various binary flags related to the story
    """
    def __init__(self,
                 basicStats = True,
                 location = True,
                 categories = False,
                 date = False,
                 concepts = False,
                 title = False,
                 summary = False,
                 medoidArticle = False,
                 commonDates = False,
                 socialScore = False,
                 details = False,
                 flags = False,
                 imageCount = 0):
        self._setFlag("IncludeStoryBasicStats", basicStats, True)
        self._setFlag("IncludeStoryLocation", location, True)

        self._setFlag("IncludeStoryCategories", categories, False)
        self._setFlag("IncludeStoryDate", date, False)
        self._setFlag("IncludeStoryConcepts", concepts, False)
        self._setFlag("IncludeStoryTitle", title, False)
        self._setFlag("IncludeStorySummary", summary, False)
        self._setFlag("IncludeStoryMedoidArticle", medoidArticle, False)
        self._setFlag("IncludeStoryCommonDates", commonDates, False)
        self._setFlag("IncludeStorySocialScore", socialScore, False)
        self._setFlag("IncludeStoryDetails", details, False)
        self._setVal("StoryImageCount", imageCount, 0)


class EventInfoFlags(ReturnInfoFlagsBase):
    """
    What information about an event should be returned by the API call

    @param title: return the title of the event
    @param summary: return the summary of the event
    @param articleCounts: return the number of articles that are assigned to the event
    @param concepts: return information about the main concepts related to the event
    @param categories: return information about the categories related to the event
    @param location: return the location where the event occured
    @param date: return information about the date of the event
    @param commonDates: return the dates that were commonly found in the articles about the event
    @param stories: return the list of stories (clusters) that are about the event
    @param socialScore: score computed based on how frequently the articles in the event were shared on social media
    @param imageCount: number of images to be returned for an event
    @param flags: various binary flags related to the event
    """
    def __init__(self,
                 title = True,
                 summary = True,
                 articleCounts = True,
                 concepts = True,
                 categories = True,
                 location = True,
                 date = True,
                 commonDates = False,
                 stories = False,
                 socialScore = False,
                 details = False,
                 flags = False,
                 imageCount = 0):
        self._setFlag("IncludeEventTitle", title, True)
        self._setFlag("IncludeEventSummary", summary, True)
        self._setFlag("IncludeEventArticleCounts", articleCounts, True)
        self._setFlag("IncludeEventConcepts", concepts, True)
        self._setFlag("IncludeEventCategories", categories, True)
        self._setFlag("IncludeEventLocation", location, True)
        self._setFlag("IncludeEventDate", date, True)

        self._setFlag("IncludeEventCommonDates", commonDates, False)
        self._setFlag("IncludeEventStories", stories, False)
        self._setFlag("IncludeEventSocialScore", socialScore, False)
        self._setFlag("IncludeEventDetails", details, False)
        self._setVal("EventImageCount", imageCount, 0)


class SourceInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a news source should be returned by the API call

    @param title: title of the news source
    @param description: description of the news source
    @param location: geographic location of the news source
    @param importance: a score of importance assigned to the news source
    @param articleCount: the number of articles from this news source that are stored in Event Registry
    @param tags: custom tags assigned to the news source
    @param flags: various binary flags related to the news source
    """
    def __init__(self,
                 title = True,
                 description = False,
                 location = False,
                 importance = False,
                 articleCount = False,
                 tags = False,
                 details = False,
                 flags = False):
        self._setFlag("IncludeSourceTitle", title, True)

        self._setFlag("IncludeSourceDescription", description, False)
        self._setFlag("IncludeSourceLocation", location, False)
        self._setFlag("IncludeSourceImportance", importance, False)
        self._setFlag("IncludeSourceArticleCount", articleCount, False)
        self._setFlag("IncludeSourceTags", tags, False)
        self._setFlag("IncludeSourceDetails", details, False)


class CategoryInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a category should be returned by the API call

    @param parentUri: uri of the parent category
    @param childrenUris: the list of category uris that are children of the category
    @param trendingScore: information about how the category is currently trending. The score is computed as Pearson residual by comparing the trending of the category in last 2 days compared to last 14 days
    @param trendingHistory: information about the number of times articles were assigned to the category in last 30 days
    @param trendingSource: source of information to be used when computing the trending score for a category. Relevant only if CategoryInfoFlags.trendingScore == True or CategoryInfoFlags.trendingHistory == True. Valid options: news, social
    @param flags: various binary flags related to the category
    @type trendingSource: string | list
    """
    def __init__(self,
                 parentUri = False,
                 childrenUris = False,
                 trendingScore = False,
                 trendingHistory = False,
                 details = False,
                 trendingSource = "news",
                 flags = False):
        self._setFlag("IncludeCategoryParentUri", parentUri, False)
        self._setFlag("IncludeCategoryChildrenUris", childrenUris, False)
        self._setFlag("IncludeCategoryTrendingScore", trendingScore, False)
        self._setFlag("IncludeCategoryTrendingHistory", trendingHistory, False)
        self._setFlag("IncludeCategoryDetails", details, False)
        self._setVal("CategoryTrendingSource", trendingSource, None)


class ConceptInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept should be returned by the API call

    @param type: which types of concepts should be provided in events, stories, ... Options: person, loc, org, wiki (non-entities), concepts (=person+loc+org+wiki), conceptClass, conceptFolder
    @param lang: in which languages should be the labels for provided concepts
    @param label: return label(s) of the concept
    @param synonyms: return concept synonyms (if any)
    @param image: provide an image associated with the concept
    @param description: description of the concept
    @param conceptClassMembership: provide a list of concept classes where the concept is a member
    @param conceptClassMembership: provide a list of concept classes and their parents where the concept is a member
    @param conceptFolderMembership: provide a list of publicly visible concept folders where the concept is a member
    @param trendingScore: information about how the concept is currently trending. The score is computed as Pearson residual by comparing the trending of the concept in last 2 days compared to last 14 days
    @param trendingHistory: information about the number of times articles were assigned to the concept in last 30 days
    @param totalCount: the total number of times the concept appeared in the news articles
    @param trendingSource: source of information to be used when computing the trending score for a concept. Relevant only if ConceptInfoFlags.trendingScore == True or ConceptInfoFlags.trendingHistory == True. Valid options: news, social
    @param flags: various binary flags related to the concept
    @type conceptType: str | list
    @type conceptLang: str | list
    @type trendingSource: string | list
    """
    def __init__(self,
                 type = "concepts",
                 lang = "eng",
                 label = True,
                 synonyms = False,
                 image = False,
                 description = False,
                 details = False,
                 conceptClassMembership = False,
                 conceptClassMembershipFull = False,
                 conceptFolderMembership = False,
                 trendingScore = False,
                 trendingHistory = False,
                 trendingSource = "news",
                 totalCount = False,
                 maxConceptsPerType = 20,
                 flags = False):
        self._setVal("ConceptType", type, "concepts")
        self._setVal("ConceptLang", lang, "eng")
        self._setFlag("IncludeConceptLabel", label, True)
        self._setFlag("IncludeConceptSynonyms", synonyms, False)
        self._setFlag("IncludeConceptImage", image, False)
        self._setFlag("IncludeConceptDescription", description, False)
        self._setFlag("IncludeConceptDetails", details, False)
        self._setFlag("IncludeConceptConceptClassMembership", conceptClassMembership, False)
        self._setFlag("IncludeConceptConceptClassMembershipFull", conceptClassMembershipFull, False)
        self._setFlag("IncludeConceptConceptFolderMembership", conceptFolderMembership, False)
        self._setFlag("IncludeConceptTrendingScore", trendingScore, False)
        self._setFlag("IncludeConceptTrendingHistory", trendingHistory, False)
        self._setFlag("IncludeConceptTotalCount", totalCount, False)
        self._setVal("ConceptTrendingSource", trendingSource, None)
        self._setVal("MaxConceptsPerType", maxConceptsPerType, 20)


class LocationInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a geographic location should be returned by the API call
    Locations are sub-types of concepts so this information is always provided as a "location" property in concept information
    country* flags are taken into account when the locations represent countries. Similarly place* flags are relevant when the location is a place (city, area, ...)
    @param label: return label of the place/country
    @param wikiUri: return wiki url of the place/country
    @param geoNamesId: return geonames id for the place/country
    @param population: return the population of the place/country
    @param geoLocation: return geographic coordinates of the place/country

    @param countryArea: return geographic area of the country
    @param countryContinent: return continent where the country is located

    @param placeFeatureCode: return the geonames feature code of the place
    @param placeCountry: return information about the country where the place is located
    """
    def __init__(self,
                 label = True,
                 wikiUri = False,
                 geoNamesId = False,
                 population = False,
                 geoLocation = False,

                 countryArea = False,
                 countryDetails = False,
                 countryContinent = False,

                 placeFeatureCode = False,
                 placeCountry = True):
        self._setFlag("IncludeLocationLabel", label, True)
        self._setFlag("IncludeLocationWikiUri", wikiUri, False)
        self._setFlag("IncludeLocationGeoNamesId", geoNamesId, False)
        self._setFlag("IncludeLocationPopulation", population, False)
        self._setFlag("IncludeLocationGeoLocation", geoLocation, False)

        self._setFlag("IncludeLocationCountryArea", countryArea, False)
        self._setFlag("IncludeLocationCountryDetails", countryDetails, False)
        self._setFlag("IncludeLocationCountryContinent", countryContinent, False)

        self._setFlag("IncludeLocationPlaceFeatureCode", placeFeatureCode, False)
        self._setFlag("IncludeLocationPlaceCountry", placeCountry, True)


class ConceptClassInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept class should be returned by the API call

    @param parentLabels: return the list of labels of the parent concept classes
    @param concepts: return the list of concepts assigned to the concept class
    @param details: return additional details about the concept class
    @param flags: various binary flags related to the concept class
    """
    def __init__(self,
                 parentLabels = True,
                 concepts = False,
                 details = False,
                 flags = False):
        self._setFlag("IncludeConceptClassParentLabels", parentLabels, True)
        self._setFlag("IncludeConceptClassConcepts", concepts, False)
        self._setFlag("IncludeConceptClassDetails", details, False)


class ConceptFolderInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept folder should be returned by the API call

    @param definition: return the complete definition of the concept folder
    @param owner: return information about the owner of the concept folder
    @param details: return additional details about the concept folder
    @param flags: various binary flags related to the concept folder
    """
    def __init__(self,
                 definition = False,
                 owner = False,
                 details = False,
                 flags = False):
        self._setFlag("IncludeConceptFolderDefinition", definition, False)
        self._setFlag("IncludeConceptFolderOwner", owner, False)
        self._setFlag("IncludeConceptFolderDetails", details, False)



class ReturnInfo:
    """
    ReturnInfo specifies what content should be returned for each possible returned object type

    @param articleInfo: what details about the articles should be returned
    @param eventInfo: what details about the event should be returned
    @param sourceInfo: what details about the article's news source should be returned
    @param storyInfo: what details about the stories (clusters) should be returned
    @param categoryInfo: what details about the categories should be returned
    @param conceptInfo: what details about the concepts should be returned
    @param locationInfo: what details about the locations should be returned (locations are sub-types of concepts so their information will be a property inside the concept information)
    @param conceptClassInfo: what details about the concept classes should be returned (concept classes are sub-types of concepts so their information will be a property inside the concept information)
    @param conceptFolderInfo: what details about the concept folders should be returned (concept folders are sub-types of concepts so their information will be a property inside the concept information)

    @type articleInfo: ArticleInfoFlags
    @type eventInfo: EventInfoFlags
    @type sourceInfo: SourceInfoFlags
    @type storyInfo: StoryInfoFlags
    @type categoryInfo: CategoryInfoFlags
    @type conceptInfo: ConceptInfoFlags
    @type locationInfo: LocationInfoFlags
    @type conceptClassInfo: ConceptClassInfoFlags
    @type conceptFolderInfo: ConceptFolderInfoFlags
    """
    def __init__(self,
                 articleInfo = ArticleInfoFlags(),
                 eventInfo = EventInfoFlags(),
                 sourceInfo = SourceInfoFlags(),
                 categoryInfo = CategoryInfoFlags(),
                 conceptInfo = ConceptInfoFlags(),
                 locationInfo = LocationInfoFlags(),
                 storyInfo = StoryInfoFlags(),
                 conceptClassInfo = ConceptClassInfoFlags(),
                 conceptFolderInfo = ConceptFolderInfoFlags()):
        assert isinstance(articleInfo, ArticleInfoFlags)
        assert isinstance(eventInfo, EventInfoFlags)
        assert isinstance(sourceInfo, SourceInfoFlags)
        assert isinstance(categoryInfo, CategoryInfoFlags)
        assert isinstance(conceptInfo, ConceptInfoFlags)
        assert isinstance(locationInfo, LocationInfoFlags)
        assert isinstance(storyInfo, StoryInfoFlags)
        assert isinstance(conceptClassInfo, ConceptClassInfoFlags)
        assert isinstance(conceptFolderInfo, ConceptFolderInfoFlags)
        self.articleInfo = articleInfo
        self.eventInfo = eventInfo
        self.sourceInfo = sourceInfo
        self.categoryInfo = categoryInfo
        self.conceptInfo = conceptInfo
        self.locationInfo = locationInfo
        self.storyInfo = storyInfo
        self.conceptClassInfo = conceptClassInfo
        self.conceptFolderInfo = conceptFolderInfo

    def getParams(self, prefix = ""):
        dict = {}
        dict.update(self.articleInfo._getFlags(prefix == "" and "article" or prefix))
        dict.update(self.eventInfo._getFlags(prefix == "" and "event" or prefix))
        dict.update(self.sourceInfo._getFlags(prefix == "" and "source" or prefix))
        dict.update(self.conceptInfo._getFlags(prefix == "" and "concept" or prefix))
        dict.update(self.categoryInfo._getFlags(prefix == "" and "category" or prefix))
        dict.update(self.locationInfo._getFlags(prefix == "" and "location" or prefix))
        dict.update(self.storyInfo._getFlags(prefix == "" and "story" or prefix))
        dict.update(self.conceptClassInfo._getFlags(prefix == "" and "conceptClass" or prefix))
        dict.update(self.conceptFolderInfo._getFlags(prefix == "" and "conceptFolder" or prefix))
        dict.update(self.articleInfo._getVals(prefix))
        dict.update(self.eventInfo._getVals(prefix))
        dict.update(self.sourceInfo._getVals(prefix))
        dict.update(self.conceptInfo._getVals(prefix))
        dict.update(self.categoryInfo._getVals(prefix))
        dict.update(self.locationInfo._getVals(prefix))
        dict.update(self.storyInfo._getVals(prefix))
        dict.update(self.conceptClassInfo._getVals(prefix))
        dict.update(self.conceptFolderInfo._getVals(prefix))
        return dict

