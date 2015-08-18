"""
the classes here represent all the types of information that can be returned
from event registry requests

the ReturnInfo class specifies all types of these parameters and is needed as 
a parameter in all query requests
"""

class ReturnInfoFlagsBase(object):
    # set the objects property propName if the dictKey key exists in dict and it is not the same as default value defVal
    def _setVal(self, name, val, defVal):
        if val != defVal:
            self.__dict__[name] = val

    def getParams(self, prefix):
        dict = {}
        for key in self.__dict__.keys():
            dict[prefix + key] = self.__dict__[key]
        return dict

class ArticleInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 basicInfo = True, 
                 title = True,
                 body = True,
                 eventUri = True,
                 concepts = False,
                 storyUri = False,
                 duplicateList = False,
                 originalArticle = False,
                 categories = False,
                 location = False,
                 image = False,
                 extractedDates = False,
                 socialScore = False,
                 details = False):
        self._setVal("IncludeArticleBasicInfo", basicInfo, True)
        self._setVal("IncludeArticleTitle", title, True)
        self._setVal("IncludeArticleBody", body, True)
        self._setVal("IncludeArticleEventUri", eventUri, True)
        self._setVal("IncludeArticleConcepts", concepts, False)
        self._setVal("IncludeArticleStoryUri", storyUri, False)
        self._setVal("IncludeArticleDuplicateList", duplicateList, False)
        self._setVal("IncludeArticleOriginalArticle", originalArticle, False)
        self._setVal("IncludeArticleCategories", categories, False)
        self._setVal("IncludeArticleLocation", location, False)
        self._setVal("IncludeArticleImage", image, False)
        self._setVal("IncludeArticleExtractedDates", extractedDates, False)
        self._setVal("IncludeArticleSocialScore", socialScore, False)
        self._setVal("IncludeArticleDetails", details, False)


class StoryInfoFlags(ReturnInfoFlagsBase):
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
                 images = False):
        self._setVal("IncludeStoryBasicStats", basicStats, True)
        self._setVal("IncludeStoryLocation", location, True)
        
        self._setVal("IncludeStoryCategories", categories, False)
        self._setVal("IncludeStoryDate", date, False)
        self._setVal("IncludeStoryConcepts", concepts, False)
        self._setVal("IncludeStoryTitle", title, False)
        self._setVal("IncludeStorySummary", summary, False)
        self._setVal("IncludeStoryMedoidArticle", medoidArticle, False)
        self._setVal("IncludeStoryCommonDates", commonDates, False)
        self._setVal("IncludeStorySocialScore", socialScore, False)
        self._setVal("IncludeStoryImages", images, False)


class EventInfoFlags(ReturnInfoFlagsBase):
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
                 images = False):
        self._setVal("IncludeEventTitle", title, True)
        self._setVal("IncludeEventSummary", summary, True)
        self._setVal("IncludeEventArticleCounts", articleCounts, True)
        self._setVal("IncludeEventConcepts", concepts, True)
        self._setVal("IncludeEventCategories", categories, True)
        self._setVal("IncludeEventLocation", location, True)
        self._setVal("IncludeEventDate", date, True)

        self._setVal("IncludeEventCommonDates", commonDates, False)
        self._setVal("IncludeEventStories", stories, False)
        self._setVal("IncludeEventSocialScore", socialScore, False)
        self._setVal("IncludeEventImages", images, False)
        

class SourceInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 title = True,
                 description = False,
                 location = False,
                 importance = False,
                 articleCount = False,
                 tags = False,
                 details = False):
        self._setVal("IncludeSourceTitle", title, True)

        self._setVal("IncludeSourceDescription", description, False)
        self._setVal("IncludeSourceLocation", location, False)
        self._setVal("IncludeSourceImportance", importance, False)
        self._setVal("IncludeSourceArticleCount", articleCount, False)
        self._setVal("IncludeSourceTags", tags, False)
        self._setVal("IncludeSourceDetails", details, False)


class CategoryInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 parentUri = False,
                 childrenUris = False,
                 trendingScore = False,
                 trendingHistory = False):
        self._setVal("IncludeCategoryParentUri", parentUri, False)
        self._setVal("IncludeCategoryChildrenUris", childrenUris, False)
        self._setVal("IncludeCategoryTrendingScore", trendingScore, False)
        self._setVal("IncludeCategoryTrendingHistory", trendingHistory, False)


class ConceptInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 label = True,
                 synonyms = False,
                 image = False,
                 description = False,
                 details = False,
                 conceptClassMembership = False,
                 conceptClassMembershipFull = False,
                 conceptFolderMembership = False,
                 trendingScore = False,
                 trendingHistory = False):
        self._setVal("IncludeConceptLabel", label, True)
        
        self._setVal("IncludeConceptSynonyms", synonyms, False)
        self._setVal("IncludeConceptImage", image, False)
        self._setVal("IncludeConceptDescription", description, False)
        self._setVal("IncludeConceptDetails", details, False)
        self._setVal("IncludeConceptConceptClassMembership", conceptClassMembership, False)
        self._setVal("IncludeConceptConceptClassMembershipFull", conceptClassMembershipFull, False)
        self._setVal("IncludeConceptConceptFolderMembership", conceptFolderMembership, False)
        self._setVal("IncludeConceptTrendingScore", trendingScore, False)
        self._setVal("IncludeConceptTrendingHistory", trendingHistory, False)


class LocationInfoFlags(ReturnInfoFlagsBase):
    def __init__(self, 
                 countryLabel = True,
                 countryWikiUri = False,
                 countryGeoNamesId = False,
                 countryArea = False,
                 countryPopulation = False,
                 countryLocation = False,
                 countryDetails = False,
                 countryContinent = False,
                 
                 placeLabel = True,
                 placeWikiUri = False,
                 placeGeoNamesId = False,
                 placePopulation = False,
                 placeFeatureCode = False,
                 placeLocation = False,
                 placeCountry = True):
        self._setVal("IncludeLocationCountryLabel", countryLabel, True)
        self._setVal("IncludeLocationCountryWikiUri", countryWikiUri, False)
        self._setVal("IncludeLocationCountryGeoNamesId", countryGeoNamesId, False)
        self._setVal("IncludeLocationCountryArea", countryArea, False)
        self._setVal("IncludeLocationCountryPopulation", countryPopulation, False)
        self._setVal("IncludeLocationCountryLocation", countryLocation, False)
        self._setVal("IncludeLocationCountryDetails", countryDetails, False)
        self._setVal("IncludeLocationCountryContinent", countryContinent, False)

        self._setVal("IncludeLocationPlaceLabel", placeLabel, True)
        self._setVal("IncludeLocationPlaceWikiUri", placeWikiUri, False)
        self._setVal("IncludeLocationPlaceGeoNamesId", placeGeoNamesId, False)
        self._setVal("IncludeLocationPlacePopulation", placePopulation, False)
        self._setVal("IncludeLocationPlaceFeatureCode", placeFeatureCode, False)
        self._setVal("IncludeLocationPlaceLocation", placeLocation, False)
        self._setVal("IncludeLocationPlaceCountry", placeCountry, True)


class ConceptClassInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 parentLabels = True,
                 concepts = False,
                 details = False):
        self._setVal("IncludeConceptClassParentLabels", parentLabels, True)
        self._setVal("IncludeConceptClassConcepts", concepts, False)
        self._setVal("IncludeConceptClassDetails", details, False)
        

class ConceptFolderInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 definition = False,
                 owner = False,
                 details = False):
        self._setVal("IncludeConceptFolderDefinition", definition, False)
        self._setVal("IncludeConceptFolderOwner", owner, False)
        self._setVal("IncludeConceptFolderDetails", details, False)



