"""
the classes here represent all the types of information that can be returned
from Event Registry requests

the ReturnInfo class specifies all types of these parameters and is needed as
a parameter in all query requests
"""
import inspect
import os
import json
from typing import Union

from eventregistry.Logger import logger

# the names exported by "from eventregistry import *"
__all__ = ["ReturnInfoFlagsBase", "ArticleInfoFlags", "StoryInfoFlags", "EventInfoFlags", "MentionInfoFlags",
           "SourceInfoFlags", "CategoryInfoFlags", "ConceptInfoFlags", "LocationInfoFlags", "ConceptClassInfoFlags",
           "ConceptFolderInfoFlags", "ReturnInfo"]


class ReturnInfoFlagsBase:
    """
    base class for the return info types
    """

    def _setFlag(self, name, val, defVal):
        """set the objects property propName if the dictKey key exists in dict and it is not the same as default value defVal"""
        if not hasattr(self, "flags"):
            self.flags = {}
        self._getKnownApiNames().add(name)
        if val != defVal:
            self.flags[name] = val


    def _getKnownApiNames(self) -> set:
        """the names of the api parameters that the named parameters of the class set"""
        if not hasattr(self, "_knownApiNames"):
            self._knownApiNames: set = set()
        return self._knownApiNames


    def _getFlags(self):
        """return the dict of stored flags"""
        if not hasattr(self, "flags"):
            self.flags = {}
        return self.flags


    def _setVal(self, name: str, val, defVal = None):
        """set value of name to val in case the val != defVal"""
        self._getKnownApiNames().add(name)
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
        vals = {}
        for key in list(self.vals.keys()):
            # if no prefix then lower the first letter
            if prefix == "":
                newkey = key[:1].lower() + key[1:] if key else ""
                vals[newkey] = self.vals[key]
            else:
                newkey = key[:1].upper() + key[1:] if key else ""
                vals[prefix + newkey] = self.vals[key]
        return vals


    def _addKwdArgs(self, kwdArgs):
        """
        add the flags and values that are not among the named parameters of the class. They are sent to the server as they are,
        so that also newly added flags can be used. A name that differs from a known parameter only in the letter case is
        a typo, and for the other unknown names we log a warning, since the server silently ignores the flags it does not know.
        Flags given with their full api name (e.g. includeArticleConcepts) are accepted without a warning
        """
        if not kwdArgs:
            return
        knownParams = {name.lower(): name for name in inspect.signature(type(self).__init__).parameters}
        for name, val in kwdArgs.items():
            if name in self._getKnownApiNames():
                # the full api name of a named parameter
                if isinstance(val, bool):
                    self._getFlags()[name] = val
                else:
                    self._setVal(name, val)
                continue
            if name.lower() in knownParams:
                raise TypeError("%s() got an unknown argument '%s'. Did you mean '%s'?" % (type(self).__name__, name, knownParams[name.lower()]))
            if not name.startswith("include"):
                logger.warning("'%s' is not a known parameter of %s. It will be sent to the server as it is - check the name if this is not intended.", name, type(self).__name__)
            if isinstance(val, bool):
                self._setFlag(name, val, not val)
            else:
                self._setVal(name, val)


