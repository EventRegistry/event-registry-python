import unittest
from eventregistry import *


class TestQueryArticles(unittest.TestCase):
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
        self.returnInfo = ReturnInfo(articleInfo = self.articleInfo, conceptInfo = self.conceptInfo,
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

    def ensureValidSource(self, source, testName):
        for prop in ["id", "uri", "location", "importance", "articleCount", "tags", "details"]:
            self.assertTrue(prop in source, "Property '%s' was expected in source for test %s" % (prop, testName))

    def ensureValidCategory(self, category, testName):
        for prop in ["id", "uri", "parentUri", "childrenUris", "trendingScore", "trendingHistory"]:
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

    def createQuery(self):
        q = QueryArticles()
        q.addConcept(self.er.getConceptUri("Obama"))
        return q

    def validateGeneralArticleList(self, res):
        self.assertIsNotNone(res.get("articles"), "Expected to get 'articles'")

        articles = res.get("articles").get("results")
        self.assertEqual(len(articles), 30, "Expected to get 30 articles")
        for article in articles:
            self.ensureValidArticle(article, "articleList")

    def testArticleList(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)


    def testArticleListWithKeywordSearch(self):
        q = QueryArticles(keywords = "iphone")
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)


    def testArticleListWithPublisherSearch(self):
        bbcUri = self.er.getNewsSourceUri("bbc")
        q = QueryArticles(sourceUri = bbcUri)
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)


    def testArticleListWithCategorySearch(self):
        disasterUri = self.er.getCategoryUri("disa")
        q = QueryArticles(categoryUri = disasterUri)
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)


    def testArticleListWithLangSearch(self):
        q = QueryArticles(lang = "deu")
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)


    def testArticleListWithLocationSearch(self):
        location = self.er.getLocationUri("united")
        q = QueryArticles(locationUri = location)
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        if "error" in res:
            return
        self.validateGeneralArticleList(res)


    def testConceptTrends(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesConceptTrends(count = 5, returnInfo = self.returnInfo))
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
        q.addRequestedResult(RequestArticlesConceptAggr(conceptCount = 50, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptAggr"), "Expected to get 'conceptAggr'")
        concepts = res.get("conceptAggr").get("results")
        self.assertEqual(len(concepts), 50, "Expected a different number of concept in conceptAggr")
        for concept in concepts:
            self.ensureValidConcept(concept, "conceptAggr")


    def testKeywordAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesKeywordAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("keywordAggr"), "Expected to get 'keywordAggr'")
        keywords = res.get("keywordAggr").get("results", [])
        self.assertTrue(len(keywords) > 0, "Expected to get some keywords")
        for kw in keywords:
            self.assertTrue("keyword" in kw, "Expected a keyword property")
            self.assertTrue("weight" in kw, "Expected a weight property")


    def testCategoryAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesCategoryAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("categoryAggr"), "Expected to get 'categoryAggr'")
        categories = res.get("categoryAggr").get("results")
        self.assertTrue(len(categories) > 0, "Expected to get a non empty category aggr")
        for cat in categories:
            self.ensureValidCategory(cat, "categoryAggr")


    def testConceptMatrix(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesConceptMatrix(conceptCount = 20, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptMatrix"), "Expected to get 'conceptMatrix'")
        matrix = res.get("conceptMatrix")
        self.assertTrue("sampleSize" in matrix, "Expecting 'sampleSize' property in conceptMatrix")
        self.assertTrue("freqMatrix" in matrix, "Expecting 'freqMatrix' property in conceptMatrix")
        self.assertTrue("concepts" in matrix, "Expecting 'concepts' property in conceptMatrix")
        self.assertEqual(len(matrix.get("concepts")), 20, "Expected 20 concepts")
        for concept in matrix.get("concepts"):
            self.ensureValidConcept(concept, "conceptMatrix")


    def testSourceAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesSourceAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("sourceAggr"), "Expected to get 'sourceAggr'")
        for sourceInfo in res.get("sourceAggr").get("results"):
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")
            counts = sourceInfo.get("counts")
            self.assertIsNotNone(counts.get("frequency"), "Counts should contain a frequency")
            self.assertIsNotNone(counts.get("ratio"), "Counts should contain a ratio")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticles)
    unittest.TextTestRunner(verbosity=3).run(suite)