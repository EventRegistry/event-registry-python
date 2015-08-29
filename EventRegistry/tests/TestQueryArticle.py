import unittest
from eventregistry import *


class TestQueryArticle(unittest.TestCase):
    
    def setUp(self):
        self.er = EventRegistry()
        self.articleInfo = ArticleInfoFlags(bodyLen = -1, concepts = True, storyUri = True, duplicateList = True, originalArticle = True, categories = True,
                location = True, image = True, extractedDates = True, socialScore = True, details = True)
        self.sourceInfo = SourceInfoFlags(description = True, location = True, importance = True, articleCount = True, tags = True, details = True)
        self.conceptInfo = ConceptInfoFlags(type=["entities"], lang = "spa", synonyms = True, image = True, description = True, details = True, 
                conceptClassMembership = True, conceptFolderMembership = True, trendingScore = True, trendingHistory = True)
        self.locationInfo = LocationInfoFlags(wikiUri = True, label = True, geoLocation = True, population = True, countryArea = True, placeFeatureCode = True, placeCountry = True)
        self.categoryInfo = CategoryInfoFlags(parentUri = True, childrenUris = True, trendingScore = True, trendingHistory = True)
        self.returnInfo = ReturnInfo(articleInfo = self.articleInfo, conceptInfo = self.conceptInfo,
            sourceInfo = self.sourceInfo, locationInfo = self.locationInfo, categoryInfo = self.categoryInfo)

    def ensureValidConcept(self, concept, testName):
        for prop in ["id", "uri", "label", "synonyms", "image", "description", "details", "conceptClassMembership", "conceptFolderMembership", "trendingScore", "trendingHistory", "details"]:
            self.assertTrue(concept.has_key(prop), "Property '%s' was expected in concept for test %s" % (prop, testName))
        self.assertTrue(concept.get("type") in ["person", "loc", "org"], "Expected concept to be an entity type, but got %s" % (concept.get("type")))

    def ensureValidArticle(self, article, testName):
        for prop in ["id", "url", "uri", "title", "body", "source", "details", "location", "duplicateList", "originalArticle", "time", "date", "categories", "lang", "extractedDates", "concepts", "details"]:
            self.assertTrue(article.has_key(prop), "Property '%s' was expected in article for test %s" % (prop, testName))
        for concept in article.get("concepts"):
            self.ensureValidConcept(concept, testName)
        self.assertTrue(article.get("isDuplicate") or article.has_key("eventUri"), "Nonduplicates should have event uris")

    def ensureValidSource(self, source, testName):
        for prop in ["id", "uri", "location", "importance", "articleCount", "tags", "details"]:
            self.assertTrue(source.has_key(prop), "Property '%s' was expected in source for test %s" % (prop, testName))

    def ensureValidCategory(self, category, testName):
        for prop in ["id", "uri", "parentUri", "childrenUris", "trendingScore", "trendingHistory"]:
            self.assertTrue(category.has_key(prop), "Property '%s' was expected in source for test %s" % (prop, testName))

    def createQuery(self):
        q = QueryArticle.queryById(range(1000, 1010))
        return q

    def testArticleList(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertEquals(len(res), 10, "Expected to get a list of 10 articles")
        for article in res.values():
            self.ensureValidArticle(article["info"], "articleList")

        uris = [article.get("info").get("uri") for article in res.values()]
        urls = [article.get("info").get("url") for article in res.values()]

        q = QueryArticle.queryByUrl(urls)
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.assertEquals(len(res), 10, "Expected to get a list of 10 articles when searching by urls")
        for article in res.values():
            self.ensureValidArticle(article["info"], "articleList")

        q = QueryArticle.queryByUri(uris)
        q.addRequestedResult(RequestArticleInfo(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.assertEquals(len(res), 10, "Expected to get a list of 10 articles when searching by uris")
        for article in res.values():
            self.ensureValidArticle(article["info"], "articleList")

    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticle)
    unittest.TextTestRunner(verbosity=3).run(suite)