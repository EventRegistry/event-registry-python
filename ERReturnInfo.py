"""
the classes here represent all the types of information that can be returned
from event registry requests

the ReturnInfo class specifies all types of these parameters and is needed as 
a parameter in all query requests
"""

class ReturnInfoFlagsBase(object):
    # set the objects property propName if the dictKey key exists in dict and it is not the same as default value defVal
    def _setProp(self, name, val, defVal):
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
                 shareInfo = False,
                 details = False):
        self._setProp("IncludeArticleBasicInfo", basicInfo, True)
        self._setProp("IncludeArticleTitle", title, True)
        self._setProp("IncludeArticleBody", body, True)
        self._setProp("IncludeArticleEventUri", eventUri, True)
        self._setProp("IncludeArticleConcepts", concepts, False)
        self._setProp("IncludeArticleStoryUri", storyUri, False)
        self._setProp("IncludeArticleDuplicateList", duplicateList, False)
        self._setProp("IncludeArticleOriginalArticle", originalArticle, False)
        self._setProp("IncludeArticleCategories", categories, False)
        self._setProp("IncludeArticleLocation", location, False)
        self._setProp("IncludeArticleImage", image, False)
        self._setProp("IncludeArticleExtractedDates", extractedDates, False)
        self._setProp("IncludeArticleShareInfo", shareInfo, False)
        self._setProp("IncludeArticleDetails", details, False)


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
                 shareInfo = False,
                 images = False):
        self._setProp("IncludeStoryBasicStats", basicStats, True)
        self._setProp("IncludeStoryLocation", location, True)
        
        self._setProp("IncludeStoryCategories", categories, False)
        self._setProp("IncludeStoryDate", date, False)
        self._setProp("IncludeStoryConcepts", concepts, False)
        self._setProp("IncludeStoryTitle", title, False)
        self._setProp("IncludeStorySummary", summary, False)
        self._setProp("IncludeStoryMedoidArticle", medoidArticle, False)
        self._setProp("IncludeStoryCommonDates", commonDates, False)
        self._setProp("IncludeStoryShareInfo", shareInfo, False)
        self._setProp("IncludeStoryImages", images, False)


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
                 shareInfo = False,
                 images = False):
        self._setProp("IncludeEventTitle", title, True)
        self._setProp("IncludeEventSummary", summary, True)
        self._setProp("IncludeEventArticleCounts", articleCounts, True)
        self._setProp("IncludeEventConcepts", concepts, True)
        self._setProp("IncludeEventCategories", categories, True)
        self._setProp("IncludeEventLocation", location, True)
        self._setProp("IncludeEventDate", date, True)

        self._setProp("IncludeEventCommonDates", commonDates, False)
        self._setProp("IncludeEventStories", stories, False)
        self._setProp("IncludeEventShareInfo", shareInfo, False)
        self._setProp("IncludeEventImages", images, False)
        

class SourceInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 title = True,
                 description = False,
                 location = False,
                 importance = False,
                 articleCount = False,
                 tags = False,
                 details = False):
        self._setProp("IncludeSourceTitle", title, True)

        self._setProp("IncludeSourceDescription", description, False)
        self._setProp("IncludeSourceLocation", location, False)
        self._setProp("IncludeSourceImportance", importance, False)
        self._setProp("IncludeSourceArticleCount", articleCount, False)
        self._setProp("IncludeSourceTags", tags, False)
        self._setProp("IncludeSourceDetails", details, False)


class CategoryInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 parent = False,
                 children = False,
                 trendingScore = False,
                 trendingHistory = False):
        self._setProp("IncludeCategoryParent", parent, False)
        self._setProp("IncludeCategoryChildren", children, False)
        self._setProp("IncludeCategoryTrendingScore", trendingScore, False)
        self._setProp("IncludeCategoryTrendingHistory", trendingHistory, False)


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
        self._setProp("IncludeConceptLabel", label, True)
        
        self._setProp("IncludeConceptSynonyms", synonyms, False)
        self._setProp("IncludeConceptImage", image, False)
        self._setProp("IncludeConceptDescription", description, False)
        self._setProp("IncludeConceptDetails", details, False)
        self._setProp("IncludeConceptConceptClassMembership", conceptClassMembership, False)
        self._setProp("IncludeConceptConceptClassMembershipFull", conceptClassMembershipFull, False)
        self._setProp("IncludeConceptConceptFolderMembership", conceptFolderMembership, False)
        self._setProp("IncludeConceptTrendingScore", trendingScore, False)
        self._setProp("IncludeConceptTrendingHistory", trendingHistory, False)


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
        self._setProp("IncludeLocationCountryLabel", countryLabel, True)
        self._setProp("IncludeLocationCountryWikiUri", countryWikiUri, False)
        self._setProp("IncludeLocationCountryGeoNamesId", countryGeoNamesId, False)
        self._setProp("IncludeLocationCountryArea", countryArea, False)
        self._setProp("IncludeLocationCountryPopulation", countryPopulation, False)
        self._setProp("IncludeLocationCountryLocation", countryLocation, False)
        self._setProp("IncludeLocationCountryDetails", countryDetails, False)
        self._setProp("IncludeLocationCountryContinent", countryContinent, False)

        self._setProp("IncludeLocationPlaceLabel", placeLabel, True)
        self._setProp("IncludeLocationPlaceWikiUri", placeWikiUri, False)
        self._setProp("IncludeLocationPlaceGeoNamesId", placeGeoNamesId, False)
        self._setProp("IncludeLocationPlacePopulation", placePopulation, False)
        self._setProp("IncludeLocationPlaceFeatureCode", placeFeatureCode, False)
        self._setProp("IncludeLocationPlaceLocation", placeLocation, False)
        self._setProp("IncludeLocationPlaceCountry", placeCountry, True)


class ConceptClassInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 parentLabels = True,
                 concepts = False,
                 details = False):
        self._setProp("IncludeConceptClassParentLabels", parentLabels, True)
        self._setProp("IncludeConceptClassConcepts", concepts, False)
        self._setProp("IncludeConceptClassDetails", details, False)
        

class ConceptFolderInfoFlags(ReturnInfoFlagsBase):
    def __init__(self,
                 definition = False,
                 owner = False,
                 details = False):
        self._setProp("IncludeConceptFolderDefinition", definition, False)
        self._setProp("IncludeConceptFolderOwner", owner, False)
        self._setProp("IncludeConceptFolderDetails", details, False)



class ReturnInfo:
    def __init__(self,
                 articleBodyLen = 300,
                 conceptType = ["concepts"],
                 conceptLang = ["eng"],
                 storyImageCount = 1,
                 eventImageCount = 1,
                 articleInfo = ArticleInfoFlags(),
                 storyInfo = StoryInfoFlags(),
                 eventInfo = EventInfoFlags(),
                 sourceInfo = SourceInfoFlags(),
                 categoryInfo = CategoryInfoFlags(),
                 conceptInfo = ConceptInfoFlags(),
                 locationInfo = LocationInfoFlags(),
                 conceptClassInfo = ConceptInfoFlags(),
                 conceptFolderInfo = ConceptFolderInfoFlags()):
        """
        ReturnInfo specifies what content should be returned for each possible returned type

        @type articleBodyLen: int
        @param articleBodyLen: max length of the article body (use -1 for full body, 0 for empty)
        """
        self.articleBodyLen = articleBodyLen
        self.conceptType = conceptType
        self.conceptLang = conceptLang
        self.storyImageCount = storyImageCount
        self.eventImageCount = eventImageCount
        self.articleInfo = articleInfo
        self.storyInfo = storyInfo
        self.eventInfo = eventInfo
        self.sourceInfo = sourceInfo
        self.categoryInfo = categoryInfo
        self.conceptInfo = conceptInfo
        self.locationInfo = locationInfo
        self.conceptClassInfo = conceptClassInfo
        self.conceptFolderInfo = conceptFolderInfo

    def getParams(self, prefix = ""):
        dict = {}
        dict[prefix == "" and "articleBodyLen" or prefix + "BodyLen"] = self.articleBodyLen
        dict[prefix == "" and "conceptType" or prefix + "ConceptType"] = self.conceptType
        dict[prefix == "" and "conceptLang" or prefix + "ConceptLang"] = self.conceptLang
        dict[prefix == "" and "storyImageCount" or prefix + "StoryImageCount"] = self.storyImageCount
        dict[prefix == "" and "eventImageCount" or prefix + "EventImageCount"] = self.eventImageCount
        dict.update(self.articleInfo.getParams(prefix == "" and "article" or prefix))
        dict.update(self.storyInfo.getParams(prefix == "" and "story" or prefix))
        dict.update(self.eventInfo.getParams(prefix == "" and "event" or prefix))
        dict.update(self.sourceInfo.getParams(prefix == "" and "source" or prefix))
        dict.update(self.categoryInfo.getParams(prefix == "" and "category" or prefix))
        dict.update(self.conceptInfo.getParams(prefix == "" and "concept" or prefix))
        dict.update(self.locationInfo.getParams(prefix == "" and "location" or prefix))
        dict.update(self.conceptClassInfo.getParams(prefix == "" and "conceptClass" or prefix))
        dict.update(self.conceptFolderInfo.getParams(prefix == "" and "conceptFolder" or prefix))
        return dict