class ArticleInfoFlags(ReturnInfoFlagsBase):
    """"
    What information about an article should be returned by the API call

    Args:
        bodyLen: max length of the article body (use -1 for full body, 0 for empty)
        basicInfo: core article information -
        title: article title
        body: article body
        url: article url
        eventUri: uri of the event to which the article belongs
        authors: the list of authors of the news article
        concepts: the list of concepts mentioned in the article
        categories: the list of categories assigned to the article
        links: the list of urls of links identified in the article body
        videos: the list of videos assigned to the article
        image: url to the image associated with the article
        socialScore: information about the number of times the article was shared on facebook and linkedin, instagram, ...
        sentiment: sentiment about the article
        location: the geographic location that the event mentioned in the article is about
        dates: the dates when the articles was crawled and the date when it was published (based on the rss feed date)
        extractedDates: the list of dates found mentioned in the article
        originalArticle: if the article is a duplicate, this will provide information about the original article
        storyUri: uri of the story (cluster) to which the article belongs
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

    Args:
        basicStats: core stats about the story
        location: geographic location that the story is about
        date: date of the story
        title: title of the story
        summary: summary of the story
        concepts: set of concepts associated with the story
        categories: categories associated with the story
        medoidArticle: the article that is closest to the center of the cluster of articles assigned to the story
        infoArticle: the article from which we have extracted the title and summary for the story
        commonDates: dates that were frequently identified in the articles belonging to the story
        socialScore: score computed based on how frequently the articles in the story were shared on social media
        imageCount: number of images to be returned for a story
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

    Args:
        title: return the title of the event
        summary: return the summary of the event
        articleCounts: return the number of articles that are assigned to the event
        concepts: return information about the main concepts related to the event
        categories: return information about the categories related to the event
        location: return the location where the event occurred
        date: return information about the date of the event
        commonDates: return the dates that were commonly found in the articles about the event
        infoArticle: return for each language the article from which we have extracted the summary and title for event for that language
        stories: return the list of stories (clusters) that are about the event
        socialScore: score computed based on how frequently the articles in the event were shared on social media
        imageCount: number of images to be returned for an event
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

    Args:
        basicInfo: return basic information about the mention
        slots: return the list of slots (concepts) related to the mention
        categories: return the list of categories associated with the article that contains the sentence from the mention
        frameworks: return list of frameworks to which the event type of the mention belongs
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

    Args:
        title: title of the news source
        description: description of the news source
        location: geographic location of the news source
        ranking: a set of rankings for the news source
        image: different images associated with the news source
        socialMedia: different social media accounts used by the news source
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

    Args:
        trendingScore: information about how the category is currently trending. The score is computed as Pearson residual by comparing the trending of the category in last 2 days compared to last 14 days
    """
    def __init__(self,
                trendingScore: bool = False,
                **kwdArgs):
        self._setFlag("includeCategoryTrendingScore", trendingScore, False)
        self._addKwdArgs(kwdArgs)



