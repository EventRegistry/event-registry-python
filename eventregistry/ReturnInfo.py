"""
the classes here represent all the types of information that can be returned
from Event Registry requests

the ReturnInfo class specifies all types of these parameters and is needed as
a parameter in all query requests
"""
import os, json

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


    def _setVal(self, name: str, val, defVal = None):
        """set value of name to val in case the val != defVal"""
        if val == defVal:
            return
        if not hasattr(self, "vals"):
            self.vals = {}
        self.vals[name] = val


    def _getVals(self, prefix: str = ""):
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


    def _addKwdArgs(self, kwdArgs):
        for name, val in kwdArgs.items():
            if isinstance(val, bool):
                self._setFlag(name, val, not val)
            else:
                self._setVal(name, val)


class ArticleInfoFlags(ReturnInfoFlagsBase):
    """"
    What information about an article should be returned by the API call

    @param bodyLen: max length of the article body (use -1 for full body, 0 for empty)
    @param basicInfo: core article information -
    @param title: article title
    @param body: article body
    @param url: article url
    @param eventUri: uri of the event to which the article belongs
    @param authors: the list of authors of the news article
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
    @param originalArticle: if the article is a duplicate, this will provide information about the original article
    @param storyUri: uri of the story (cluster) to which the article belongs
    """
    def __init__(self,
                 bodyLen: int = -1,
                 basicInfo: bool = True,
                 title: bool = True,
                 body: bool = True,
                 url: bool = True,
                 eventUri: bool = True,
                 authors: bool = True,
                 concepts: bool = False,
                 categories: bool = False,
                 links: bool = False,
                 videos: bool = False,
                 image: bool = True,
                 socialScore: bool = False,
                 sentiment: bool = True,
                 location: bool = False,
                 extractedDates: bool = False,
                 originalArticle: bool = False,
                 storyUri: bool = False,
                 **kwdArgs):
        self._setVal("articleBodyLen", bodyLen, -1)
        self._setFlag("includeArticleBasicInfo", basicInfo, True)
        self._setFlag("includeArticleTitle", title, True)
        self._setFlag("includeArticleBody", body, True)
        self._setFlag("includeArticleUrl", url, True)
        self._setFlag("includeArticleEventUri", eventUri, True)
        self._setFlag("includeArticleAuthors", authors, True)
        self._setFlag("includeArticleConcepts", concepts, False)
        self._setFlag("includeArticleCategories", categories, False)
        self._setFlag("includeArticleLinks", links, False)
        self._setFlag("includeArticleVideos", videos, False)
        self._setFlag("includeArticleImage", image, True)
        self._setFlag("includeArticleSocialScore", socialScore, False)
        self._setFlag("includeArticleSentiment", sentiment, True)
        self._setFlag("includeArticleLocation", location, False)
        self._setFlag("includeArticleExtractedDates", extractedDates, False)
        self._setFlag("includeArticleOriginalArticle", originalArticle, False)
        self._setFlag("includeArticleStoryUri", storyUri, False)
        self._addKwdArgs(kwdArgs)



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
                basicStats: bool = True,
                location: bool = True,
                date: bool = False,
                title: bool = False,
                summary: bool = False,
                concepts: bool = False,
                categories: bool = False,
                medoidArticle: bool = False,
                infoArticle: bool = False,
                commonDates: bool = False,
                socialScore: bool = False,
                imageCount: int = 0,
                **kwdArgs):
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
        self._addKwdArgs(kwdArgs)



class EventInfoFlags(ReturnInfoFlagsBase):
    """
    What information about an event should be returned by the API call

    @param title: return the title of the event
    @param summary: return the summary of the event
    @param articleCounts: return the number of articles that are assigned to the event
    @param concepts: return information about the main concepts related to the event
    @param categories: return information about the categories related to the event
    @param location: return the location where the event occurred
    @param date: return information about the date of the event
    @param commonDates: return the dates that were commonly found in the articles about the event
    @param infoArticle: return for each language the article from which we have extracted the summary and title for event for that language
    @param stories: return the list of stories (clusters) that are about the event
    @param socialScore: score computed based on how frequently the articles in the event were shared on social media
    @param imageCount: number of images to be returned for an event
    """
    def __init__(self,
                title: bool = True,
                summary: bool = True,
                articleCounts: bool = True,
                concepts: bool = True,
                categories: bool = True,
                location: bool = True,
                date: bool = True,
                commonDates: bool = False,
                infoArticle: bool = False,
                stories: bool = False,
                socialScore: bool = False,
                imageCount: int = 0,
                **kwdArgs):
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
        self._addKwdArgs(kwdArgs)



class MentionInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a mention should be returned by the API call

    @param basicInfo: return basic information about the mention
    @param slots: return the list of slots (concepts) related to the mention
    @param categories: return the list of categories associated with the article that contains the sentence from the mention
    @param frameworks: return list of frameworks to which the event type of the mention belongs
    """
    def __init__(self,
                basicInfo: bool = True,
                slots: bool = True,
                categories: bool = False,
                frameworks: bool = True,
                **kwdArgs):
        self._setFlag("includeMentionBasicInfo", basicInfo, True)
        self._setFlag("includeMentionSlots", slots, True)
        self._setFlag("includeMentionCategories", categories, False)
        self._setFlag("includeMentionFrameworks", frameworks, True)
        self._addKwdArgs(kwdArgs)



class SourceInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a news source should be returned by the API call

    @param title: title of the news source
    @param description: description of the news source
    @param location: geographic location of the news source
    @param ranking: a set of rankings for the news source
    @param image: different images associated with the news source
    @param socialMedia: different social media accounts used by the news source
    """
    def __init__(self,
                title: bool = True,
                description: bool = False,
                location: bool = False,
                ranking: bool = False,
                image: bool = False,
                socialMedia: bool = False,
                **kwdArgs):
        self._setFlag("includeSourceTitle", title, True)
        self._setFlag("includeSourceDescription", description, False)
        self._setFlag("includeSourceLocation", location, False)
        self._setFlag("includeSourceRanking", ranking, False)
        self._setFlag("includeSourceImage", image, False)
        self._setFlag("includeSourceSocialMedia", socialMedia, False)
        self._addKwdArgs(kwdArgs)



class CategoryInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a category should be returned by the API call

    @param trendingScore: information about how the category is currently trending. The score is computed as Pearson residual by comparing the trending of the category in last 2 days compared to last 14 days
    """
    def __init__(self,
                trendingScore: bool = False,
                **kwdArgs):
        self._setFlag("includeCategoryTrendingScore", trendingScore, False)
        self._addKwdArgs(kwdArgs)



class ConceptInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept should be returned by the API call

    @param type: which types of concepts should be provided in events, stories, ... Options: person, loc, org, wiki (non-entities), concepts (=person+loc+org+wiki), conceptClass, conceptFolder
    @param lang: in which languages should be the labels for provided concepts
    @param label: return label(s) of the concept
    @param synonyms: return concept synonyms (if any)
    @param image: provide an image associated with the concept
    @param description: description of the concept
    @param trendingScore: information about how the concept is currently trending. The score is computed as Pearson residual by comparing the trending of the concept in last 2 days compared to last 14 days
    @type type: str | list
    @type lang: str | list
    """
    def __init__(self,
                type: str = "concepts",
                lang: str = "eng",
                label: bool = True,
                synonyms: bool = False,
                image: bool = False,
                description: bool = False,
                trendingScore: bool = False,
                maxConceptsPerType: int = 20,
                **kwdArgs):
        self._setVal("conceptType", type, "concepts")
        self._setVal("conceptLang", lang, "eng")
        self._setFlag("includeConceptLabel", label, True)
        self._setFlag("includeConceptSynonyms", synonyms, False)
        self._setFlag("includeConceptImage", image, False)
        self._setFlag("includeConceptDescription", description, False)
        self._setFlag("includeConceptTrendingScore", trendingScore, False)
        self._setVal("maxConceptsPerType", maxConceptsPerType, 20)
        self._addKwdArgs(kwdArgs)



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
                label: bool = True,
                wikiUri: bool = False,
                geoNamesId: bool = False,
                population: bool = False,
                geoLocation: bool = False,

                countryArea: bool = False,
                countryDetails: bool = False,
                countryContinent: bool = False,

                placeFeatureCode: bool = False,
                placeCountry: bool = True,
                **kwdArgs):
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
        self._addKwdArgs(kwdArgs)



class ConceptClassInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept class should be returned by the API call

    @param parentLabels: return the list of labels of the parent concept classes
    @param concepts: return the list of concepts assigned to the concept class
    """
    def __init__(self,
                parentLabels: bool = True,
                concepts: bool = False,
                **kwdArgs):
        self._setFlag("includeConceptClassParentLabels", parentLabels, True)
        self._setFlag("includeConceptClassConcepts", concepts, False)
        self._addKwdArgs(kwdArgs)



class ConceptFolderInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept folder should be returned by the API call

    @param definition: return the complete definition of the concept folder
    @param owner: return information about the owner of the concept folder
    """
    def __init__(self,
                definition: bool = False,
                owner: bool = False,
                **kwdArgs):
        self._setFlag("includeConceptFolderDefinition", definition, False)
        self._setFlag("includeConceptFolderOwner", owner, False)
        self._addKwdArgs(kwdArgs)



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
    @param mentionInfo: what details about the mention should be returned
    @param conceptFolderInfo: what details about the concept folders should be returned (concept folders are sub-types of concepts so their information will be a property inside the concept information)
    """
    def __init__(self,
                 articleInfo : ArticleInfoFlags = ArticleInfoFlags(),
                 eventInfo : EventInfoFlags = EventInfoFlags(),
                 sourceInfo : SourceInfoFlags = SourceInfoFlags(),
                 categoryInfo : CategoryInfoFlags = CategoryInfoFlags(),
                 conceptInfo : ConceptInfoFlags = ConceptInfoFlags(),
                 locationInfo : LocationInfoFlags = LocationInfoFlags(),
                 storyInfo : StoryInfoFlags = StoryInfoFlags(),
                 mentionInfo : MentionInfoFlags = MentionInfoFlags(),
                 conceptFolderInfo : ConceptFolderInfoFlags= ConceptFolderInfoFlags()):
        assert isinstance(articleInfo, ArticleInfoFlags)
        assert isinstance(eventInfo, EventInfoFlags)
        assert isinstance(sourceInfo, SourceInfoFlags)
        assert isinstance(categoryInfo, CategoryInfoFlags)
        assert isinstance(conceptInfo, ConceptInfoFlags)
        assert isinstance(locationInfo, LocationInfoFlags)
        assert isinstance(storyInfo, StoryInfoFlags)
        assert isinstance(mentionInfo, MentionInfoFlags)
        assert isinstance(conceptFolderInfo, ConceptFolderInfoFlags)
        self.articleInfo = articleInfo
        self.eventInfo = eventInfo
        self.sourceInfo = sourceInfo
        self.categoryInfo = categoryInfo
        self.conceptInfo = conceptInfo
        self.locationInfo = locationInfo
        self.storyInfo = storyInfo
        self.mentionInfo = mentionInfo
        self.conceptFolderInfo = conceptFolderInfo


    @staticmethod
    def loadFromFile(fileName: str):
        """
        load the configuration for the ReturnInfo from a fileName
        @param fileName: filename that contains the json configuration to use in the ReturnInfo
        """
        assert os.path.exists(fileName), "File " + fileName + " does not exist"
        conf = json.load(open(fileName, encoding="utf8"))
        return ReturnInfo(
            articleInfo=ArticleInfoFlags(**conf.get("articleInfo", {})),
            eventInfo=EventInfoFlags(**conf.get("eventInfo", {})),
            sourceInfo=SourceInfoFlags(**conf.get("sourceInfo", {})),
            categoryInfo=CategoryInfoFlags(**conf.get("categoryInfo", {})),
            conceptInfo=ConceptInfoFlags(**conf.get("conceptInfo", {})),
            locationInfo=LocationInfoFlags(**conf.get("locationInfo", {})),
            storyInfo=StoryInfoFlags(**conf.get("storyInfo", {})),
            mentionInfo=MentionInfoFlags(**conf.get("mentionInfo", {})),
            conceptFolderInfo=ConceptFolderInfoFlags(**conf.get("conceptFolderInfo", {}))
        )


    def getConf(self):
        """
        return configuration in a json object that stores properties set by each *InfoFlags class
        """
        conf = {
            "articleInfo": self.articleInfo._getFlags().copy(),
            "eventInfo": self.eventInfo._getFlags().copy(),
            "sourceInfo": self.sourceInfo._getFlags().copy(),
            "categoryInfo":  self.categoryInfo._getFlags().copy(),
            "conceptInfo": self.conceptInfo._getFlags().copy(),
            "locationInfo": self.locationInfo._getFlags().copy(),
            "storyInfo": self.storyInfo._getFlags().copy(),
            "mentionInfo": self.mentionInfo._getFlags().copy(),
            "conceptFolderInfo": self.articleInfo._getFlags().copy()
        }
        conf["articleInfo"].update(self.articleInfo._getVals())
        conf["eventInfo"].update(self.eventInfo._getVals())
        conf["sourceInfo"].update(self.sourceInfo._getVals())
        conf["categoryInfo"].update(self.categoryInfo._getVals())
        conf["conceptInfo"].update(self.conceptInfo._getVals())
        conf["locationInfo"].update(self.locationInfo._getVals())
        conf["storyInfo"].update(self.storyInfo._getVals())
        conf["mentionInfo"].update(self.mentionInfo._getVals())
        conf["conceptFolderInfo"].update(self.conceptFolderInfo._getVals())
        return conf


    def getParams(self, prefix = ""):
        dict = {}
        dict.update(self.articleInfo._getFlags())
        dict.update(self.eventInfo._getFlags())
        dict.update(self.sourceInfo._getFlags())
        dict.update(self.conceptInfo._getFlags())
        dict.update(self.categoryInfo._getFlags())
        dict.update(self.locationInfo._getFlags())
        dict.update(self.storyInfo._getFlags())
        dict.update(self.mentionInfo._getFlags())
        dict.update(self.conceptFolderInfo._getFlags())

        dict.update(self.articleInfo._getVals())
        dict.update(self.eventInfo._getVals())
        dict.update(self.sourceInfo._getVals())
        dict.update(self.conceptInfo._getVals())
        dict.update(self.categoryInfo._getVals())
        dict.update(self.locationInfo._getVals())
        dict.update(self.storyInfo._getVals())
        dict.update(self.mentionInfo._getVals())
        dict.update(self.conceptFolderInfo._getVals())
        return dict

