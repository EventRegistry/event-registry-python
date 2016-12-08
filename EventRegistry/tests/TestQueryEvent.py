import unittest
from eventregistry import *


class TestQueryEvent(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.er = EventRegistry(host = "http://eventregistry.org")
        self.articleInfo = ArticleInfoFlags(bodyLen = -1, concepts = True, storyUri = True, duplicateList = True, originalArticle = True, categories = True,
                location = True, image = True, extractedDates = True, socialScore = True, details = True)
        self.sourceInfo = SourceInfoFlags(description = True, location = True, importance = True, articleCount = True, tags = True, details = True)
        self.conceptInfo = ConceptInfoFlags(type=["entities"], lang = "spa", synonyms = True, image = True, description = True, details = True,
                conceptClassMembership = True, conceptFolderMembership = True, trendingScore = True, trendingHistory = True)
        self.locationInfo = LocationInfoFlags(wikiUri = True, label = True, geoNamesId = True, geoLocation = True, population = True,
                                              countryArea = True, countryDetails = True, countryContinent = True,
                                              placeFeatureCode = True, placeCountry = True)
        self.categoryInfo = CategoryInfoFlags(parentUri = True, childrenUris = True, trendingScore = True, trendingHistory = True)
        self.eventInfo = EventInfoFlags(commonDates = True, stories = True, socialScore = True, details = True, imageCount = 2)
        self.storyInfo = StoryInfoFlags(categories = True, date = True, concepts = True, title = True, summary = True,
                                        medoidArticle = True, commonDates = True, socialScore = True, imageCount = 2, details = True)
        self.returnInfo = ReturnInfo(articleInfo = self.articleInfo, conceptInfo = self.conceptInfo, eventInfo = self.eventInfo, storyInfo = self.storyInfo,
            sourceInfo = self.sourceInfo, locationInfo = self.locationInfo, categoryInfo = self.categoryInfo)

    def ensureValidConcept(self, concept, testName):
        for prop in ["id", "uri", "label", "synonyms", "image", "description", "details", "conceptClassMembership", "conceptFolderMembership", "trendingScore", "trendingHistory", "details"]:
            self.assertTrue(prop in concept, "Property '%s' was expected in concept for test %s" % (prop, testName))
        self.assertTrue(concept.get("type") in ["person", "loc", "org"], "Expected concept to be an entity type, but got %s" % (concept.get("type")))
        if concept.get("location"):
            self.ensureValidLocation(concept.get("location"), testName)

    def ensureValidArticle(self, article, testName):
        for prop in ["id", "url", "uri", "title", "body", "source", "details", "location", "duplicateList", "originalArticle", "time", "date", "categories", "lang", "extractedDates", "concepts", "details"]:
            self.assertTrue(prop in article, "Property '%s' was expected in article for test %s" % (prop, testName))
        for concept in article.get("concepts"):
            self.ensureValidConcept(concept, testName)
        self.assertTrue(article.get("isDuplicate") or "eventUri" in article, "Nonduplicates should have event uris")
        if article.get("location"):
            self.ensureValidLocation(article.get("location"), testName)

    def ensureValidSource(self, source, testName):
        for prop in ["id", "uri", "location", "importance", "articleCount", "tags", "details"]:
            self.assertTrue(prop in source, "Property '%s' was expected in source for test %s" % (prop, testName))
        if source.get("location"):
            self.ensureValidLocation(source.get("location"), testName)

    def ensureValidCategory(self, category, testName):
        for prop in ["id", "uri", "parentUri", "childrenUris", "trendingScore", "trendingHistory"]:
            self.assertTrue(prop in category, "Property '%s' was expected in source for test %s" % (prop, testName))

    def ensureValidEvent(self, event, testName):
        for prop in ["uri", "title", "summary", "articleCounts", "concepts", "categories", "location", "eventDate", "commonDates", "stories", "socialScore", "details", "images"]:
            self.assertTrue(prop in event, "Property '%s' was expected in event for test %s" % (prop, testName))
        for concept in event.get("concepts"):
            self.ensureValidConcept(concept, testName)
        for story in event.get("stories"):
            self.ensureValidStory(story, testName)
        for category in event.get("categories"):
            self.ensureValidCategory(category, testName)
        if event.get("location"):
            self.ensureValidLocation(event.get("location"), testName)

    def ensureValidStory(self, story, testName):
        for prop in ["uri", "title", "summary", "concepts", "categories", "location",
                     "storyDate", "averageDate", "commonDates", "socialScore", "details", "images"]:
            self.assertTrue(prop in story, "Property '%s' was expected in story for test %s" % (prop, testName))
        if story.get("location"):
            self.ensureValidLocation(story.get("location"), testName)

    def ensureValidLocation(self, location, testName):
        for prop in ["wikiUri", "label", "lat", "long", "geoNamesId", "population"]:
            self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "country":
            for prop in ["area", "code2", "code3", "webExt", "continent"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "place":
            for prop in ["featureCode", "country"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))


    def createQuery(self):
        return QueryEvent(list(range(100, 110)))


    def testArticleList(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventArticles(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            for article in event.get("articles").get("results"):
                self.ensureValidArticle(article, "testArticleList")


    def testArticleUris(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventArticleUris())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertTrue("articleUris" in event, "Expected to see 'articleUris'")


    def testKeywords(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventKeywordAggr())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("keywordAggr"), "Expected to see 'keywordAggr'")
            if isinstance(event.get("keywordAggr"), dict) and "error" in event.get("keywordAggr"):
                print("Got error: " + event.get("keywordAggr").get("error"))
                continue;
            for kw in event.get("keywordAggr").get("results"):
                self.assertIsNotNone(kw.get("keyword"), "Keyword expected")
                self.assertIsNotNone(kw.get("weight"), "Weight expected")

    def testSourceAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventSourceAggr())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("sourceExAggr"), "Expected to see 'sourceExAggr'")


    def testArticleTrend(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventArticleTrend())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("articleTrend"), "Expected to see 'articleTrend'")


    def testSimilarEvents(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventSimilarEvents(addArticleTrendInfo = True, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("similarEvents"), "Expected to see 'similarEvents'")
            for simEvent in event.get("similarEvents").get("results"):
                self.ensureValidEvent(simEvent, "testSimilarEvents")
            self.assertIsNotNone(event.get("similarEvents").get("trends"), "Expected to see a 'trends' property")


    def testSimilarStories(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventSimilarStories(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("similarStories"), "Expected to see 'similarStories'")
            for simStory in event.get("similarStories").get("results"):
                self.ensureValidStory(simStory, "testSimilarStories")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEvent)
    unittest.TextTestRunner(verbosity=3).run(suite)