class ConceptInfoFlags(ReturnInfoFlagsBase):
    """
    What information about a concept should be returned by the API call

    Args:
        type (str | list): which types of concepts should be provided in events, stories, ... Options: person, loc, org, wiki (non-entities), concepts (=person+loc+org+wiki), conceptClass, conceptFolder
        lang (str | list): in which languages should be the labels for provided concepts
        label: return label(s) of the concept
        synonyms: return concept synonyms (if any)
        image: provide an image associated with the concept
        description: description of the concept
        trendingScore: information about how the concept is currently trending. The score is computed as Pearson residual by comparing the trending of the concept in last 2 days compared to last 14 days
        maxConceptsPerType: the maximum number of concepts of each type to return
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

    Args:
        label: return label of the place/country
        wikiUri: return wiki url of the place/country
        geoNamesId: return geonames id for the place/country
        population: return the population of the place/country
        geoLocation: return geographic coordinates of the place/country
        countryArea: return geographic area of the country
        countryDetails: return additional details about the country
        countryContinent: return continent where the country is located
        placeFeatureCode: return the geonames feature code of the place
        placeCountry: return information about the country where the place is located
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

    Args:
        parentLabels: return the list of labels of the parent concept classes
        concepts: return the list of concepts assigned to the concept class
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

    Args:
        definition: return the complete definition of the concept folder
        owner: return information about the owner of the concept folder
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

    Args:
        articleInfo: what details about the articles should be returned
        eventInfo: what details about the event should be returned
        sourceInfo: what details about the article's news source should be returned
        storyInfo: what details about the stories (clusters) should be returned
        categoryInfo: what details about the categories should be returned
        conceptInfo: what details about the concepts should be returned
        locationInfo: what details about the locations should be returned (locations are sub-types of concepts so their information will be a property inside the concept information)
        mentionInfo: what details about the mention should be returned
        conceptFolderInfo: what details about the concept folders should be returned (concept folders are sub-types of concepts so their information will be a property inside the concept information)
    """
    def __init__(self,
                 articleInfo: Union[ArticleInfoFlags, None] = None,
                 eventInfo: Union[EventInfoFlags, None] = None,
                 sourceInfo: Union[SourceInfoFlags, None] = None,
                 categoryInfo: Union[CategoryInfoFlags, None] = None,
                 conceptInfo: Union[ConceptInfoFlags, None] = None,
                 locationInfo: Union[LocationInfoFlags, None] = None,
                 storyInfo: Union[StoryInfoFlags, None] = None,
                 mentionInfo: Union[MentionInfoFlags, None] = None,
                 conceptFolderInfo: Union[ConceptFolderInfoFlags, None] = None):
        self.articleInfo = articleInfo if articleInfo is not None else ArticleInfoFlags()
        self.eventInfo = eventInfo if eventInfo is not None else EventInfoFlags()
        self.sourceInfo = sourceInfo if sourceInfo is not None else SourceInfoFlags()
        self.categoryInfo = categoryInfo if categoryInfo is not None else CategoryInfoFlags()
        self.conceptInfo = conceptInfo if conceptInfo is not None else ConceptInfoFlags()
        self.locationInfo = locationInfo if locationInfo is not None else LocationInfoFlags()
        self.storyInfo = storyInfo if storyInfo is not None else StoryInfoFlags()
        self.mentionInfo = mentionInfo if mentionInfo is not None else MentionInfoFlags()
        self.conceptFolderInfo = conceptFolderInfo if conceptFolderInfo is not None else ConceptFolderInfoFlags()
        if not (isinstance(self.articleInfo, ArticleInfoFlags)):
            raise TypeError("articleInfo should be of type ArticleInfoFlags")
        if not (isinstance(self.eventInfo, EventInfoFlags)):
            raise TypeError("eventInfo should be of type EventInfoFlags")
        if not (isinstance(self.sourceInfo, SourceInfoFlags)):
            raise TypeError("sourceInfo should be of type SourceInfoFlags")
        if not (isinstance(self.categoryInfo, CategoryInfoFlags)):
            raise TypeError("categoryInfo should be of type CategoryInfoFlags")
        if not (isinstance(self.conceptInfo, ConceptInfoFlags)):
            raise TypeError("conceptInfo should be of type ConceptInfoFlags")
        if not (isinstance(self.locationInfo, LocationInfoFlags)):
            raise TypeError("locationInfo should be of type LocationInfoFlags")
        if not (isinstance(self.storyInfo, StoryInfoFlags)):
            raise TypeError("storyInfo should be of type StoryInfoFlags")
        if not (isinstance(self.mentionInfo, MentionInfoFlags)):
            raise TypeError("mentionInfo should be of type MentionInfoFlags")
        if not (isinstance(self.conceptFolderInfo, ConceptFolderInfoFlags)):
            raise TypeError("conceptFolderInfo should be of type ConceptFolderInfoFlags")


    @staticmethod
    def loadFromFile(fileName: str):
        """
        load the configuration for the ReturnInfo from a fileName

        Args:
            fileName: filename that contains the json configuration to use in the ReturnInfo
        """
        if not (os.path.exists(fileName)):
            raise FileNotFoundError("File " + fileName + " does not exist")
        with open(fileName, encoding="utf-8") as f:
            conf = json.load(f)
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
            "categoryInfo": self.categoryInfo._getFlags().copy(),
            "conceptInfo": self.conceptInfo._getFlags().copy(),
            "locationInfo": self.locationInfo._getFlags().copy(),
            "storyInfo": self.storyInfo._getFlags().copy(),
            "mentionInfo": self.mentionInfo._getFlags().copy(),
            "conceptFolderInfo": self.conceptFolderInfo._getFlags().copy()
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
        params = {}
        params.update(self.articleInfo._getFlags())
        params.update(self.eventInfo._getFlags())
        params.update(self.sourceInfo._getFlags())
        params.update(self.conceptInfo._getFlags())
        params.update(self.categoryInfo._getFlags())
        params.update(self.locationInfo._getFlags())
        params.update(self.storyInfo._getFlags())
        params.update(self.mentionInfo._getFlags())
        params.update(self.conceptFolderInfo._getFlags())

        params.update(self.articleInfo._getVals())
        params.update(self.eventInfo._getVals())
        params.update(self.sourceInfo._getVals())
        params.update(self.conceptInfo._getVals())
        params.update(self.categoryInfo._getVals())
        params.update(self.locationInfo._getVals())
        params.update(self.storyInfo._getVals())
        params.update(self.mentionInfo._getVals())
        params.update(self.conceptFolderInfo._getVals())
        return params
