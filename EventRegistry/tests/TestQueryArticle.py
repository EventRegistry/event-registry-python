import unittest
from eventregistry import *


class TestQueryArticle(unittest.TestCase):

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
        q = QueryArticle.queryById(list(range(1000, 1010)))
        return q

    def testArticleList(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertEqual(len(res), 10, "Expected to get a list of 10 articles")
        for article in list(res.values()):
            self.ensureValidArticle(article["info"], "articleList")

        uris = [article.get("info").get("uri") for article in list(res.values())]
        urls = [article.get("info").get("url") for article in list(res.values())]

        mapper = ArticleMapper(self.er)
        mappedUris = [mapper.getArticleUri(url) for url in urls]
        q = QueryArticle.queryByUri(mappedUris)
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected to get a list of 10 articles when searching by urls")
        for article in list(res.values()):
            self.ensureValidArticle(article["info"], "articleList")

        q = QueryArticle.queryByUri(uris)
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.assertEqual(len(res), 10, "Expected to get a list of 10 articles when searching by uris")
        for article in list(res.values()):
            self.ensureValidArticle(article["info"], "articleList")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticle)
    unittest.TextTestRunner(verbosity=3).run(suite)