class ReturnInfo:
    """
    ReturnInfo specifies what content should be returned for each possible returned object type

    @param articleBodyLen: max length of the article body (use -1 for full body, 0 for empty)
    @param conceptType: which types of concepts should be provided in events, stories, ... Options: person, loc, org, wiki (non-entities), concepts (=person+loc+org+wiki), conceptClass, conceptFolder
    @param conceptLang: in which languages should be the labels for provided concepts
    @param articleInfo: what details about the articles should be returned
    @param eventInfo: what details about the event should be returned
    @param sourceInfo: what details about the article's news source should be returned
    @param storyInfo: what details about the stories (clusters) should be returned
    @param categoryInfo: what details about the categories should be returned
    @param conceptInfo: what details about the concepts should be returned
    @param locationInfo: what details about the locations should be returned (locations are sub-types of concepts so their information will be a property inside the concept information)
    @param conceptClassInfo: what details about the concept classes should be returned (concept classes are sub-types of concepts so their information will be a property inside the concept information)
    @param conceptFolderInfo: what details about the concept folders should be returned (concept folders are sub-types of concepts so their information will be a property inside the concept information)
    @param storyImageCount: number of images to be returned for each story (cluster). Relevant only if StoryInfoFlags.image == True
    @param eventImageCount: number of images to be returned for each event. Relevant only if EventInfoFlags.image == True
    @param conceptTrendingSource: source of information to be used when computing the trending score for a concept. Relevant only if ConceptInfoFlags.trendingScore == True or ConceptInfoFlags.trendingHistory == True. Valid options: news, social
    @param categoryTrendingSource: source of information to be used when computing the trending score for a category. Relevant only if CategoryInfoFlags.trendingScore == True or CategoryInfoFlags.trendingHistory == True. Valid options: news, social
    @type articleBodyLen: int
    @type conceptType: str | list
    @type conceptLang: str | list
    @type articleInfo: ArticleInfoFlags
    @type eventInfo: EventInfoFlags
    @type sourceInfo: SourceInfoFlags
    @type storyInfo: StoryInfoFlags
    @type categoryInfo: CategoryInfoFlags
    @type conceptInfo: ConceptInfoFlags
    @type locationInfo: LocationInfoFlags
    @type conceptClassInfo: ConceptClassInfoFlags
    @type conceptFolderInfo: ConceptFolderInfoFlags
    @type storyImageCount: int
    @type eventImageCount: int
    @type conceptTrendingSource: string | list
    @type categoryTrendingSource: string | list
    """
    def __init__(self,
                 articleBodyLen = 300,
                 conceptType = ["concepts"],
                 conceptLang = ["eng"],
                 articleInfo = ArticleInfoFlags(),
                 eventInfo = EventInfoFlags(),
                 sourceInfo = SourceInfoFlags(),
                 storyInfo = StoryInfoFlags(),
                 categoryInfo = CategoryInfoFlags(),
                 conceptInfo = ConceptInfoFlags(),
                 locationInfo = LocationInfoFlags(),
                 conceptClassInfo = ConceptInfoFlags(),
                 conceptFolderInfo = ConceptFolderInfoFlags(),
                 storyImageCount = 1,
                 eventImageCount = 1,
                 conceptTrendingSource = "news",
                 categoryTrendingSource = "news"):
        self.articleBodyLen = articleBodyLen
        self.conceptType = conceptType
        self.conceptLang = conceptLang
        self.articleInfo = articleInfo
        self.storyInfo = storyInfo
        self.eventInfo = eventInfo
        self.sourceInfo = sourceInfo
        self.categoryInfo = categoryInfo
        self.conceptInfo = conceptInfo
        self.locationInfo = locationInfo
        self.conceptClassInfo = conceptClassInfo
        self.conceptFolderInfo = conceptFolderInfo
        self.storyImageCount = storyImageCount
        self.eventImageCount = eventImageCount
        self.conceptTrendingSource = conceptTrendingSource
        self.categoryTrendingSource = categoryTrendingSource

    def getParams(self, prefix = ""):
        dict = {}
        dict[prefix == "" and "articleBodyLen" or prefix + "BodyLen"] = self.articleBodyLen
        dict[prefix == "" and "conceptType" or prefix + "ConceptType"] = self.conceptType
        dict[prefix == "" and "conceptLang" or prefix + "ConceptLang"] = self.conceptLang
        dict.update(self.articleInfo.getParams(prefix == "" and "article" or prefix))
        dict.update(self.storyInfo.getParams(prefix == "" and "story" or prefix))
        dict.update(self.eventInfo.getParams(prefix == "" and "event" or prefix))
        dict.update(self.sourceInfo.getParams(prefix == "" and "source" or prefix))
        dict.update(self.categoryInfo.getParams(prefix == "" and "category" or prefix))
        dict.update(self.conceptInfo.getParams(prefix == "" and "concept" or prefix))
        dict.update(self.locationInfo.getParams(prefix == "" and "location" or prefix))
        dict.update(self.conceptClassInfo.getParams(prefix == "" and "conceptClass" or prefix))
        dict.update(self.conceptFolderInfo.getParams(prefix == "" and "conceptFolder" or prefix))
        dict[prefix == "" and "storyImageCount" or prefix + "StoryImageCount"] = self.storyImageCount
        dict[prefix == "" and "eventImageCount" or prefix + "EventImageCount"] = self.eventImageCount
        dict[prefix == "" and "conceptTrendingSource" or prefix + "ConceptTrendingSource"] = self.conceptTrendingSource
        dict[prefix == "" and "categoryTrendingSource" or prefix + "CategoryTrendingSource"] = self.categoryTrendingSource
        return dict

