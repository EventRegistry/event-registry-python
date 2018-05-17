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


    def _getFlags(self):
        """return the dict of stored flags"""
        if not hasattr(self, "flags"):
            self.flags = {}
        return self.flags


    def _setVal(self, name, val, defVal = None):
        """set value of name to val in case the val != defVal"""
        if val == defVal:
            return
        if not hasattr(self, "vals"):
            self.vals = {}
        self.vals[name] = val


    def _getVals(self, prefix = ""):
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
                newkey = key[:1].upper() + key[1:] if key else ""
                dict[prefix + newkey] = self.vals[key]
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
    @param categories: the list of categories assigned to the article
    @param links: the list of urls of links identified in the article body
    @param videos: the list of videos assigned to the article
    @param image: url to the image associated with the article
    @param socialScore: information about the number of times the article was shared on facebook and linkedin, instagram, ...
    @param sentiment: sentiment about the article
    @param location: the geographic location that the event mentioned in the article is about
    @param dates: the dates when the articles was crawled and the date when it was published (based on the rss feed date)
    @param extractedDates: the list of dates found mentioned in the article
    @param duplicateList: the list of articles that are a copy of this article
    @param originalArticle: if the article is a duplicate, this will provide information about the original article
    @param storyUri: uri of the story (cluster) to which the article belongs
    """
    def __init__(self,
                 bodyLen = -1,
                 basicInfo = True,
                 title = True,
                 body = True,
                 url = True,
                 eventUri = True,
                 concepts = False,
                 categories = False,
                 links = False,
                 videos = False,
                 image = False,
                 socialScore = False,
                 sentiment = False,
                 location = False,
                 dates = False,
                 extractedDates = False,
                 duplicateList = False,
                 originalArticle = False,
                 storyUri = False):
        self._setVal("articleBodyLen", bodyLen, 300)
        self._setFlag("includeArticleBasicInfo", basicInfo, True)
        self._setFlag("includeArticleTitle", title, True)
        self._setFlag("includeArticleBody", body, True)
        self._setFlag("includeArticleUrl", url, True)
        self._setFlag("includeArticleEventUri", eventUri, True)
        self._setFlag("includeArticleConcepts", concepts, False)
        self._setFlag("includeArticleCategories", categories, False)
        self._setFlag("includeArticleLinks", links, False)
        self._setFlag("includeArticleVideos", videos, False)
        self._setFlag("includeArticleImage", image, False)
        self._setFlag("includeArticleSocialScore", socialScore, False)
        self._setFlag("includeArticleSentiment", sentiment, False)
        self._setFlag("includeArticleLocation", location, False)
        self._setFlag("includeArticleDates", dates, False)
        self._setFlag("includeArticleExtractedDates", extractedDates, False)
        self._setFlag("includeArticleDuplicateList", duplicateList, False)
        self._setFlag("includeArticleOriginalArticle", originalArticle, False)
        self._setFlag("includeArticleStoryUri", storyUri, False)



class StoryInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a story (cluster of articles) should be returned by the API call

    @param basicStats: core stats about the story
    @param location: geographic location that the story is about
    @param date: date of the story
    @param title: title of the story
    @param summary: summary of the story
    @param concepts: set of concepts associated with the story
    @param categories: categories associated with the story
    @param medoidArticle: the article that is closest to the center of the cluster of articles assigned to the story
    @param infoArticle: the article from which we have extracted the title and summary for the story
    @param commonDates: dates that were frequently identified in the articles belonging to the story
    @param socialScore: score computed based on how frequently the articles in the story were shared on social media
    @param imageCount: number of images to be returned for a story
    """
    def __init__(self,
                basicStats = True,
                location = True,
                date = False,
                title = False,
                summary = False,
                concepts = False,
                categories = False,
                medoidArticle = False,
                infoArticle = False,
                commonDates = False,
                socialScore = False,
                imageCount = 0):
        self._setFlag("includeStoryBasicStats", basicStats, True)
        self._setFlag("includeStoryLocation", location, True)
        self._setFlag("includeStoryDate", date, False)
        self._setFlag("includeStoryTitle", title, False)
        self._setFlag("includeStorySummary", summary, False)
        self._setFlag("includeStoryConcepts", concepts, False)
        self._setFlag("includeStoryCategories", categories, False)
        self._setFlag("includeStoryMedoidArticle", medoidArticle, False)
        self._setFlag("includeStoryInfoArticle", infoArticle, False)
        self._setFlag("includeStoryCommonDates", commonDates, False)
        self._setFlag("includeStorySocialScore", socialScore, False)
        self._setVal("storyImageCount", imageCount, 0)



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
    @param infoArticle: return for each language the article from which we have extracted the summary and title for event for that language
    @param stories: return the list of stories (clusters) that are about the event
    @param socialScore: score computed based on how frequently the articles in the event were shared on social media
    @param imageCount: number of images to be returned for an event
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
                infoArticle = False,
                stories = False,
                socialScore = False,
                imageCount = 0):
        self._setFlag("includeEventTitle", title, True)
        self._setFlag("includeEventSummary", summary, True)
        self._setFlag("includeEventArticleCounts", articleCounts, True)
        self._setFlag("includeEventConcepts", concepts, True)
        self._setFlag("includeEventCategories", categories, True)
        self._setFlag("includeEventLocation", location, True)
        self._setFlag("includeEventDate", date, True)

        self._setFlag("includeEventCommonDates", commonDates, False)
        self._setFlag("includeEventInfoArticle", infoArticle, False)
        self._setFlag("includeEventStories", stories, False)
        self._setFlag("includeEventSocialScore", socialScore, False)
        self._setVal("eventImageCount", imageCount, 0)



class SourceInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a news source should be returned by the API call

    @param title: title of the news source
    @param description: description of the news source
    @param location: geographic location of the news source
    @param ranking: a set of rankings for the news source
    @param image: different images associated with the news source
    @param articleCount: the number of articles from this news source that are stored in Event Registry
    @param socialMedia: different social media accounts used by the news source
    @param sourceGroups: info about the names of the source groups to which the source belongs to
    """
    def __init__(self,
                title = True,
                description = False,
                location = False,
                ranking = False,
                image = False,
                articleCount = False,
                socialMedia = False,
                sourceGroups = False):
        self._setFlag("includeSourceTitle", title, True)
        self._setFlag("includeSourceDescription", description, False)
        self._setFlag("includeSourceLocation", location, False)
        self._setFlag("includeSourceRanking", ranking, False)
        self._setFlag("includeSourceImage", image, False)
        self._setFlag("includeSourceArticleCount", articleCount, False)
        self._setFlag("includeSourceSocialMedia", socialMedia, False)
        self._setFlag("includeSourceSourceGroups", sourceGroups, False)



class CategoryInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a category should be returned by the API call

    @param parentUri: uri of the parent category
    @param childrenUris: the list of category uris that are children of the category
    @param trendingScore: information about how the category is currently trending. The score is computed as Pearson residual by comparing the trending of the category in last 2 days compared to last 14 days
    @param trendingHistory: information about the number of times articles were assigned to the category in last 30 days
    @param trendingSource: source of information to be used when computing the trending score for a category. Relevant only if CategoryInfoFlags.trendingScore == True or CategoryInfoFlags.trendingHistory == True. Valid options: news, social
    @type trendingSource: string | list
    """
    def __init__(self,
                parentUri = False,
                childrenUris = False,
                trendingScore = False,
                trendingHistory = False,
                trendingSource = "news"):
        self._setFlag("includeCategoryParentUri", parentUri, False)
        self._setFlag("includeCategoryChildrenUris", childrenUris, False)
        self._setFlag("includeCategoryTrendingScore", trendingScore, False)
        self._setFlag("includeCategoryTrendingHistory", trendingHistory, False)
        self._setVal("categoryTrendingSource", trendingSource, "news")



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
    @param conceptClassMembershipFull: provide a list of concept classes and their parents where the concept is a member
    @param trendingScore: information about how the concept is currently trending. The score is computed as Pearson residual by comparing the trending of the concept in last 2 days compared to last 14 days
    @param trendingHistory: information about the number of times articles were assigned to the concept in last 30 days
    @param trendingSource: source of information to be used when computing the trending score for a concept. Relevant only if ConceptInfoFlags.trendingScore == True or ConceptInfoFlags.trendingHistory == True. Valid options: news, social
    @param totalCount: the total number of times the concept appeared in the news articles
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
                 conceptClassMembership = False,
                 conceptClassMembershipFull = False,
                 trendingScore = False,
                 trendingHistory = False,
                 totalCount = False,
                 trendingSource = "news",
                 maxConceptsPerType = 20):
        self._setVal("conceptType", type, "concepts")
        self._setVal("conceptLang", lang, "eng")
        self._setFlag("includeConceptLabel", label, True)
        self._setFlag("includeConceptSynonyms", synonyms, False)
        self._setFlag("includeConceptImage", image, False)
        self._setFlag("includeConceptDescription", description, False)
        self._setFlag("includeConceptConceptClassMembership", conceptClassMembership, False)
        self._setFlag("includeConceptConceptClassMembershipFull", conceptClassMembershipFull, False)
        self._setFlag("includeConceptTrendingScore", trendingScore, False)
        self._setFlag("includeConceptTrendingHistory", trendingHistory, False)
        self._setFlag("includeConceptTotalCount", totalCount, False)
        self._setVal("conceptTrendingSource", trendingSource, "news")
        self._setVal("maxConceptsPerType", maxConceptsPerType, 20)



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
    @param countryDetails: return additional details about the country
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
        self._setFlag("includeLocationLabel", label, True)
        self._setFlag("includeLocationWikiUri", wikiUri, False)
        self._setFlag("includeLocationGeoNamesId", geoNamesId, False)
        self._setFlag("includeLocationPopulation", population, False)
        self._setFlag("includeLocationGeoLocation", geoLocation, False)

        self._setFlag("includeLocationCountryArea", countryArea, False)
        self._setFlag("includeLocationCountryDetails", countryDetails, False)
        self._setFlag("includeLocationCountryContinent", countryContinent, False)

        self._setFlag("includeLocationPlaceFeatureCode", placeFeatureCode, False)
        self._setFlag("includeLocationPlaceCountry", placeCountry, True)



class ConceptClassInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept class should be returned by the API call

    @param parentLabels: return the list of labels of the parent concept classes
    @param concepts: return the list of concepts assigned to the concept class
    """
    def __init__(self,
                parentLabels = True,
                concepts = False):
        self._setFlag("includeConceptClassParentLabels", parentLabels, True)
        self._setFlag("includeConceptClassConcepts", concepts, False)



class ConceptFolderInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept folder should be returned by the API call

    @param definition: return the complete definition of the concept folder
    @param owner: return information about the owner of the concept folder
    """
    def __init__(self,
                 definition = False,
                 owner = False):
        self._setFlag("includeConceptFolderDefinition", definition, False)
        self._setFlag("includeConceptFolderOwner", owner, False)



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
        dict.update(self.articleInfo._getFlags())
        dict.update(self.eventInfo._getFlags())
        dict.update(self.sourceInfo._getFlags())
        dict.update(self.conceptInfo._getFlags())
        dict.update(self.categoryInfo._getFlags())
        dict.update(self.locationInfo._getFlags())
        dict.update(self.storyInfo._getFlags())
        dict.update(self.conceptClassInfo._getFlags())
        dict.update(self.conceptFolderInfo._getFlags())
        dict.update(self.articleInfo._getVals())
        dict.update(self.eventInfo._getVals())
        dict.update(self.sourceInfo._getVals())
        dict.update(self.conceptInfo._getVals())
        dict.update(self.categoryInfo._getVals())
        dict.update(self.locationInfo._getVals())
        dict.update(self.storyInfo._getVals())
        dict.update(self.conceptClassInfo._getVals())
        dict.update(self.conceptFolderInfo._getVals())
        return dict

