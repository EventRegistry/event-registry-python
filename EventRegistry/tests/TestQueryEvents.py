import unittest
from eventregistry import *


class TestQueryEvents(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.er = EventRegistry(host = "http://eventregistry.org")

        self.articleInfo = ArticleInfoFlags(bodyLen = -1, concepts = True, storyUri = True, duplicateList = True, originalArticle = True, categories = True,
                location = True, image = True, extractedDates = True, socialScore = True, details = True)
        self.sourceInfo = SourceInfoFlags(description = True, location = True, importance = True, articleCount = True, tags = True, details = True)
        self.conceptInfo = ConceptInfoFlags(type=["entities"], lang = ["eng", "spa"], synonyms = True, image = True, description = True, details = True,
                conceptClassMembership = True, conceptFolderMembership = True, trendingScore = True, trendingHistory = True, )
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
        if "newEventUri" in event:
            return
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


    def validateGeneralEventList(self, res):
        self.assertIsNotNone(res.get("events"), "Expected to get 'events'")

        events = res.get("events").get("results")
        self.assertEqual(len(events), 10, "Expected to get 10 events but got %d" % (len(events)))
        for event in events:
            self.ensureValidEvent(event, "eventList")

    def createQuery(self):
        q = QueryEvents()
        q.addConcept(self.er.getConceptUri("Obama"))
        return q

    def testEventList(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    def testEventListWithKeywordSearch(self):
        q = QueryEvents(keywords="germany")
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    def testEventListWithSourceSearch(self):
        q = QueryEvents(sourceUri = self.er.getNewsSourceUri("bbc"))
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    def testEventListWithCategorySearch(self):
        q = QueryEvents(categoryUri = self.er.getCategoryUri("disa"))
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    def testEventListWithLanguageSearch(self):
        q = QueryEvents(lang = "spa")
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        if "error" in res:
            return
        self.validateGeneralEventList(res)

    def testEventListWithMinArtsSearch(self):
        q = QueryEvents(minArticlesInEvent = 100)
        q.addRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    def testConceptTrends(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 5, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptTrends"), "Expected to get 'conceptTrends'")
        self.assertIsNotNone(res.get("conceptTrends").get("trends"), "Expected to get 'trends' property in conceptTrends")
        self.assertIsNotNone(res.get("conceptTrends").get("conceptInfo"), "Expected to get 'conceptInfo' property in conceptTrends")
        self.assertTrue(len(res["conceptTrends"]["conceptInfo"]) == 5, "Expected to get 5 concepts in concept trends")
        trends = res["conceptTrends"]["trends"]
        self.assertTrue(len(trends) > 0, "Expected to get trends for some days")
        for trend in trends:
            self.assertTrue("date" in trend, "A trend should have a date")
            self.assertTrue("conceptFreq" in trend, "A trend should have a conceptFreq")
            self.assertTrue("totArts" in trend, "A trend should have a totArts property")
            self.assertTrue(len(trend.get("conceptFreq")), "Concept frequencies should contain 5 elements - one for each concept")
        for concept in res.get("conceptTrends").get("conceptInfo"):
            self.ensureValidConcept(concept, "conceptTrends")


    def testConceptAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 50, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptAggr"), "Expected to get 'conceptAggr'")
        concepts = res.get("conceptAggr", {}).get("results", [])
        # concept count is per type so we expect 3*50
        self.assertEqual(len(concepts), 3*50, "Expected a different number of concept in conceptAggr")
        for concept in concepts:
            self.ensureValidConcept(concept, "conceptAggr")


    def testKeywordAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsKeywordAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("keywordAggr"), "Expected to get 'keywordAggr'")
        keywords = res.get("keywordAggr", {}).get("results")
        self.assertTrue(len(keywords) > 0, "Expected to get some keywords")
        for kw in keywords:
            self.assertTrue("keyword" in kw, "Expected a keyword property")
            self.assertTrue("weight" in kw, "Expected a weight property")


    def testCategoryAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsCategoryAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("categoryAggr"), "Expected to get 'categoryAggr'")
        categories = res.get("categoryAggr", {}).get("results")
        self.assertTrue(len(categories) > 0, "Expected to get a non empty category aggr")
        for cat in categories:
            self.ensureValidCategory(cat, "categoryAggr")


    def testConceptMatrix(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsConceptMatrix(conceptCount = 20, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptMatrix"), "Expected to get 'conceptMatrix'")
        matrix = res.get("conceptMatrix")
        self.assertTrue("sampleSize" in matrix, "Expecting 'sampleSize' property in conceptMatrix")
        self.assertTrue("freqMatrix" in matrix, "Expecting 'freqMatrix' property in conceptMatrix")
        self.assertTrue("concepts" in matrix, "Expecting 'concepts' property in conceptMatrix")
        self.assertEqual(len(matrix.get("concepts")), 20, "Expected 20 concepts")
        for concept in matrix.get("concepts"):
            self.ensureValidConcept(concept, "conceptMatrix")


    def test_SourceAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestEventsSourceAggr(sourceCount = 15, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("sourceAggr"), "Expected to get 'sourceAggr'")
        sources = res.get("sourceAggr",{}).get("results")
        self.assertEqual(len(sources), 15, "Expected 15 sources")
        for sourceInfo in sources:
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            self.assertIsNotNone(sourceInfo.get("counts").get("frequency"), "Counts should contain a frequency")
            self.assertIsNotNone(sourceInfo.get("counts").get("ratio"), "Counts should contain ratio")


    def testSearchBySource(self):
        q = QueryEvents()
        q.addNewsSource(self.er.getNewsSourceUri("bbc"))             # and have been reported by BBC
        q.addRequestedResult(RequestEventsUriList())            # return uris of all events
        q.addRequestedResult(RequestEventsInfo(page = 1, count = 100, sortBy = "size", sortByAsc = True,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(lang = "deu", type = "wiki"),
                eventInfo = EventInfoFlags(concepts = True, articleCounts = True, title = True, summary = True, categories = True, location = True, stories = True, imageCount = 1)
                )))   # return event details for first 100 events
        q.addRequestedResult(RequestEventsConceptAggr(conceptCount = 5,
            returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["org", "loc"]))))        # compute concept aggregate on the events
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "conceptAggr"), "Results should contain conceptAggr")
        self.assertTrue(hasattr(obj, "events"), "Results should contain events")
        self.assertTrue(hasattr(obj, "uriList"), "Results should contain uriList")

        concepts = obj.conceptAggr.results
        self.assertTrue(len(concepts) <= 10, "Received a list of concepts that is too long")
        for concept in concepts:
            self.assertTrue(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")

        lastArtCount = 0
        self.assertTrue(len(obj.events.results) <= 100, "Returned list of events was too long")

        for event in obj.events.results:
            self.assertTrue(hasattr(event, "articleCounts"), "Event should contain articleCounts")
            self.assertTrue(hasattr(event, "categories"), "Event should contain categories")
            self.assertTrue(hasattr(event, "concepts"), "Event should contain concepts")
            self.assertTrue(hasattr(event, "stories"), "Event should contain stories")
            self.assertTrue(hasattr(event, "title"), "Event should contain title")
            self.assertTrue(hasattr(event, "summary"), "Event should contain summary")
            self.assertTrue(hasattr(event, "images"), "Event should contain images")
            self.assertTrue(hasattr(event, "location"), "Event should contain location")

            #self.assertTrue(event.totalArticleCount >= lastArtCount, "Events were not sorted by increasing size")
            lastArtCount = event.totalArticleCount
            for concept in event.concepts:
                self.assertTrue(hasattr(concept.label, "deu"), "Concept should contain label in german language")
                self.assertTrue(concept.type == "wiki", "Got concept of invalid type")

    def testSearchByKeyword(self):
        q = QueryEvents()
        q.addKeyword("car")  # get events containing word car
        q.addRequestedResult(RequestEventsInfo(page = 1, count = 10, sortBy = "date", sortByAsc = False,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = "org"),
                eventInfo = EventInfoFlags(concepts = False, articleCounts = False, title = False, summary = False, categories = False, location = False, stories = False, imageCount = 0)
                )))
        q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 5,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = ["org", "loc"], lang = "spa"))))
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "events"), "Results should contain events")
        self.assertTrue(hasattr(obj, "conceptTrends"), "Results should contain conceptAggr")

        for concept in obj.conceptTrends.conceptInfo:
            self.assertTrue(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")
            self.assertTrue(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")

        lastEventDate = obj.events.results[0].eventDate if len(obj.events.results) > 0 else ""
        for event in obj.events.results:
            self.assertTrue(event.eventDate <= lastEventDate, "Events are not sorted by date")
            lastEventDate = event.eventDate
            self.assertFalse(hasattr(event, "articleCounts"), "Event should not contain articleCounts")
            self.assertFalse(hasattr(event, "categories"), "Event should not contain categories")
            self.assertFalse(hasattr(event, "concepts"), "Event should not contain concepts")
            self.assertFalse(hasattr(event, "location"), "Event should not contain location")
            self.assertFalse(hasattr(event, "stories"), "Event should not contain stories")
            self.assertFalse(hasattr(event, "images"), "Event should not contain images")
            self.assertFalse(hasattr(event, "title"), "Event should not contain title")
            self.assertFalse(hasattr(event, "summary"), "Event should not contain summary")

    def testSearchByLocation(self):
        q = QueryEvents()
        q.addLocation(self.er.getLocationUri("Washington"))
        q.addRequestedResult(RequestEventsConceptTrends(conceptCount = 40, returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = "person"))))
        q.addRequestedResult(RequestEventsCategoryAggr())
        q.addRequestedResult(RequestEventsInfo())
        res = self.er.execQuery(q)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEvents)
    unittest.TextTestRunner(verbosity=3).run(suite)