import unittest
from eventregistry import *
from DataValidator import DataValidator

class TestQueryArticles(DataValidator):

    def createQuery(self):
        q = QueryArticles(conceptUri = self.er.getConceptUri("Obama"))
        return q


    def validateGeneralArticleList(self, res):
        self.assertIsNotNone(res.get("articles"), "Expected to get 'articles'")

        articles = res.get("articles").get("results")
        self.assertEqual(len(articles), 30, "Expected to get 30 articles")
        for article in articles:
            self.ensureValidArticle(article, "articleList")


    def testArticleList(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)

    #
    # test different search query params
    #

    def testArticleListWithKeywordSearch(self):
        q = QueryArticles(keywords = "iphone")
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)

        q2 = QueryArticles(keywords = "iphone")
        q2.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res2)

        self.ensureSameResults(res, res2, '[articles][].totalResults')


    def testArticleListWithKeywordTitleSearch(self):
        """make sure search in title works"""
        q = QueryArticlesIter(keywords = "iphone", keywordsLoc = "title")
        for art in q.execQuery(self.er):
            self.assertTrue(art["title"].lower().find("iphone") >= 0)


    def testArticleListWithKeywordTitleSearch(self):
        """make sure search in title works"""
        q = QueryArticlesIter(keywords = "home", keywordsLoc = "title")
        for art in q.execQuery(self.er):
            self.assertTrue(art["title"].lower().find("home") >= 0)


    def testArticleListWithKeywordBodySearch(self):
        """make sure search in body works"""
        q = QueryArticlesIter(keywords = "home", keywordsLoc = "body")
        for art in q.execQuery(self.er):
            self.assertTrue(art["body"].lower().find("home") >= 0)


    def testArticleListWithKeywordBodySearch(self):
        """make sure search in body works"""
        q = QueryArticlesIter(keywords = "jack", keywordsLoc = "body")
        for art in q.execQuery(self.er):
            self.assertTrue(art["body"].lower().find("jack") >= 0)


    def testArticleListWithPublisherSearch(self):
        bbcUri = self.er.getNewsSourceUri("bbc")
        q = QueryArticles(sourceUri = bbcUri)
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)
        for article in res.get("articles").get("results"):
            self.assertTrue(article["source"]["uri"] == bbcUri, "article is not from bbc")

        q2 = QueryArticles(sourceUri = bbcUri)
        q2.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res2)

        self.ensureSameResults(res, res2, '[articles][].totalResults')


    def testArticleListWithCategorySearch(self):
        disasterUri = self.er.getCategoryUri("disa")
        q = QueryArticles(categoryUri = disasterUri)
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)

        q2 = QueryArticles(categoryUri = disasterUri)
        q2.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res)

        self.ensureSameResults(res, res2, '[articles][].totalResults')


    def testArticleListWithLangSearch(self):
        q = QueryArticles(lang = "deu")
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)
        for article in res.get("articles").get("results"):
            self.assertTrue(article["lang"] == "deu", "article is not in deu")


    def testArticleListWithLocationSearch(self):
        location = self.er.getLocationUri("united")
        q = QueryArticles(locationUri = location)
        q.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        if "error" in res:
            return
        self.validateGeneralArticleList(res)

        q2 = QueryArticles(locationUri = location)
        q2.setRequestedResult(RequestArticlesInfo(count = 30,  returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res2)

        self.ensureSameResults(res, res2, '[articles][].totalResults')


    def testEventListWithCombinedSearch1(self):
        q = QueryArticles(keywords="germany", lang = ["eng", "deu"], conceptUri = [self.er.getConceptUri("Merkel")], categoryUri = self.er.getCategoryUri("Business"))
        q.setRequestedResult(RequestArticlesInfo(count = 30, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)

        q2 = QueryArticles(
            keywords="germany",
            lang = ["eng", "deu"],
            conceptUri = self.er.getConceptUri("Merkel"),
            categoryUri = self.er.getCategoryUri("Business"))
        q2.setRequestedResult(RequestArticlesInfo(count = 30, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res2)

        self.ensureSameResults(res, res2, '[articles][].totalResults')

    #
    # test different return types
    #

    def testConceptTrends(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticlesConceptTrends(count = 5, returnInfo = self.returnInfo))
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
        q.setRequestedResult(RequestArticlesConceptAggr(conceptCount = 50, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptAggr"), "Expected to get 'conceptAggr'")
        concepts = res.get("conceptAggr").get("results")
        self.assertEqual(len(concepts), 50, "Expected a different number of concept in conceptAggr")
        for concept in concepts:
            self.ensureValidConcept(concept, "conceptAggr")


    def testKeywordAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticlesKeywordAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("keywordAggr"), "Expected to get 'keywordAggr'")
        keywords = res.get("keywordAggr").get("results", [])
        self.assertTrue(len(keywords) > 0, "Expected to get some keywords")
        for kw in keywords:
            self.assertTrue("keyword" in kw, "Expected a keyword property")
            self.assertTrue("weight" in kw, "Expected a weight property")


    def testCategoryAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticlesCategoryAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("categoryAggr"), "Expected to get 'categoryAggr'")
        categories = res.get("categoryAggr").get("results")
        self.assertTrue(len(categories) > 0, "Expected to get a non empty category aggr")
        for cat in categories:
            self.ensureValidCategory(cat, "categoryAggr")


    def testConceptMatrix(self):
        q = self.createQuery()
        q.setRequestedResult(RequestArticlesConceptMatrix(conceptCount = 20, returnInfo = self.returnInfo))
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
        q.setRequestedResult(RequestArticlesSourceAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("sourceAggr"), "Expected to get 'sourceAggr'")
        for sourceInfo in res.get("sourceAggr").get("results"):
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")
            counts = sourceInfo.get("counts")
            self.assertIsNotNone(counts.get("frequency"), "Counts should contain a frequency")
            self.assertIsNotNone(counts.get("ratio"), "Counts should contain a ratio")

    #
    # tests for iterators
    #

    def testQueryArticlesIterator(self):
        # check that the iterator really downloads all articles
        iter = QueryArticlesIter(keywords = "trump", conceptUri = self.er.getConceptUri("Obama"), sourceUri = self.er.getNewsSourceUri("los angeles times"))
        articleCount = iter.count(self.er)
        articles = list(iter.execQuery(self.er, returnInfo = self.returnInfo))
        self.assertTrue(articleCount == len(articles), "Article iterator did not generate the full list of aticles")


    def testQuery1(self):
        obamaUri = self.er.getConceptUri("Obama")
        LAsourceUri = self.er.getNewsSourceUri("los angeles times")
        iter = QueryArticlesIter(keywords = "trump", conceptUri = obamaUri, sourceUri = LAsourceUri)
        for article in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 500):
            self.ensureArticleHasConcept(article, obamaUri)
            self.ensureArticleSource(article, LAsourceUri)
            self.ensureArticleBodyContainsText(article, "trump")


    def testQuery2(self):
        obamaUri = self.er.getConceptUri("Obama")
        LAsourceUri = self.er.getNewsSourceUri("los angeles times")
        businessCatUri = self.er.getCategoryUri("business")
        iter = QueryArticlesIter(conceptUri = obamaUri, sourceUri = LAsourceUri, categoryUri = businessCatUri)
        for article in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 500):
            self.ensureArticleHasCategory(article, businessCatUri)
            self.ensureArticleSource(article, LAsourceUri)
            self.ensureArticleHasConcept(article, obamaUri)


    def testQuery3(self):
        """query with several negative conditions"""
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getConceptUri("politics")
        chinaUri = self.er.getConceptUri("china")
        unitedStatesUri = self.er.getConceptUri("united states")

        srcDailyCallerUri = self.er.getNewsSourceUri("daily caller")
        srcAawsatUri = self.er.getNewsSourceUri("aawsat")
        srcSvodkaUri = self.er.getNewsSourceUri("svodka")

        catBusinessUri = self.er.getCategoryUri("business")
        catPoliticsUri = self.er.getCategoryUri("politics")
        iter = QueryArticlesIter(conceptUri = obamaUri,
                                 ignoreConceptUri = [politicsUri, chinaUri, unitedStatesUri],
                                 ignoreKeywords=["trump", "politics", "michelle"],
                                 ignoreSourceUri = [srcDailyCallerUri, srcAawsatUri, srcSvodkaUri],
                                 ignoreCategoryUri = [catBusinessUri, catPoliticsUri])
        for article in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 500):
            self.ensureArticleHasConcept(article, obamaUri)
            self.ensureArticleHasNotConcept(article, politicsUri)
            self.ensureArticleHasNotConcept(article, chinaUri)
            self.ensureArticleHasNotConcept(article, unitedStatesUri)

            self.ensureArticleBodyDoesNotContainText(article, "trump")
            self.ensureArticleBodyDoesNotContainText(article, "politics")
            self.ensureArticleBodyDoesNotContainText(article, "michelle")

            self.ensureArticleNotFromSource(article, srcDailyCallerUri)
            self.ensureArticleNotFromSource(article, srcAawsatUri)
            self.ensureArticleNotFromSource(article, srcSvodkaUri)

            self.ensureArticleHasNotCategory(article, catBusinessUri)
            self.ensureArticleHasNotCategory(article, catPoliticsUri)



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticles)
    unittest.TextTestRunner(verbosity=3).run(suite)
