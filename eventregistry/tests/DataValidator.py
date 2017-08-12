import unittest, jmespath
from eventregistry import *

class DataValidator(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # load settings from the current folder. use different instance than for regular ER requests
        currPath = os.path.split(__file__)[0]
        settPath = os.path.join(currPath, "settings.json")
        self.er = EventRegistry(verboseOutput = True, settingsFName = settPath)


    def __init__(self, *args, **kwargs):
        super(DataValidator, self).__init__(*args, **kwargs)

        self.articleInfo = ArticleInfoFlags(bodyLen = -1, concepts = True, storyUri = True, duplicateList = True, originalArticle = True, categories = True,
                videos = True, image = True, location = True, extractedDates = True, socialScore = True, details = True)
        self.sourceInfo = SourceInfoFlags(description = True, location = True, ranking = True, articleCount = True, sourceGroups = True, details = True)
        self.conceptInfo = ConceptInfoFlags(type=["entities"], lang = ["eng", "spa"], synonyms = True, image = True, description = True, details = True,
                conceptClassMembership = True, trendingScore = True, trendingHistory = True, maxConceptsPerType = 50)
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
        for prop in ["id", "uri", "label", "synonyms", "image", "details", "trendingScore"]:
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


    def ensureValidSource(self, source, testName):
        for prop in ["id", "uri", "location", "ranking", "articleCount", "sourceGroups", "details"]:
            self.assertTrue(prop in source, "Property '%s' was expected in source for test %s" % (prop, testName))


    def ensureValidCategory(self, category, testName):
        for prop in ["id", "uri", "parentUri", "trendingScore"]:
            self.assertTrue(prop in category, "Property '%s' was expected in source for test %s" % (prop, testName))


    def ensureValidLocation(self, location, testName):
        for prop in ["wikiUri", "label", "lat", "long", "geoNamesId", "population"]:
            self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "country":
            for prop in ["area", "code2", "code3", "webExt", "continent"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "place":
            for prop in ["featureCode", "country"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))


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


    def ensureArticleBodyContainsText(self, article, text):
        self.assertTrue("body" in article, "Article did not contain body")
        self.assertTrue(re.search("(^|\s)" + text + "($|'|\s)", article["body"], re.IGNORECASE) != None, "Article body did not contain text '%s'" % (text))


    def ensureArticleBodyDoesNotContainText(self, article, text):
        if "body" in article:
            if re.search("(^|\s)" + text + "($|'|\s)", article["body"], re.IGNORECASE) != None:
                self.fail("Article body contained text '%s' and it shouldn't" % (text))


    def ensureArticleHasConcept(self, article, conceptUri):
        self.assertTrue("concepts" in article, "Article did not contain concept array")
        for concept in article["concepts"]:
            if conceptUri == concept["uri"]:
                return
        self.fail("Article concepts did not contain concept '%s'" % (conceptUri))


    def ensureArticleHasNotConcept(self, article, conceptUri):
        if "concepts" in article:
            for concept in article["concepts"]:
                if conceptUri == concept["uri"]:
                    self.fail("Article concepts contained concept '%s'" % (conceptUri))


    def ensureArticleHasCategory(self, article, categoryUri):
        """
        ensure that the article has the given category or ANY child category
        """
        self.assertTrue("categories" in article, "Article did not contain category array")
        for category in article["categories"]:
            if category["uri"].find(categoryUri) == 0:
                return
        self.fail("Article categories did not contain category '%s'" % (categoryUri))


    def ensureArticleHasNotCategory(self, article, categoryUri):
        """
        ensure that the article does not have the given category or ANY child category
        """
        for category in article["categories"]:
            if category["uri"].find(categoryUri) != -1:
                self.fail("Article categories contained an incorrect category '%s'" % (categoryUri))


    def ensureArticleSource(self, article, sourceUri):
        self.assertTrue(article.get("source").get("uri") == sourceUri, "Article source is not '%s'" % sourceUri)


    def ensureArticleNotFromSource(self, article, sourceUri):
        self.assertFalse(article.get("source").get("uri") == sourceUri, "Article source is not '%s'" % sourceUri)


    def ensureArticlesContainText(self, articles, keyword):
        """assure that at least one article contains the given keyword"""
        hasKw = [True for art in articles if keyword.lower() in art["body"].lower()]
        self.assertTrue(len(hasKw) > 0, "None of the articles contained given keyword '%s'" % keyword)


    def ensureArticlesDoNotContainText(self, articles, keyword):
        """assure that at least one article contains the given keyword"""
        for article in articles:
            self.ensureArticleBodyDoesNotContainText(article, keyword)


    def ensureArticlesNotFromSource(self, articles, sourceUri):
        """assure that none of the articles are from the given source"""
        for article in articles:
            self.ensureArticleNotFromSource(article, sourceUri)


    def ensureEventHasConcept(self, event, conceptUri):
        self.assertTrue("concepts" in event, "Event did not contain concept array")
        for concept in event["concepts"]:
            if conceptUri == concept["uri"]:
                return
        self.fail("Event concepts did not contain concept '%s'" % (conceptUri))


    def ensureEventHasNotConcept(self, event, conceptUri):
        if "concepts" in event:
            for concept in event["concepts"]:
                if conceptUri == concept["uri"]:
                    self.fail("Event concepts contained concept '%s'" % (conceptUri))


    def ensureEventHasCategory(self, event, categoryUri):
        """
        ensure that the event has the given category or ANY child category
        """
        self.assertTrue("categories" in event, "Event did not contain category array")
        for category in event["categories"]:
            if category["uri"].find(categoryUri) == 0:
                return
        self.fail("Event categories did not contain category '%s'" % (categoryUri))


    def ensureEventHasNotCategory(self, event, categoryUri):
        """
        ensure that the event does not have the given category or ANY child category
        """
        for category in event["categories"]:
            if category["uri"].find(categoryUri) != -1:
                self.fail("Event categories contained an incorrect category '%s'" % (categoryUri))


    def ensureSameResults(self, res1, res2, queryStr):
        arr1 = jmespath.compile(queryStr).search(res1)
        arr2 = jmespath.compile(queryStr).search(res2)
        if not isinstance(arr1, list) or not isinstance(arr2, list):
            return
        if arr1 != [] and arr2 != []:
            if arr1[0] != arr2[0]:
                self.fail("Found different results for query %s" % (queryStr))
        elif len(arr1) != len(arr2):
            self.fail("Found different number of results for query %s" % (queryStr))

