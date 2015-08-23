import unittest
from eventregistry import *


class TestQueryArticles(unittest.TestCase):
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
        q = QueryArticles()
        q.addConcept(self.er.getConceptUri("Obama"))
        return q

    def validateGeneralArticleList(self, res):
        self.assertIsNotNone(res.get("articles"), "Expected to get 'articles'")
        
        articles = res.get("articles").get("results")
        self.assertEquals(len(articles), 30, "Expected to get 30 articles")
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
        location = self.er.getLocationUri("germany")
        q = QueryArticles(locationUri = location)
        q.addRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
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
            self.assertTrue(trend.has_key("date"), "A trend should have a date")
            self.assertTrue(trend.has_key("conceptFreq"), "A trend should have a conceptFreq")
            self.assertTrue(trend.has_key("totArts"), "A trend should have a totArts property")
            self.assertTrue(len(trend.get("conceptFreq")), "Concept frequencies should contain 5 elements - one for each concept")
        for concept in res.get("conceptTrends").get("conceptInfo"):
            self.ensureValidConcept(concept, "conceptTrends")


    def testConceptAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesConceptAggr(conceptCount = 50, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptAggr"), "Expected to get 'conceptAggr'")
        self.assertEqual(len(res.get("conceptAggr")), 50, "Expected a different number of concept in conceptAggr")
        for concept in res.get("conceptAggr"):
            self.ensureValidConcept(concept, "conceptAggr")


    def testKeywordAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesKeywordAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("keywordAggr"), "Expected to get 'keywordAggr'")
        keywords = res.get("keywordAggr")
        self.assertTrue(len(keywords) > 0, "Expected to get some keywords")
        for kw in keywords:
            self.assertTrue(kw.has_key("keyword"), "Expected a keyword property")
            self.assertTrue(kw.has_key("weight"), "Expected a weight property")


    def testCategoryAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesCategoryAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("categoryAggr"), "Expected to get 'categoryAggr'")
        categories = res.get("categoryAggr")
        self.assertTrue(len(categories) > 0, "Expected to get a non empty category aggr")
        for cat in categories:
            self.ensureValidCategory(cat, "categoryAggr")


    def testConceptMatrix(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesConceptMatrix(count = 20, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        
        self.assertIsNotNone(res.get("conceptMatrix"), "Expected to get 'conceptMatrix'")
        matrix = res.get("conceptMatrix")
        self.assertTrue(matrix.has_key("sampleSize"), "Expecting 'sampleSize' property in conceptMatrix")
        self.assertTrue(matrix.has_key("freqMatrix"), "Expecting 'freqMatrix' property in conceptMatrix")
        self.assertTrue(matrix.has_key("concepts"), "Expecting 'concepts' property in conceptMatrix")
        self.assertEquals(len(matrix.get("concepts")), 20, "Expected 20 concepts")
        for concept in matrix.get("concepts"):
            self.ensureValidConcept(concept, "conceptMatrix")


    def testSourceAggr(self):
        q = self.createQuery()
        q.addRequestedResult(RequestArticlesSourceAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        
        self.assertIsNotNone(res.get("sourceAggr"), "Expected to get 'sourceAggr'")
        for sourceInfo in res.get("sourceAggr"):
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            for count in sourceInfo.get("counts"):
                self.assertIsNotNone(count.get("date"), "Counts should contain a date")
                self.assertIsNotNone(count.get("count"), "Counts should contain a count")
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticles)
    unittest.TextTestRunner(verbosity=3).run(suite)