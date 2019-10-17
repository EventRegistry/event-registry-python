import unittest, math
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryArticles(DataValidator):

    def createQuery(self):
        conceptUri = self.er.getConceptUri("Obama")
        self.assertTrue(conceptUri != None)
        q = QueryArticles(conceptUri = conceptUri)
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


    def testArticleUriWgtList(self):
        conceptUri = self.er.getConceptUri("germany")
        self.assertTrue(conceptUri != None)
        iter = QueryArticlesIter(conceptUri=conceptUri)
        expectedCount = iter.count(self.er)

        countPerPage = 20000
        pages = int(math.ceil(expectedCount / float(countPerPage)))
        conceptUri = self.er.getConceptUri("germany")
        self.assertTrue(conceptUri != None)
        q = QueryArticles(conceptUri=conceptUri)
        items = []
        for page in range(1, pages+1):
            q.setRequestedResult(RequestArticlesUriWgtList(page = page, count = countPerPage))
            res = self.er.execQuery(q)
            items.extend(res.get("uriWgtList", {}).get("results", []))
        if expectedCount != len(items):
            self.fail("We did not retrieve all item uris. We were expecting %d, but got %d uris on %d pages" %(expectedCount, len(items), pages))

        lastWgt = None
        for item in items:
            wgt = int(item.split(":")[1])
            if lastWgt == None: lastWgt = wgt
            else:
                assert lastWgt >= wgt
                lastWgt = wgt

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
        for art in q.execQuery(self.er, maxItems = 1000):
            title = self.removeAccents(art["title"]).lower()
            if title.find("iphone") < 0:
                print(art["body"])
            self.assertTrue(title.find("iphone") >= 0)


    def testArticleListWithKeywordTitleSearch2(self):
        """make sure search in title works"""
        q = QueryArticlesIter(keywords = "home", keywordsLoc = "title")
        for art in q.execQuery(self.er, maxItems = 1000):
            title = self.removeAccents(art["title"]).lower()
            self.assertTrue(title.find("home") >= 0)


    def testArticleListWithKeywordBodySearch(self):
        """make sure search in body works"""
        q = QueryArticlesIter(keywords = "home", keywordsLoc = "body")
        for art in q.execQuery(self.er, maxItems = 1000):
            body = self.removeAccents(art["body"]).lower()
            if body.find("home") < 0:
                print(art["body"])
            self.assertTrue(body.find("home") >= 0)


    def testArticleListWithKeywordBodySearch2(self):
        """make sure search in body works"""
        q = QueryArticlesIter(keywords = "jack", keywordsLoc = "body")
        for art in q.execQuery(self.er, maxItems = 1000):
            body = self.removeAccents(art["body"]).lower()
            if body.find("jack") < 0:
                print(art["body"])
            self.assertTrue(body.find("jack") >= 0)


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


    def testArticleListWithSourceGroupSearch(self):
        top10Uri = self.er.getSourceGroupUri("general 10")
        bbcUri = self.er.getNewsSourceUri("bbc")
        bloombergUri = self.er.getNewsSourceUri("bloomberg")
        groupSourceInfo = self.er.getSourceGroup(top10Uri)
        groupSourceUris = [src.get("uri") for src in groupSourceInfo.get(top10Uri).get("sources")]
        groupSourceUriSet = set(groupSourceUris)
        groupSourceUriSet.add(bloombergUri)

        q = QueryArticlesIter(sourceUri = bbcUri, sourceGroupUri = top10Uri)
        for art in q.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 1000):
            self.ensureValidArticle(art, "sourceGroupSearch")
            self.assertTrue(art.get("source").get("uri") == bbcUri)

        seenSourceUris = set()
        cq = ComplexArticleQuery(CombinedQuery.OR([
                BaseQuery(sourceUri = bloombergUri),
                BaseQuery(sourceGroupUri = top10Uri)
            ]))
        q = QueryArticlesIter.initWithComplexQuery(cq)
        for art in q.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 1000):
            self.ensureValidArticle(art, "sourceGroupSearch")
            self.assertTrue(art.get("source").get("uri") in groupSourceUriSet)
            seenSourceUris.add(art.get("source").get("uri"))
        # we should have results from multiple sources
        self.assertTrue(len(seenSourceUris) > 1)


    def testArticleListWithSourceGroupAndLocationSearch(self):
        top10Uri = self.er.getSourceGroupUri("general 10")
        usUri = self.er.getLocationUri("United states")
        groupSourceInfo = self.er.getSourceGroup(top10Uri)
        groupSourceUris = [src.get("uri") for src in groupSourceInfo.get(top10Uri).get("sources")]
        groupSourceUriSet = set(groupSourceUris)

        q = QueryArticlesIter(sourceLocationUri = usUri, sourceGroupUri = top10Uri)
        for art in q.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 1000):
            self.ensureValidArticle(art, "sourceGroupLocationSearch")
            self.assertTrue(art.get("source").get("uri") in groupSourceUriSet)
            loc = art.get("source").get("location")
            if loc.get("type") == "country":
                self.assertTrue(loc.get("wikiUri") == usUri)
            else:
                self.assertTrue(loc.get("country").get("wikiUri") == usUri)

        cq = ComplexArticleQuery(CombinedQuery.AND([
                BaseQuery(sourceLocationUri = usUri),
                BaseQuery(sourceGroupUri = top10Uri)
            ]))
        q = QueryArticlesIter.initWithComplexQuery(cq)
        for art in q.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 1000):
            self.ensureValidArticle(art, "sourceGroupLocationSearch")
            self.assertTrue(art.get("source").get("uri") in groupSourceUriSet)
            if loc.get("type") == "country":
                self.assertTrue(loc.get("wikiUri") == usUri)
            else:
                self.assertTrue(loc.get("country").get("wikiUri") == usUri)


    def testArticleListWithAuthorSearch(self):
        """
        make sure that search for author returns articles by that author
        """
        authorUri = self.er.getAuthorUri("associated")
        q = QueryArticles(authorUri = authorUri)
        q.setRequestedResult(RequestArticlesInfo(count = 100, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        for art in res.get("articles", {}).get("results", []):
            foundAuthor = False
            for author in art.get("authors"):
                if author["uri"] == authorUri:
                    foundAuthor = True
            assert foundAuthor == True

        cq = ComplexArticleQuery(BaseQuery(authorUri = authorUri))
        q = QueryArticles.initWithComplexQuery(cq)
        q.setRequestedResult(RequestArticlesInfo(count = 100, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q)

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
        merkelUri = self.er.getConceptUri("Merkel")
        businessUri = self.er.getCategoryUri("business")
        self.assertTrue(merkelUri != None)
        self.assertTrue(businessUri != None)
        q = QueryArticles(keywords="germany", lang = ["eng", "deu"], conceptUri = [merkelUri], categoryUri = businessUri)
        q.setRequestedResult(RequestArticlesInfo(count = 30, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralArticleList(res)

        q2 = QueryArticles(
            keywords="germany",
            lang = ["eng", "deu"],
            conceptUri = merkelUri,
            categoryUri = businessUri)
        q2.setRequestedResult(RequestArticlesInfo(count = 30, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralArticleList(res2)

        self.ensureSameResults(res, res2, '[articles][].totalResults')

    #
    # test different return types
    #

    def testConceptTrends(self):
        q = self.createQuery()
        obamaUri = self.er.getConceptUri("obama")
        trumpUri = self.er.getConceptUri("trump")
        q.setRequestedResult(RequestArticlesConceptTrends(
            conceptUris = [obamaUri, trumpUri],
            returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptTrends"), "Expected to get 'conceptTrends'")
        self.assertIsNotNone(res.get("conceptTrends").get("trends"), "Expected to get 'trends' property in conceptTrends")
        self.assertIsNotNone(res.get("conceptTrends").get("conceptInfo"), "Expected to get 'conceptInfo' property in conceptTrends")
        self.assertTrue(len(res["conceptTrends"]["conceptInfo"]) == 2, "Expected to get 2 concepts in concept trends but got %d" % (len(res["conceptTrends"]["conceptInfo"])))
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
        q.setRequestedResult(RequestArticlesKeywordAggr(articlesSampleSize=100))
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
        for sourceInfo in res.get("sourceAggr").get("countsPerSource"):
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")
            counts = sourceInfo.get("counts")
            self.assertIsNotNone(counts.get("frequency"), "Counts should contain a frequency")
            self.assertIsNotNone(counts.get("total"), "Counts should contain a total")

        countries = res.get("sourceAggr", {}).get("countsPerCountry")
        for country in countries:
            self.assertTrue(country.get("type") == "loc", "Country should be a location")
            self.assertTrue(country.get("frequency") > 0)

    #
    # tests for iterators
    #

    def testQueryArticlesIterator(self):
        # check that the iterator really downloads all articles
        iter = QueryArticlesIter(keywords = "trump", conceptUri = self.er.getConceptUri("Obama"), sourceUri = self.er.getNewsSourceUri("los angeles times"))
        articleCount = iter.count(self.er)
        articles = list(iter.execQuery(self.er, returnInfo = self.returnInfo))
        if articleCount != len(articles):
            self.fail("Article iterator did not generate the full list of articles. Expected %d, but got %d items" % (articleCount, len(articles) ))


    def testQueryArticlesIterator2(self):
        """
        test if we can get non-first page of results
        """
        q = QueryArticles(keywords="Trump")
        q.setRequestedResult(RequestArticlesUriWgtList(page=2, count=100))
        res = self.er.execQuery(q)
        if len(res.get("uriWgtList", {}).get("results", [])) == 0:
            self.fail("No results were obtained for second page of uris")


    def testQuery1(self):
        obamaUri = self.er.getConceptUri("Obama")
        LAsourceUri = self.er.getNewsSourceUri("latimes")
        self.assertTrue(obamaUri != None)
        self.assertTrue(LAsourceUri != None)
        iter = QueryArticlesIter(keywords = "trump", conceptUri = obamaUri, sourceUri = LAsourceUri)
        for article in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 500):
            self.ensureArticleHasConcept(article, obamaUri)
            self.ensureArticleSource(article, LAsourceUri)
            self.ensureArticleBodyContainsText(article, "trump")


    def testQuery2(self):
        obamaUri = self.er.getConceptUri("Obama")
        LAsourceUri = self.er.getNewsSourceUri("latimes")
        businessCatUri = self.er.getCategoryUri("business")
        self.assertTrue(obamaUri != None)
        self.assertTrue(LAsourceUri != None)
        self.assertTrue(businessCatUri != None)
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

        self.assertTrue(obamaUri != None)
        self.assertTrue(politicsUri != None)
        self.assertTrue(chinaUri != None)
        self.assertTrue(unitedStatesUri != None)
        self.assertTrue(srcDailyCallerUri != None)
        self.assertTrue(srcAawsatUri != None)
        self.assertTrue(srcSvodkaUri != None)

        catBusinessUri = self.er.getCategoryUri("business")
        catPoliticsUri = self.er.getCategoryUri("politics")
        iter = QueryArticlesIter(conceptUri = obamaUri,
                                 ignoreConceptUri = [politicsUri, chinaUri, unitedStatesUri],
                                 ignoreKeywords=["trump", "politics", "michelle"],
                                 ignoreLang = "zho",
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


    #
    # test if we download all content
    #
    def testGetAllArticlesCount(self):
        returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(body = 0))
        unitedStatesUri = self.er.getConceptUri("united states")
        self.assertTrue(unitedStatesUri != None)
        iter = QueryArticlesIter(conceptUri=unitedStatesUri, lang="eng", dataType=["news", "blog"])

        total = iter.count(self.er)
        uniqueUris = set()
        for article in iter.execQuery(self.er, returnInfo=returnInfo):
            if article["uri"] in uniqueUris:
                print("again seeing " + article["uri"])
            uniqueUris.add(article["uri"])
        self.assertTrue(total == len(uniqueUris))


    def testGetAllArticlesCount2(self):
        returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(body = 0))
        twitterUri = self.er.getConceptUri("twitter")
        self.assertTrue(twitterUri != None)
        iter = QueryArticlesIter(conceptUri=twitterUri, lang="eng", dataType=["news", "blog"])

        total = iter.count(self.er)
        uniqueUris = set()
        for article in iter.execQuery(self.er, returnInfo=returnInfo, sortBy="date"):
            if article["uri"] in uniqueUris:
                print("again seeing " + article["uri"])
            uniqueUris.add(article["uri"])
        self.assertTrue(total == len(uniqueUris))

        total = iter.count(self.er)
        uniqueUris = set()
        for article in iter.execQuery(self.er, returnInfo=returnInfo, sortBy="rel"):
            if article["uri"] in uniqueUris:
                print("again seeing " + article["uri"])
            uniqueUris.add(article["uri"])
        self.assertTrue(total == len(uniqueUris))





if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticles)
    # suite = unittest.TestSuite()
    # suite.addTest(TestQueryArticles("testQuery2"))
    unittest.TextTestRunner(verbosity=3).run(suite)
