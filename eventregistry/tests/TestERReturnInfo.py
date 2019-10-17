"""
test that setting return flags to false actually returns just the minimum set of properties in the returned objects
"""
import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator

class TestReturnInfo(DataValidator):

    def getEmptyReturnInfo(self):
        return ReturnInfo(
            articleInfo=ArticleInfoFlags(bodyLen=0, basicInfo=False, title=False, body=False, url=False, eventUri=False, concepts=False, categories=False, links=False, videos=False, image=False, socialScore=False, sentiment=False, location=False, dates=False, extractedDates=False, duplicateList=False, originalArticle=False, storyUri=False),
            eventInfo=EventInfoFlags(title=False, summary=False, articleCounts=False, concepts=False, categories=False, location=False, date=False, commonDates=False, infoArticle=False, stories=False, socialScore=False, imageCount=0),
            sourceInfo = SourceInfoFlags(title = False, description = False,location = False,ranking = False,image = False,articleCount = False,socialMedia = False,sourceGroups = False),
            conceptInfo=ConceptInfoFlags(type="concepts", lang="slv", label=False, synonyms=False, image=False, description=False, conceptClassMembership=False, conceptClassMembershipFull=False, totalCount=False, trendingSource="news", maxConceptsPerType=20),
            locationInfo=LocationInfoFlags(label=False, wikiUri=False, geoNamesId=False, population=False, geoLocation=False, countryArea=False, countryDetails=False, countryContinent=False, placeFeatureCode=False, placeCountry=False),
            storyInfo = StoryInfoFlags(basicStats = False,location = False,date = False,title = False,summary = False,concepts = False,categories = False,medoidArticle = False,infoArticle = False,commonDates = False,socialScore = False,imageCount = 0),
            conceptClassInfo = ConceptClassInfoFlags(parentLabels = False))

    def ensureValidConcept(self, concept, testName):
        for prop in ["label", "synonyms", "image"]:
            self.assertFalse(prop in concept, "Property '%s' was not expected in concept for test %s" % (prop, testName))
        self.assertTrue(concept.get("type") in ["loc"], "Expected concept to be a location type, but got %s" % (concept.get("type")))
        if concept.get("location"):
            self.ensureValidLocation(concept.get("location"), testName)


    def ensureValidArticle(self, article, testName):
        for prop in ["url", "title", "body", "source", "time", "date", "lang", "image", "links", "videos", "categories", "location", "isDuplicate", "duplicateList", "originalArticle", "extractedDates", "concepts", "shares", "sentiment"]:
            self.assertFalse(prop in article, "Property '%s' was not expected in article for test %s" % (prop, testName))
        for concept in article.get("concepts", []):
            self.ensureValidConcept(concept, testName)


    def ensureValidSource(self, source, testName):
        for prop in ["title", "description", "image", "thumbImage", "favicon", "location", "ranking", "articleCount", "sourceGroups", "socialMedia"]:
            self.assertFalse(prop in source, "Property '%s' was not expected in source for test %s" % (prop, testName))


    def ensureValidCategory(self, category, testName):
        for prop in ["parentUri"]:
            self.assertFalse(prop in category, "Property '%s' was not expected in source for test %s" % (prop, testName))


    def ensureValidLocation(self, location, testName):
        for prop in ["wikiUri", "label", "lat", "long", "geoNamesId", "population"]:
            self.assertFalse(prop in location, "Property '%s' was not expected in a location for test %s" % (prop, testName))
        if location.get("type") == "country":
            for prop in ["area", "code2", "code3", "webExt", "continent"]:
                self.assertFalse(prop in location, "Property '%s' was not expected in a location for test %s" % (prop, testName))
        if location.get("type") == "place":
            for prop in ["featureCode", "country"]:
                self.assertFalse(prop in location, "Property '%s' was not expected in a location for test %s" % (prop, testName))


    def ensureValidEvent(self, event, testName):
        for prop in ["title", "summary", "articleCounts", "concepts", "categories", "location", "eventDate", "commonDates", "stories", "socialScore", "images"]:
            self.assertFalse(prop in event, "Property '%s' was not expected in event for test %s" % (prop, testName))
        for concept in event.get("concepts", []):
            self.ensureValidConcept(concept, testName)
        for story in event.get("stories", []):
            self.ensureValidStory(story, testName)
        for category in event.get("categories", []):
            self.ensureValidCategory(category, testName)
        if event.get("location"):
            self.ensureValidLocation(event.get("location"), testName)


    def ensureValidStory(self, story, testName):
        for prop in ["title", "summary", "concepts", "categories", "location",
                     "storyDate", "averageDate", "commonDates", "socialScore", "images"]:
            self.assertFalse(prop in story, "Property '%s' was not expected in story for test %s" % (prop, testName))
        if story.get("location"):
            self.ensureValidLocation(story.get("location"), testName)


    def testArticleResult(self):
        q = QueryArticles(keywords="Obama", requestedResult=RequestArticlesInfo(returnInfo = self.getEmptyReturnInfo()))
        res = self.er.execQuery(q)
        for art in res.get("articles", {}).get("results"):
            self.ensureValidArticle(art, "testArticleResult")


    def testEventResult(self):
        q = QueryEvents(keywords="Trump", requestedResult = RequestEventsInfo(returnInfo = self.getEmptyReturnInfo()))
        res = self.er.execQuery(q)
        for event in res.get("events", {}).get("results"):
            self.ensureValidEvent(event, "testEventResult")


    def testConceptResult(self):
        uri = self.er.getConceptUri("Ljubljana")
        retInfo = self.er.getConceptInfo(uri, returnInfo=self.getEmptyReturnInfo())
        concept = retInfo[uri]
        self.ensureValidConcept(concept, "testConceptResult")



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReturnInfo)
    unittest.TextTestRunner(verbosity=3).run(suite)
